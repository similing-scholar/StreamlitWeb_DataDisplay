"""将同一文件夹内的所有UV的Excel文件进行合并，并画图"""
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def merge_excel(folder_path, spectrum):
    # 获取文件夹内所有 Excel 文件的路径
    excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' not in f) and (spectrum in f)]
    # 创建一个空 DataFrame 用于存储合并后的数据
    merged_df = pd.DataFrame()
    # 创建一个空 DataFrame 用于存储归一化的数据
    normalized_df = pd.DataFrame()

    # 遍历所有 Excel 文件
    for excel_file in excel_files:
        file_path = os.path.join(folder_path, excel_file)

        # 读取 Excel 文件，获取sheet_name，并转化为dataframe
        workbook = pd.ExcelFile(file_path)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取file_name，即曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]
        # 将透过率列名重命名为file_name
        df.rename(columns={df.columns[1]: curve_label}, inplace=True)
        # 将归一化数据列名重命名为 "Normalized " + file_name
        normalized_column_name = 'Normalized_' + curve_label
        df.rename(columns={'Normalized': normalized_column_name}, inplace=True)

        # # 如果第一次读取，直接作为基础 DataFrame
        # if merged_df.empty:
        #     merged_df = df
        # else:
        #     # 合并 Excel 文件，共享第一列 'Wavelengths'
        #     merged_df = pd.merge(merged_df, df, on='Wavelength[nm]', how='outer')
        # 如果第一次读取，直接作为基础 DataFrame
        if merged_df.empty:
            merged_df = df[[df.columns[0], curve_label]]  # 只选取波长和当前文件的数据列
            normalized_merged_df = df[[df.columns[0], normalized_column_name]]  # 只选取波长和当前文件的归一化数据列
        else:
            # 合并主数据，共享第一列 'Wavelengths'
            merged_df = pd.merge(merged_df, df[[df.columns[0], curve_label]], on='Wavelength[nm]', how='outer')
            # 合并归一化数据
            normalized_merged_df = pd.merge(normalized_merged_df, df[[df.columns[0], normalized_column_name]],
                                            on='Wavelength[nm]', how='outer')

    # 将合并后的 DataFrame 写入新 Excel 文件
    output_name = os.path.basename(folder_path)
    output_path = os.path.join(folder_path, f'{spectrum}_merged_{output_name}.xlsx')
    # merged_df.to_excel(output_path, index=False, engine='openpyxl', sheet_name=spectrum)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        merged_df.to_excel(writer, index=False, sheet_name=spectrum)
        normalized_merged_df.to_excel(writer, index=False, sheet_name='Normalized Data')

    return st.success(f"Merged excel file saved to {output_path}")


def merged_curve(folder_path, spectrum, x_scale, y_scale):
    """所有曲线画在一个图中"""
    merged_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' in f) and (spectrum in f)]
    for merged_file_name in merged_files:
        merged_file_path = os.path.join(folder_path, merged_file_name)
        # 读取excel文件数据
        df_merged = pd.read_excel(merged_file_path, engine='openpyxl', sheet_name=spectrum)
        # 获取列名，即光谱曲线的标签
        curve_labels = df_merged.columns[1:]

        # 提前设置图形属性，避免重复
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False

        # 遍历每个光谱曲线并绘总图
        plt.figure()
        plt.xlim(x_scale[0], x_scale[1])
        plt.ylim(y_scale[0], y_scale[1])
        plt.xlabel("Wavelength[nm]")
        plt.ylabel(spectrum)
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
            # 获取对应光谱曲线的数据
            wavelength = df_merged.iloc[:, 0]  # 提取第一列数据作为波长数据
            intensity = df_merged[curve_label]
            # 绘制光谱曲线
            plt.plot(wavelength, intensity, label=curve_label, color=colors[i])

        plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0))  # 调整legend的位置到右侧
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, merged_file_path.replace('.xlsx', '.png')), dpi=300)
        plt.close()
        st.success(f"Merged {merged_file_name} PNG saved to {folder_path}")

    return None


def merged_normalized_curve(folder_path, spectrum, x_scale, y_scale):
    """所有曲线画在一个图中"""
    merged_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' in f) and (spectrum in f)]
    for merged_file_name in merged_files:
        merged_file_path = os.path.join(folder_path, merged_file_name)
        # 读取excel文件数据
        df_merged = pd.read_excel(merged_file_path, engine='openpyxl', sheet_name='Normalized Data')
        # 获取列名，即光谱曲线的标签
        curve_labels = df_merged.columns[1:]

        # 提前设置图形属性，避免重复
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False

        # 遍历每个光谱曲线并绘总图
        plt.figure()
        plt.xlim(x_scale[0], x_scale[1])
        plt.ylim(y_scale[0], y_scale[1])
        plt.xlabel("Wavelength[nm]")
        plt.ylabel(spectrum)
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
            # 获取对应光谱曲线的数据
            wavelength = df_merged.iloc[:, 0]  # 提取第一列数据作为波长数据
            intensity = df_merged[curve_label]
            # 绘制光谱曲线
            plt.plot(wavelength, intensity, label=curve_label, color=colors[i])

        plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0))  # 调整legend的位置到右侧
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, merged_file_path.replace('.xlsx', '.png').replace(spectrum, 'Normalized_'+spectrum)), dpi=300)
        plt.close()
        st.success(f"Merged Normalized_{merged_file_name} PNG saved to {folder_path}")

    return None


def single_curve(folder_path, spectrum, x_scale, y_scale):
    """单个数据画单个图"""
    single_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' not in f) and (spectrum in f)]
    for single_file_name in single_files:
        single_file_path = os.path.join(folder_path, single_file_name)
        # 读取excel文件数据
        workbook = pd.ExcelFile(single_file_path)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取file_name，即曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]

        # 提前设置图形属性，避免重复
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False

        # 遍历每个光谱曲线并绘总图
        plt.figure()
        plt.xlim(x_scale[0], x_scale[1])
        plt.ylim(y_scale[0], y_scale[1])
        plt.xlabel("Wavelength[nm]")
        plt.ylabel(spectrum)

        # 获取对应光谱曲线的数据
        wavelength = df.iloc[:, 0]
        intensity = df.iloc[:, 1]
        # 绘制光谱曲线
        plt.plot(wavelength, intensity, label=curve_label)

        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, single_file_name.replace('.xlsx', '.png')), dpi=300)
        plt.close()
        st.success(f"Single {single_file_name } PNG saved to {folder_path}")

    return None


def single_normalized_curve(folder_path, spectrum, x_scale, y_scale):
    """单个数据画单个图"""
    single_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' not in f) and (spectrum in f)]
    for single_file_name in single_files:
        single_file_path = os.path.join(folder_path, single_file_name)
        # 读取excel文件数据
        workbook = pd.ExcelFile(single_file_path)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取file_name，即曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]

        # 提前设置图形属性，避免重复
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False

        # 遍历每个光谱曲线并绘总图
        plt.figure()
        plt.xlim(x_scale[0], x_scale[1])
        plt.ylim(y_scale[0], y_scale[1])
        plt.xlabel("Wavelength[nm]")
        plt.ylabel(spectrum)

        # 获取对应光谱曲线的数据
        wavelength = df.iloc[:, 0]
        intensity = df.iloc[:, 2]  # 归一化数据列
        # 绘制光谱曲线
        plt.plot(wavelength, intensity, label='Normalized_'+curve_label)

        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, single_file_name.replace('.xlsx', '.png').replace(spectrum, 'Normalized_'+spectrum)), dpi=300)
        plt.close()
        st.success(f"Single Normalized_{single_file_name} PNG saved to {folder_path}")

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    st.subheader('文件合并')
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：合并所有子文件夹内的所有excel', '模式二：合并单个文件夹下的所有excel'],
                    index=1)
    if mode == '模式一：合并所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input("输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：合并单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")

    # ---spectrum选择---
    spectrum = st.selectbox('当前excel数据是哪种光谱？', ('Transmittance', 'Absorbance'), index=0)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：合并所有子文件夹内的所有excel':
            # 获取所有子文件夹的路径
            subfolders = [os.path.join(excel_farther_folder, subfolder) for subfolder in os.listdir(excel_farther_folder)]
            for subfolder in subfolders:
                merge_excel(subfolder, spectrum)
        elif mode == '模式二：合并单个文件夹下的所有excel':
            merge_excel(excel_folder, spectrum)

    st.subheader('画图程序（可以独立使用，共用上面的选择项与路径输入项）')
    # ---绘制merged选择---
    single_fig = st.checkbox('是否绘制single_excel（一个excel文件中只有一个光谱数据）', value=True)
    merged_fig = st.checkbox('是否绘制merged_excel（一个excel文件中有多个光谱数据）', value=True)
    if merged_fig:
        st.warning('确保文件夹内已经通过运行**文件转换程序**顺利生成**merged_excel**')

    # ---画图x轴范围选择---
    col1, col2 = st.columns(2)
    x_min = col1.number_input('输入**x轴**(光谱波长)**最小值**', value=300)
    x_max = col2.number_input('输入**x轴**(光谱波长)**最大值**', value=1100)
    x_scale = (x_min, x_max)
    # ---画图纵轴范围选择---
    col3, col4 = st.columns(2)
    y_min = col3.number_input('输入**y轴**(透过率/吸光度)**最小值**', value=-0.1)
    y_max = col4.number_input('输入**y轴**(透过率/吸光度)**最大值**', value=1.2)
    y_scale = (y_min, y_max)

    # ---绘图---
    if st.button('将excel数据绘制成光谱图'):
        if mode == '模式一：合并所有子文件夹内的所有excel':
            # 获取所有子文件夹的路径
            subfolders = [os.path.join(excel_farther_folder, subfolder) for subfolder in os.listdir(excel_farther_folder)]
            for subfolder in subfolders:
                if single_fig:
                    single_curve(subfolder, spectrum, x_scale, y_scale)
                    single_normalized_curve(subfolder, spectrum, x_scale, y_scale)
                if merged_fig:
                    merged_curve(subfolder, spectrum, x_scale, y_scale)
                    merged_normalized_curve(subfolder, spectrum, x_scale, y_scale)
        elif mode == '模式二：合并单个文件夹下的所有excel':
            if single_fig:
                single_curve(excel_folder, spectrum, x_scale, y_scale)
                single_normalized_curve(excel_folder, spectrum, x_scale, y_scale)
            if merged_fig:
                merged_curve(excel_folder, spectrum, x_scale, y_scale)
                merged_normalized_curve(excel_folder, spectrum, x_scale, y_scale)

    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——uv.excel文件合并与画图")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
