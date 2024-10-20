import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt


def normalize_min_max(series):
    """最大最小值归一化到0-1之间。"""
    min_value = series.min()
    max_value = series.max()
    return (series - min_value) / (max_value - min_value)


def normalize_max(series):
    """最大值归一化到0-1之间，使用最大值进行归一化。"""
    max_value = series.max()
    return series / max_value


def normalize_series(series, normalization_type):
    """根据归一化类型选择归一化方式。"""
    if normalization_type == '最大最小值归一化':
        return normalize_min_max(series)
    elif normalization_type == '最大值归一化':
        return normalize_max(series)


def normalize_individual_columns(df, normalization_type):
    """对DataFrame中从第二列开始的每一列依次归一化。"""
    for column in df.columns[1:]:
        df[column] = normalize_series(df[column], normalization_type)
    return df


def normalize_all_y_together(df, normalization_type):
    """对DataFrame中从第二列开始的所有列一起归一化。"""
    if normalization_type == '最大最小值归一化':
        all_y = df.iloc[:, 1:]
        global_min = all_y.min().min()  # 找到所有列的全局最小值
        global_max = all_y.max().max()  # 找到所有列的全局最大值
        for column in all_y.columns:
            df[column] = (df[column] - global_min) / (global_max - global_min)
    elif normalization_type == '最大值归一化':
        all_y = df.iloc[:, 1:]
        global_max = all_y.max().max()  # 找到所有列的全局最大值
        for column in all_y.columns:
            df[column] = df[column] / global_max
    return df


def excel_normalize(file_path, row_normalize_select, global_normalize_select, normalization_type):
    """归一化处理并保存为新文件。"""
    workbook = pd.ExcelFile(file_path)
    sheet_name = workbook.sheet_names[0]
    df = workbook.parse(sheet_name)
    x_col_name = df.columns[0]
    file_name = file_path.split('.xlsx')[0].split('\\')[-1]
    # new_file_name = 'Normalized_' + file_name
    # save_path = file_path.replace(file_name, new_file_name)
    # 根据归一化类型决定文件名后缀
    normalization_suffix = 'max' if normalization_type == '最大值归一化' else 'maxmin'

    df_individual_normalized = normalize_individual_columns(df.copy(), normalization_type)
    df_all_y_normalized = normalize_all_y_together(df.copy(), normalization_type)

    df_individual_normalized.columns = [x_col_name] + ['row_normalized_' + col for col in df_individual_normalized.columns[1:]]
    df_all_y_normalized.columns = [x_col_name] + ['global_normalized_' + col for col in df_all_y_normalized.columns[1:]]

    if row_normalize_select:
        save_path = file_path.replace(file_name, f'RowNormalized_{normalization_suffix}_' + file_name)
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            df_individual_normalized.to_excel(writer, sheet_name=sheet_name, index=False)
            parameters = pd.DataFrame({'File Name': [file_name]})
            parameters.to_excel(writer, sheet_name='parameter', index=False)
        st.success(f"normalized excel file saved to {save_path}")

    if global_normalize_select:
        save_path = file_path.replace(file_name, f'GlobalNormalized_{normalization_suffix}_' + file_name)
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            df_all_y_normalized.to_excel(writer, sheet_name=sheet_name, index=False)
            parameters = pd.DataFrame({'File Name': [file_name]})
            parameters.to_excel(writer, sheet_name='parameter', index=False)
        st.success(f"normalized excel file saved to {save_path}")

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel', '模式三：处理单个excel'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input(
            "输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个excel':
        file_path = st.text_input("输入excel的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\normalize.xlsx**")

    col1, col2 = st.columns(2)
    # 归一化选择
    row_normalize_select = col1.checkbox('是否进行列归一化（每一y列各自归一化）', value=True)
    global_normalize_select = col1.checkbox('是否进行全局归一化（所有y列一起归一化）', value=False)

    # 归一化类型选择
    normalization_type = col2.selectbox('选择归一化类型', ['最大最小值归一化', '最大值归一化'])

    # 按mode执行
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in files if
                         file.endswith('.xlsx')]
            for file_path in excel_files:
                excel_normalize(file_path, row_normalize_select, global_normalize_select, normalization_type)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if file.endswith('.xlsx')]
            for file_path in excel_files:
                excel_normalize(file_path, row_normalize_select, global_normalize_select, normalization_type)
        elif mode == '模式三：处理单个excel':
            excel_normalize(file_path, row_normalize_select, global_normalize_select, normalization_type)
    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——excel数据归一化")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
