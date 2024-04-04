import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.colors import ListedColormap


def excel2png(file_path, y_scale):
    """绘制2维图"""
    # 读取excel文件数据
    workbook = pd.ExcelFile(file_path)
    spectrum_data_sheet = workbook.sheet_names[0]
    df = workbook.parse(spectrum_data_sheet)
    # 获取列名，即光谱曲线的标签
    curve_labels = df.columns[1:]

    # 提前设置图形属性，避免重复
    plt.rcParams['font.sans-serif'] = ['simhei']
    plt.rcParams['axes.unicode_minus'] = False

    # 遍历每个光谱曲线并绘总图
    plt.figure()
    plt.grid(True)  # 辅助网格样式
    plt.ylim(y_scale[0], y_scale[1])
    plt.ylabel(spectrum_data_sheet)
    plt.xlabel('Wavelength[nm]')
    # 使用科学计数法表示纵轴坐标
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    # 自定义颜色映射的颜色列表
    custom_colors = ['#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3',
                     '#03A9F4', '#00BCD4', '#009688', '#4CAF50', '#8BC34A', '#CDDC39',
                     '#FFEB3B', '#FFC107', '#FF9800', '#FF5722', '#795548', '#9E9E9E', '#607D8B']
    # 创建自定义的颜色映射
    custom_cmap = ListedColormap(custom_colors)
    # 使用自定义颜色映射分配颜色给曲线
    colors = custom_cmap(np.linspace(0, 1, len(curve_labels)))

    # 循环内只进行绘图设置提高效率
    for i, curve_label in enumerate(curve_labels):
        # 获取对应IV曲线的数据
        wavelength = df.iloc[:, 0]  # 提取第一列数据作为波长数据
        intensity = df[curve_label]
        plt.plot(wavelength, intensity, label=curve_label, color=colors[i])

    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0))  # 调整legend的位置到右侧
    plt.tight_layout()
    plt.savefig(file_path.replace('.xlsx', '.png'), dpi=300)
    plt.close()
    st.success(f"PNG of {file_path} is saved.")

    return None


def excel2gif(file_path, series_type, y_scale):
    """绘制动图"""
    # 读取excel文件数据
    workbook = pd.ExcelFile(file_path)
    sheet_name = workbook.sheet_names[0]
    df = workbook.parse(sheet_name, index_col=0)
    # 获取文件名
    parameter_df = workbook.parse('parameter')
    file_name = parameter_df['File Name'][0]

    # 初始化图形
    fig, ax = plt.subplots()
    line, = ax.plot(df.index, df.iloc[:, 0], label=df.columns[0])  # 初始化第一个时间点

    # 添加标题和标签
    ax.set_title(f'{file_name} of {series_type} series')
    ax.set_xlabel(df.index.name)
    ax.set_ylabel(sheet_name)
    ax.set_ylim(y_scale[0], y_scale[1])
    ax.legend()

    # 更新函数，用于每个动画帧
    def update(frame):
        line.set_ydata(df.iloc[:, frame])
        line.set_label(df.columns[frame])
        legend = ax.legend()
        return line, legend

    # 创建动画
    animation = FuncAnimation(fig, update, frames=df.shape[1], interval=50)
    # 保存为 GIF
    animation.save(file_path.replace('xlsx', 'gif'), writer='pillow', fps=30)

    return st.success(f'GIF of {file_path} is saved.')


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    st.subheader('画图程序')
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel',
                                     '模式三：处理单个excel'], index=2)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input(
            "输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
        st.warning('需要保证该目录下所有子文件夹内的excel处理的光谱类型相同，即全为吸收or透过or荧光')
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
        st.warning('需要保证该文件夹内的excel处理的光谱类型相同，即全为吸收or透过or荧光')
    elif mode == '模式三：处理单个excel':
        excel_path = st.text_input("输入excel的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\ava.xlsx**",
                                   value='.xlsx')

    # ---序列选择---
    series_check = st.checkbox('是否是序列数据（序列数据将绘制**动图**）', value=True)
    if series_check:
        series_type = st.text_input('输入序列的类型，例如：time', value='time')

    # ---画图纵轴范围选择---
    col1, col2 = st.columns(2)
    y_min = col1.number_input('输入**纵轴**(透过率/吸光度)**最小值**', value=-0.1)
    y_max = col2.number_input('输入**纵轴**(透过率/吸光度)**最大值**', value=1.2)
    y_scale = (y_min, y_max)

    # ---按mode执行---
    if st.button('将excel数据绘制成光谱图'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in
                           files if file.endswith('.xlsx') and
                           any(keyword in file for keyword in ['Transmittance', 'Absorbance', 'Fluorescence'])]
            for file_path in excel_files:
                if series_check:
                    excel2gif(file_path, series_type, y_scale)
                else:
                    excel2png(file_path, y_scale)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if
                           file.endswith('.xlsx') and
                           any(keyword in file for keyword in ['Transmittance', 'Absorbance', 'Fluorescence'])]
            for file_path in excel_files:
                if series_check:
                    excel2gif(file_path, series_type, y_scale)
                else:
                    excel2png(file_path, y_scale)
        elif mode == '模式三：处理单个excel':
            if series_check:
                excel2gif(excel_path, series_type, y_scale)
            else:
                excel2png(excel_path, y_scale)

    st.subheader('文件拆分程序（可以独立使用，共用上面的选择项与路径输入项）')

    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——avantes.excel文件画图与拆分")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
