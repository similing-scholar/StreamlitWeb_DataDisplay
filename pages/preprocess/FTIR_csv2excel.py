import pandas as pd
import streamlit as st
import os
import numpy as np


def FTIR_csv2excel(file_path, base_csv_path=None):
    """将FTIR的csv测试数据转换为Excel文件"""
    # 读取csv文件内容
    df = pd.read_csv(file_path, delimiter=',', header=None)
    scan_mode = 'Transmittance'
    columns = ['Wavenumbers[cm-1]', scan_mode]
    df = df.astype(float)
    df.columns = columns

    # 读取基础数据
    if base_csv_path:
        base_df = pd.read_csv(base_csv_path, delimiter=',', header=None)
        base_df = base_df.astype(float)
        # 将原始数据除以基础数据并添加到 DataFrame 的第三列
        df['Corrected Transmittance'] = df[scan_mode] / base_df.iloc[:, 1]

    # 将 DataFrame 保存为 Excel 文件
    file_name = file_path.split('.csv')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.csv', f'FTIR_{scan_mode}_{file_name}.xlsx')
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
    elif mode == '模式二：处理单个文件夹下的所有csv':
        csv_folder = st.text_input("输入csv所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个csv':
        csv_path = st.text_input("输入csv的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\FTIR.csv**")

    # ---基底的IR数据添加---
    base_check = st.checkbox('如果需要将基底当作背景扣除，请选择此项', value=True)
    if base_check:
        base_csv_path = st.text_input("输入基底csv的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\FTIR_base.csv**")

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有csv':
            csv_files = [os.path.join(root, file.lower()) for root, _, files in os.walk(csv_farther_folder) for file in files if
                         file.lower().endswith('.csv')]
            for file_path in csv_files:
                FTIR_csv2excel(file_path, base_csv_path)
        elif mode == '模式二：处理单个文件夹下的所有csv':
            csv_files = [os.path.join(csv_folder, file.lower()) for file in os.listdir(csv_folder) if
                         file.lower().endswith('.csv')]  # 避免大小写问题
            for csv_file in csv_files:
                FTIR_csv2excel(csv_file, base_csv_path)
        elif mode == '模式三：处理单个csv':
            FTIR_csv2excel(csv_path, base_csv_path)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——FTIR.csv文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
