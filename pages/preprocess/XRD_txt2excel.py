"""将XRD的txt测试数据转换为Excel文件"""
import pandas as pd
import re
import streamlit as st
import os
from scipy.signal import savgol_filter


def kei_txt2excel(file_path, window_length, polyorder):
    """注意原始txt列数，起始行的处理"""
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            if re.match(r'^\d', line):  # 仅读取以数字开头的行
                data.append([float(x) for x in line.strip().split()])  # 以空格分割，转换为浮点数

    # 将数据转换为 DataFrame
    df = pd.DataFrame(data, columns=['2Θ[degree]', 'Intensity[a.u.]'])  # 根据实际情况调整列名

    # SG平滑处理
    smoothed_intensity = savgol_filter(df['Intensity[a.u.]'], window_length=window_length, polyorder=polyorder)
    df['Smoothed Intensity[a.u.]'] = smoothed_intensity

    # 将数据保存为Excel文件，包含处理后的第一行，指定工作表名称为文件名
    file_name = file_path.split('.txt')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.txt', f'{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, index=False, header=True, startrow=0, sheet_name='XRD_rawdata')  # 从第一行开始写入数据，包含标题行
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name],
                                   'SG Window Length': [window_length], 'SG Poly-order': [polyorder]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Excel file saved to {excel_output_path}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有txt', '模式二：处理单个文件夹下的所有txt', '模式三：处理单个txt'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有txt':
        txt_farther_folder = st.text_input("输入txt所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有txt':
        txt_folder = st.text_input("输入txt所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个txt':
        txt_path = st.text_input("输入txt的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\kei.txt**")

    # ---SG参数---
    smooth_check = st.checkbox('是否进行SG平滑处理？', value=True)
    if smooth_check:
        col1, col2 = st.columns([0.5, 0.5])
        window_length = col1.number_input('输入SG窗口长度', value=11)
        polyorder = col2.number_input('输入SG多项式阶数', value=2)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有txt':
            # 获取所有txt文件的路径
            txt_files = [os.path.join(root, file) for root, _, files in os.walk(txt_farther_folder) for file in files if
                         file.endswith('.txt')]
            # 处理每个txt文件
            for file_path in txt_files:
                kei_txt2excel(file_path, window_length, polyorder)
        elif mode == '模式二：处理单个文件夹下的所有txt':
            txt_files = [os.path.join(txt_folder, file) for file in os.listdir(txt_folder) if file.endswith('.txt')]
            for file_path in txt_files:
                kei_txt2excel(file_path, window_length, polyorder)
        elif mode == '模式三：处理单个txt':
            kei_txt2excel(txt_path, window_length, polyorder)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——XRD.txt文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
