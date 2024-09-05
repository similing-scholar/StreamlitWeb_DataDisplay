import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.io as pio


def excel2png(file_path, x_scale, y_scale, use_legend):
    """绘制2维图"""
    # 读取excel文件数据
    workbook = pd.ExcelFile(file_path)
    spectrum_data_sheet = workbook.sheet_names[0]
    df = workbook.parse(spectrum_data_sheet)
    # 获取文件名
    parameter_df = workbook.parse('parameter')
    file_name = parameter_df['File Name'][0]
    # 获取列名，即光谱曲线的标签
    curve_labels = df.columns[1:]

    # 提前设置图形属性，避免重复
    plt.rcParams['font.sans-serif'] = ['simhei']
    plt.rcParams['axes.unicode_minus'] = False

    # 遍历每个光谱曲线并绘总图
    plt.figure()
    plt.grid(True)  # 辅助网格样式
    plt.title(f'{file_name}')
    plt.xlim(x_scale[0], x_scale[1])
    plt.ylim(y_scale[0], y_scale[1])
    plt.xlabel('Wavelength[nm]')
    plt.ylabel(spectrum_data_sheet)
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

    # 是否使用图例
    if use_legend:
        plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0))  # 调整legend的位置到右侧
    plt.tight_layout()
    plt.savefig(file_path.replace('.xlsx', '.png'), dpi=300)
    plt.close()
    st.success(f"PNG of {file_path} is saved.")

    return None


def excel2gif(file_path, series_type, x_scale, y_scale):
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
    ax.set_xlim(x_scale[0], x_scale[1])
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


def excel2waterfall(file_path, x_scale, y_scale):
    """使用 Plotly 绘制3D瀑布图"""
    # 读取excel文件数据
    workbook = pd.ExcelFile(file_path)
    spectrum_data_sheet = workbook.sheet_names[0]
    df = workbook.parse(spectrum_data_sheet)
    # 获取文件名
    parameter_df = workbook.parse('parameter')
    file_name = parameter_df['File Name'][0]
    # 获取列名，即光谱曲线的标签
    curve_labels = df.columns[1:]

    fig = go.Figure()

    for i, curve_label in enumerate(curve_labels):
        fig.add_trace(go.Scatter3d(
            x=df.iloc[:, 0],
            y=[i] * len(df),
            z=df[curve_label],
            mode='lines',
            name=curve_label,
            line=dict(color=f'rgba({i * 30 % 255}, {(i * 60) % 255}, {(i * 90) % 255}, 1)')
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Wavelength[nm]',
            yaxis_title='Curve Index',
            zaxis_title=spectrum_data_sheet,
            xaxis=dict(range=x_scale),
            yaxis=dict(range=[0, len(curve_labels) - 1]),
            zaxis=dict(range=y_scale)
        ),
        title=f"{file_name}",
        margin=dict(r=20, b=10, l=10, t=10)
    )

    output_file = file_path.replace('.xlsx', '_3D.png')
    pio.write_image(fig, output_file)
    st.success(f"3D Waterfall plot is saved as {output_file}")

    return None


def excel_split(file_path):
    xls = pd.ExcelFile(file_path)
    spectrum_model = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=spectrum_model)
    # 获取第一列数据 (Wavelength[nm])
    wavelength_column = df.iloc[:, 0]

    # 遍历每个列，创建单独的Excel文件
    for i in range(1, df.shape[1]):  # 从第2列开始遍历 (跳过第1列)
        # 创建一个新DataFrame，包含第一列和当前时间点列
        new_df = pd.DataFrame({
            'Wavelength[nm]': wavelength_column,
            spectrum_model: df.iloc[:, i]
        })

        # 保存到新的Excel文件
        file_name = df.columns[i]
        file_dir = os.path.dirname(file_path)
        excel_output_path = os.path.join(file_dir, f'{spectrum_model}_{file_name}.xlsx')

        with pd.ExcelWriter(excel_output_path) as writer:
            # 将 new_df保存到名为 scan_mode 的 sheet 中
            new_df.to_excel(writer, sheet_name=spectrum_model, index=False)
            # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
            parameters = pd.DataFrame({'File Name': [file_name]})
            parameters.to_excel(writer, sheet_name='parameter', index=False)
        st.success(f"Splited excel file saved to {excel_output_path}")

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    st.subheader('画图程序')
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel',
                                     '模式三：处理单个excel'], index=1)
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

    # ---画图纵轴范围选择---
    col1, col2, col3, col4 = st.columns(4)
    y_min = col1.number_input('输入**纵轴**(透过率/吸光度)**最小值**', value=-0.1)
    y_max = col2.number_input('输入**纵轴**(透过率/吸光度)**最大值**', value=1.2)
    x_min = col1.number_input('输入**x轴**(透过率/吸光度)**最小值**', value=300)
    x_max = col2.number_input('输入**x轴**(透过率/吸光度)**最大值**', value=1100)
    x_scale = (x_min, x_max)
    y_scale = (y_min, y_max)

    # ---绘图类型选择---
    cola, colb, colc = st.columns(3)
    plot_2d = cola.checkbox('2D光谱图', value=True)
    if plot_2d:
        use_legend = cola.checkbox('2D图中使用图例', value=False)
    plot_gif = colb.checkbox('动图', value=True)
    if plot_gif:
        series_type = colb.text_input('输入序列的类型，例如：time', value='time')
    plot_3d = colc.checkbox('3D瀑布图', value=True)

    # ---按mode执行---
    if st.button('将excel数据绘制成光谱图'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in
                           files if file.endswith('.xlsx') and
                           any(keyword in file for keyword in ['Transmittance', 'Absorbance', 'Fluorescence'])]
            for file_path in excel_files:
                if plot_gif:
                    excel2gif(file_path, series_type, x_scale, y_scale)
                if plot_2d:
                    excel2png(file_path, x_scale, y_scale, use_legend)
                if plot_3d:
                    excel2waterfall(file_path, x_scale, y_scale)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if
                           file.endswith('.xlsx') and
                           any(keyword in file for keyword in ['Transmittance', 'Absorbance', 'Fluorescence'])]
            for file_path in excel_files:
                if plot_gif:
                    excel2gif(file_path, series_type, x_scale, y_scale)
                if plot_2d:
                    excel2png(file_path, x_scale, y_scale, use_legend)
                if plot_3d:
                    excel2waterfall(file_path, x_scale, y_scale)
        elif mode == '模式三：处理单个excel':
            if plot_gif:
                excel2gif(excel_path, series_type, x_scale, y_scale)
            if plot_2d:
                excel2png(excel_path, x_scale, y_scale, use_legend)
            if plot_3d:
                excel2waterfall(excel_path, x_scale, y_scale)

    st.subheader('文件拆分程序（可以独立使用，共用上面的选择项与路径输入项，仅支持model2）')
    if st.button('拆分excel文件'):
        excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if
                       file.endswith('.xlsx') and
                       any(keyword in file for keyword in
                           ['Transmittance_merged', 'Absorbance_merged', 'Fluorescence_merged'])]
        for file_path in excel_files:
            excel_split(file_path)

    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——avantes.excel文件画图与拆分")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
