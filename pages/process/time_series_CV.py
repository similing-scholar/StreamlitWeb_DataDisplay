"""时间序列的CV数据，可视化分析与画图"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import os


@st.cache_data(experimental_allow_widgets=True)
def load_data():
    uploaded_file = st.file_uploader("上传时间序列的循环扫描数据Excel文件，通常为[**CV_yyyymmdd-.xlsx**]文件",
                                     type=["xlsx", "xls"])
    if uploaded_file is not None:
        # 读取 Excel 文件，获取sheet_name，并转化为dataframe
        workbook = pd.ExcelFile(uploaded_file)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取curve_name
        parameter_df = workbook.parse('parameter')
        curve_name = parameter_df['File Name'][0]
        # 获取file_name
        file_name = uploaded_file.name
        return df, curve_name, file_name
    else:
        return None, None, None


def cv_plot(df, curve_name, file_name):
    # 读取数据
    Potential = df['Potential[V]']
    Current = df['Current[A]']
    st.warning('如果存在Time[s]列，则使用该列作为时间轴；否则需要输入采样时间间隔；默认为0时使用采样次数作为时间轴')
    if 'Time[s]' in df.columns:
        time_axis = df['Time[s]']
        time_axis_label = 'Time[s]'
    else:
        # 填写采样时间间隔
        sampling_interval = st.number_input('填写采样时间间隔[s]')  # 【可修改】
        # np创建一个df行数的列表，作为时间轴
        time_axis = np.arange(df.shape[0]) * sampling_interval
        time_axis_label = 'Time[s]'
        # 如果没有输入采样时间间隔，使用index作为时间轴
        if sampling_interval == 0:
            time_axis = df.index
            time_axis_label = 'sampling index'

    col1, col2 = st.columns([30, 70])
    with col1:
        # 填写子图的横纵坐标
        ax1_xlabel = st.text_input('第一个子图的xlabel', value='Potential[V]')  # 【可修改】
        ax1_ylabel = st.text_input('第一个子图的ylabel', value='Current[A]')  # 【可修改】
        ax2_xlabel = st.text_input('第二个子图的xlabel', value=time_axis_label)  # 【可修改】
        ax2_ylabel = st.text_input('第二个子图的ylabel', value='Potential[V]')  # 【可修改】
        ax3_xlabel = st.text_input('第三个子图的xlabel', value=time_axis_label)  # 【可修改】
        ax3_ylabel = st.text_input('第三个子图的ylabel', value='Current[A]')  # 【可修改】

    with col2:
        # 使用plt渲染图片，提前设置图形属性
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(8, 10))
        gs = fig.add_gridspec(3, 1, height_ratios=[4, 2, 2])  # 根据需要调整每行子图的高度比例

        # CV图
        ax1 = fig.add_subplot(gs[0])
        ax1.grid(True)  # 辅助网格样式
        # 使用科学计数法表示纵轴坐标
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        ax1.plot(Potential, Current, label=curve_name)
        ax1.set_title('cyclic curve')
        ax1.set_xlabel(ax1_xlabel)
        ax1.set_ylabel(ax1_ylabel)
        ax1.legend()

        # Vt图
        ax2 = fig.add_subplot(gs[1])
        ax2.grid(True)
        ax2.plot(time_axis, Potential, label=curve_name)
        ax2.set_xlabel(ax2_xlabel)
        ax2.set_ylabel(ax2_ylabel)
        ax2.legend()

        # It图
        ax3 = fig.add_subplot(gs[2])
        ax3.grid(True)
        # 使用科学计数法表示纵轴坐标
        ax3.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        ax3.plot(time_axis, Current, label=curve_name)
        ax3.set_xlabel(ax3_xlabel)
        ax3.set_ylabel(ax3_ylabel)
        ax3.legend()
        # 显示图形
        st.pyplot(fig)

        # 选择保存文件夹
        save_folder = st.text_input("输入保存文件夹的**绝对路径**，如C:\\User\\JiaPeng\\Desktop\\test")  # 【可修改】
        save_name = st.text_input("输入保存的名字，例如xxx.png", value=file_name.replace('.xlsx', '[process].png'))  # 【可修改】
        # 保存图形按钮
        if st.button("保存为png格式"):
            if save_folder == '':
                st.warning("请先输入保存文件夹的绝对路径")
            else:
                fig.savefig(os.path.join(save_folder, save_name), dpi=300)
                st.success(f"图像保存在{save_folder}文件夹下")


def st_main():
    st.title(":recycle:数据处理——时间序列的电学数据分析")  # ♻️
    # 1.0 -----读入DataFrame-----
    df, curve_name, file_name = load_data()

    if df is not None:
        # 2.0 -----绘制某个时间点的器件光谱曲线-----
        st.subheader(":clock1:绘制器件的循环伏安曲线")  # 🕐
        cv_plot(df, curve_name, file_name)

    return None


if __name__ == "__main__":
    st_main()