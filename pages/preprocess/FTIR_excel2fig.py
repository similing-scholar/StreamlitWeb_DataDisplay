"""将同一文件夹内的所有电学测试数据（除电阻）的Excel文件进行画图"""
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt


def single_curve(file_path):
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
    X = df['Wavenumbers[cm-1]']
    Intensity = df['Transmittance']
    if 'Corrected Transmittance' in df.columns:
        corrected_transmittance = df['Corrected Transmittance']

    # 提前设置图形属性，避免重复
    plt.rcParams['font.sans-serif'] = ['simhei']
    plt.rcParams['axes.unicode_minus'] = False
    # 画图
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(X, Intensity, label=curve_label, color='tab:blue')
    ax1.set_xlabel('Wavenumbers[cm-1]')
    ax1.set_ylabel('Intensity', color='tab:blue')
    ax1.tick_params(axis='y')

    if 'Corrected Transmittance' in df.columns:
        ax2 = ax1.twinx()
        ax2.plot(X, corrected_transmittance, label='Corrected Transmittance', color='tab:red')
        ax2.set_ylabel('Corrected Transmittance', color='tab:red')
        ax2.tick_params(axis='y')

    # 反转x轴
    plt.gca().invert_xaxis()

    fig.tight_layout()
    # 获取所有轴上的线和标签
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')  # 合并图例
    plt.savefig(save_path, dpi=300)
    plt.close()
    st.success(f'FTIR_plot PNG saved to {save_path}')

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
        file_path = st.text_input("输入excel的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\FTIR.xlsx**")

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有excel文件的路径
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in files if
                         file.endswith('.xlsx')]
            # 处理每个excel文件
            for file_path in excel_files:
                single_curve(file_path)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if file.endswith('.xlsx')]
            for file_path in excel_files:
                single_curve(file_path)
        elif mode == '模式三：处理单个excel':
            single_curve(file_path)
    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——FTIR.excel数据画图")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
