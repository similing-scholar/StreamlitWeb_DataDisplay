"""将同一文件夹内的所有电学测试数据（除电阻）的Excel文件进行画图"""
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt


def single_curve(file_path, x_bar):
    """一个数据一个图"""
    # 读取excel文件数据
    workbook = pd.ExcelFile(file_path)
    sheet_name = workbook.sheet_names[0]
    df = workbook.parse(sheet_name)
    # 获取file_name
    parameter_df = workbook.parse('parameter')
    curve_label = parameter_df['File Name'][0]
    # 图片保存路径
    save_path = file_path.replace('.xlsx', '.png')

    # 提取数据
    X = df['2Θ[degree]']
    Intensity = df['Intensity[a.u.]']
    Smoothed_Intensity = df['Smoothed Intensity[a.u.]']

    # 提前设置图形属性，避免重复
    plt.rcParams['font.sans-serif'] = ['simhei']
    plt.rcParams['axes.unicode_minus'] = False
    # 画图
    plt.figure(figsize=(12, 6))
    plt.plot(X, Intensity, label=curve_label)
    plt.plot(X, Smoothed_Intensity, label='Smoothed Intensity')

    plt.xlim(x_bar[0], x_bar[1])
    plt.xlabel('2Θ[degree]')
    plt.ylabel('Intensity[a.u.]')
    # 使用科学计数法表示纵轴坐标
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    st.success(f'XRD_plot PNG saved to {save_path}')

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel', '模式三：处理单个excel'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input(
            "输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个excel':
        file_path = st.text_input("输入excel的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\xrd.xlsx**")

    # ---横坐标范围参数选择---
    col1, col2 = st.columns(2)
    x_min = col1.number_input('横坐标2Θ[degree]最小值', value=5)
    x_max = col2.number_input('横坐标2Θ[degree]最大值', value=50)
    x_bar = [x_min, x_max]

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有excel文件的路径
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in files if
                         file.endswith('.xlsx')]
            # 处理每个excel文件
            for file_path in excel_files:
                single_curve(file_path, x_bar)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if file.endswith('.xlsx')]
            for file_path in excel_files:
                single_curve(file_path, x_bar)
        elif mode == '模式三：处理单个excel':
            single_curve(file_path, x_bar)
    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——XRD.excel数据画图")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
