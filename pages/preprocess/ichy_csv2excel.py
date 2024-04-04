import pandas as pd
import streamlit as st
import os
import numpy as np


def ichy_csv2excel(file_path):
    """将ichy的csv测试数据转换为Excel文件"""
    # 读取csv文件内容
    df = pd.read_csv(file_path, delimiter=',', header=None)

    # 通过测试模式判断数据起始行和其余的数据处理方式
    scan_mode = df.iloc[1, 1]

    if scan_mode == 'LSV - Linear Sweep Voltammetry':
        scan_mode = 'LSV'
        data_start_row = 9
        columns = ['Potential[V]', 'Current[A]']
        # 新的数据
        df = df.iloc[data_start_row:].reset_index(drop=True)
        df = df.astype(float)
        df.columns = columns

    if scan_mode == 'CV - Cyclic Voltammetry':
        scan_mode = 'CV'
        data_start_row = 11
        columns = ['Potential[V]', 'Current[A]']
        scan_rate = float(df.iloc[6, 1]) * 1e-6  # (uV/S) -> (V/S)
        time_interval = (float(df.iloc[12, 0]) - float(df.iloc[11, 0]))/scan_rate
        # 新的数据
        df = df.iloc[data_start_row:].reset_index(drop=True)
        df = df.astype(float)
        df.columns = columns
        # 新增 'time[s]' 列，数据为索引乘以time_interval
        df.insert(0, 'Time[s]', df.index * time_interval)

    if scan_mode == 'I-t - Amperometric i-t Curve':
        scan_mode = 'It'
        data_start_row = 9
        columns = ['Time[s]', 'Current[A]']
        potential = df.iloc[3, 1]
        # 新的数据
        df = df.iloc[data_start_row:].reset_index(drop=True)
        df = df.astype(float)
        df.columns = columns
        # 在 'Time[s]'后面插入常数列'Potential[V]'
        df.insert(1, 'Potential[V]', int(potential)*0.001)
        # 删除完全相同的行（仪器It模式数据采集问题？？？）
        df = df.drop_duplicates(subset=['Time[s]'])

    if scan_mode == 'CA - Chronoamperometry':
        scan_mode = 'CA'
        data_start_row = 11
        columns = ['Time[s]', 'Current[A]']
        High_E = int(df.iloc[4, 1]) * 1e-3
        Low_E = int(df.iloc[5, 1]) * 1e-3
        Pulse_Width = int(df.iloc[7, 1]) * 1e-3
        Sample_Int = int(df.iloc[9, 1]) * 1e-3
        # 新的数据
        df = df.iloc[data_start_row:].reset_index(drop=True)
        df = df.astype(float)
        df.columns = columns
        # 重新计算 'time[s]' 列，原数据时间戳有问题？？？
        df['Time[s]'] = (df.index + 1) * Sample_Int
        # 在 'Time[s]'后面插入'Potential[V]'
        pattern = np.repeat([High_E, Low_E], Pulse_Width / Sample_Int)  # 重复高低电压的基本模式
        repeated_pattern = np.tile(pattern, len(df) // len(pattern))  # 重复整个模式以匹配 DataFrame 的长度
        repeated_pattern = np.append(repeated_pattern, pattern[0:len(df) % len(pattern)])  # 添加不完整的部分
        df.insert(1, 'Potential[V]', repeated_pattern)

    # 将 DataFrame 保存为 Excel 文件
    file_name = file_path.split('.csv')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.csv', f'{scan_mode}_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path) as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, sheet_name=scan_mode, index=False)
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Excel file saved to {excel_output_path}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有csv', '模式二：处理单个文件夹下的所有csv', '模式三：处理单个csv'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有csv':
        csv_farther_folder = st.text_input(
            "输入csv所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
        st.warning('根据csv的测试信息自动处理，同一文件夹下可以存在不同测量方式的csv文件')
    elif mode == '模式二：处理单个文件夹下的所有csv':
        csv_folder = st.text_input("输入csv所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
        st.warning('根据csv的测试信息自动处理，同一文件夹下可以存在不同测量方式的csv文件')
    elif mode == '模式三：处理单个csv':
        csv_path = st.text_input("输入csv的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\ichy.csv**")

    # ---按mode执行---
    st.warning('除了LSV将输出Potential[V],Current[A]两列，It/CV/CA都输出Time[s],Potential[V],Current[A]三列')
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有csv':
            csv_files = [os.path.join(root, file) for root, _, files in os.walk(csv_farther_folder) for file in files if
                         file.endswith('.csv')]
            for file_path in csv_files:
                ichy_csv2excel(file_path)
        elif mode == '模式二：处理单个文件夹下的所有csv':
            csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]
            for file_path in csv_files:
                ichy_csv2excel(file_path)
        elif mode == '模式三：处理单个csv':
            ichy_csv2excel(csv_path)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——ichy.csv文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()