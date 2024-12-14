import pandas as pd
import streamlit as st
import os
from scipy.interpolate import interp1d
import numpy as np
import re

def transmittance_calculation(df):
    """计算透过率"""
    # 提取波长与背景、参考数据
    wavelength_column = df.iloc[:, 0]
    background = df.iloc[:, 1]
    reference = df.iloc[:, 2]

    # 扣除背景
    transmittance_df = df.iloc[:, 3:].sub(background, axis=0)  # 使用sub将每一列都减去新的列，0表示按行操作
    reference = reference - background
    # 计算透过率
    transmittance_df = transmittance_df.div(reference, axis=0)  # 使用div将每一列都除以新的列，0表示按行操作

    # 合并数据
    result_df = pd.concat([wavelength_column, transmittance_df], axis=1)
    return result_df

def transmittance_to_absorbance(transmittance_series):
    # 确保所有值都是正数，以避免取对数时出错
    # 将所有非正数值替换为一个非常小的正数
    transmittance_series = transmittance_series.apply(lambda x: x if x > 0 else 1e-10)
    # 计算吸光度
    absorbance_series = -np.log10(transmittance_series)
    return absorbance_series

def absorbance_calculation(df):
    """计算吸光度"""
    result_df = transmittance_calculation(df)
    # 使用apply函数时，确保传递整个列，这里使用lambda函数确保每一列都正确处理
    result_df.iloc[:, 1:] = result_df.iloc[:, 1:].apply(lambda x: transmittance_to_absorbance(x))
    return result_df

def fluorescence_calculation(df):
    """计算荧光强度"""
    # 提取波长与背景、参考数据
    wavelength_column = df.iloc[:, 0]
    background = df.iloc[:, 1]

    # 扣除背景
    fluorescence_df = df.iloc[:, 2:].sub(background, axis=0)  # 使用sub将每一列都减去新的列，0表示按行操作

    # 合并数据
    result_df = pd.concat([wavelength_column, fluorescence_df], axis=1)
    return result_df

def dataframe_interpolation(df, interpolation_parameters):
    """对dataframe进行插值"""
    # 配置插值参数
    start, end, interval, kind = interpolation_parameters
    x_column = df.columns[0]
    new_x = np.arange(start, end + interval, interval)
    # 创建插值后的dataframe，使用字典存储
    interpolated_data = {x_column: new_x}

    # 创建 interp1d 对象
    f_objects = {column: interp1d(df[x_column], df[column], kind=kind) for column in df.columns[1:]}
    # 使用 interp1d 对象进行插值
    for column, f in f_objects.items():
        interpolated_data[column] = f(new_x)

    # 合并所有列转为dataframe
    interpolated_df = pd.DataFrame(interpolated_data)
    return interpolated_df

def extract_time_interval(file_name):
    """从文件名中提取时间间隔"""
    match = re.search(r'scan(\d+\.?\d*)s', file_name)
    if match:
        return float(match.group(1))
    else:
        return None

def excel2excel(file_path, spectrum_select, interpolation_parameters, column_names):
    # 读取原始数据，并修改格式
    df = pd.read_excel(file_path)
    df = df.iloc[5:]  # 删除前五行无数据行
    df.reset_index(drop=True, inplace=True)  # 重设索引（原来的数据行为第零行）
    df.columns.values[:3] = ['Wavelength[nm]', 'dark', 'reference']  # 修改前三列的列标签
    df.columns = df.columns.str.replace(r'\.Raw8', '', regex=True, n=-1)  # 去除从第四列开始的'.RAW/Raw'
    df.columns = df.columns.str.replace(r'\.RAW8', '', regex=True, n=-1)  # 去除从第四列开始的'.RAW/Raw'

    # 自动提取时间间隔
    time_interval = extract_time_interval(os.path.basename(file_path))
    if time_interval and len(column_names) > 0:
        column_start, _, column_unit = column_names
        column_names = [f'{column_start + i * time_interval}{column_unit}' for i in range(df.shape[1] - 3)]
        df.columns.values[3:] = column_names
    elif len(column_names) > 0:
        column_start, column_interval, column_unit = column_names
        column_names = [f'{column_start + i * column_interval}{column_unit}' for i in range(df.shape[1] - 3)]
        df.columns.values[3:] = column_names

    df.astype('float64')  # 确保数据类型一致
    # 如果interpolation_parameters不为空，则插值
    if len(interpolation_parameters) > 0:
        df = dataframe_interpolation(df, interpolation_parameters)

    # 处理光谱类型
    if spectrum_select == 'Transmittance':
        df = transmittance_calculation(df)
    elif spectrum_select == 'Absorbance':
        df = absorbance_calculation(df)
    elif spectrum_select == 'Fluorescence':
        df = fluorescence_calculation(df)

    # 将 DataFrame 保存为 Excel 文件
    file_name = file_path.split('.xlsx')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.xlsx', f'{spectrum_select}_merged_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path) as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, sheet_name=spectrum_select, index=False)
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    st.success(f"Converted excel file saved to {excel_output_path}")
    return None

@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel', '模式三：处理单个excel'],
                    index=2)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input("输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
        st.warning('需要保证该目录下所有子文件夹内的excel处理的光谱类型相同，即全为吸收or透过or荧光')
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
        st.warning('需要保证该文件夹内的excel处理的光谱类型相同，即全为吸收or透过or荧光')
    elif mode == '模式三：处理单个excel':
        excel_path = st.text_input("输入excel的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\ava.xlsx**",
                                   value='.xlsx')

    # ---spectrum选择（字符串）---
    spectrum_select = st.selectbox('选择需要处理成哪种光谱？', ('Transmittance', 'Absorbance', 'fluorescence'))
    if spectrum_select in ['Transmittance', 'Absorbance']:
        st.warning('使用AvaSoft转换时，第二列为dark.RAW8（背景光），第三列为ref.RAW8（参比光），**第四列起为实测光谱数据**')
    elif spectrum_select == 'fluorescence':
        st.warning('使用AvaSoft转换时，第二列为dark.RAW8（背景光），**第三列起为实测光谱数据**')

    # ---插值（列表）---
    interpolation_check = st.checkbox('是否插值？（原始AvaSoft数据的波长不为整数，默认使用插值统一数据格式）', value=True)
    if interpolation_check:
        col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
        start = col1.number_input('插值起始波长[nm]', min_value=187.3, max_value=3500.1, value=300.0)
        end = col2.number_input('插值终止波长[nm]', min_value=start, max_value=3500.1,  value=1100.0)
        interval = col3.number_input('插值间隔[nm]', min_value=0.5, max_value=1000.0, value=1.0)
        kind = col4.selectbox('插值方法', ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next'], index=0)
        interpolation_parameters = [start, end, interval, kind]
    else:
        interpolation_parameters = []

    # ---时间序列需要修改列名（列表）---
    column_check = st.checkbox('是否修改**序列**列名？（使用自动采集数据功能得到的文件名由AvaSoft序列编码，可自定义修改）', value=True)
    st.warning('**CV同步采集的时间序列光谱**确保修改列名，其他光谱可不修改')
    if column_check:
        col1, col2, col3 = st.columns([0.33, 0.33, 0.33])
        column_start = col1.number_input('序列起始序号', value=0)
        column_interval = col2.number_input('即采样间隔（即采样间隔）,文件名中有‘scan0.5s’将自动匹配', value=0.5)
        column_unit = col3.text_input('单位（例如：s/min/mm）', value='s')
        column_names = [column_start, column_interval, column_unit]
    else:
        column_names = []

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in
                         files if
                         file.endswith('.xlsx')]
            for file_path in excel_files:
                excel2excel(file_path, spectrum_select, interpolation_parameters, column_names)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            sca_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if file.endswith('.xlsx')]
            for file_path in sca_files:
                excel2excel(file_path, spectrum_select, interpolation_parameters, column_names)

        elif mode == '模式三：处理单个excel':
            excel2excel(excel_path, spectrum_select, interpolation_parameters, column_names)

    return None

def st_main():
    st.title(":repeat_one: 数据预处理——avantes.raw/excel文件转excel文件")  # 🔂
    st.warning('先使用AvaSoft将.RAW8文件转换为excel表格')
    parameter_configuration()
    return None

if __name__ == '__main__':
    st_main()
