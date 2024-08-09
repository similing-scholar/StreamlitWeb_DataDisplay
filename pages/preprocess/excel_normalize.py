"""对excel中的数据进行归一化"""
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt


def normalize_series(series):
    """归一化给定的Pandas Series到0-1之间。"""
    min_value = series.min()
    max_value = series.max()
    return (series - min_value) / (max_value - min_value)


def normalize_individual_columns(df):
    """对DataFrame中从第二列开始的每一列依次归一化。"""
    for column in df.columns[1:]:
        df[column] = normalize_series(df[column])
    return df


def normalize_series_global(series, global_min, global_max):
    """使用全局最小值和最大值归一化给定的Pandas Series到0-1之间。"""
    return (series - global_min) / (global_max - global_min)


def normalize_all_y_together_optimized(df):
    """对DataFrame中从第二列开始的所有列一起归一化，使用全局最大值和最小值。"""
    all_y = df.iloc[:, 1:]
    global_min = all_y.min().min()  # 找到所有列的全局最小值
    global_max = all_y.max().max()  # 找到所有列的全局最大值
    # 应用归一化
    for column in all_y.columns:
        df[column] = normalize_series_global(df[column], global_min, global_max)
    return df


def excel_normalize(file_path, row_normalize_select, global_normalize_select):
    """归一化"""
    # 读取excel文件数据
    workbook = pd.ExcelFile(file_path)
    sheet_name = workbook.sheet_names[0]
    df = workbook.parse(sheet_name)
    # 获取X列
    x_col_name = df.columns[0]
    # 获取file_name
    file_name = file_path.split('.xlsx')[0].split('\\')[-1]
    # 保存路径
    new_file_name = 'Normalized_'+file_name
    save_path = file_path.replace(file_name, new_file_name)

    # 归一化处理
    df_individual_normalized = normalize_individual_columns(df.copy())
    df_all_y_normalized = normalize_all_y_together_optimized(df.copy())

    # 添加列名前缀
    df_individual_normalized.columns = [x_col_name] + ['row_normalized_' + col for col in df_individual_normalized.columns[1:]]
    df_all_y_normalized.columns = [x_col_name] + ['global_normalized_' + col for col in df_all_y_normalized.columns[1:]]

    # 将归一化结果保存回新的Excel文件
    if row_normalize_select:
        # 保存路径
        save_path = file_path.replace(file_name, 'RowNormalized_' + file_name)
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            df_individual_normalized.to_excel(writer, sheet_name=sheet_name, index=False)
            # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
            parameters = pd.DataFrame({'File Name': [file_name]})
            parameters.to_excel(writer, sheet_name='parameter', index=False)
        st.success(f"normalized excel file saved to {save_path}")

    if global_normalize_select:
        save_path = file_path.replace(file_name, 'GlobalNormalized_' + file_name)
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            df_all_y_normalized.to_excel(writer, sheet_name=sheet_name, index=False)
            # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
            parameters = pd.DataFrame({'File Name': [file_name]})
            parameters.to_excel(writer, sheet_name='parameter', index=False)
        st.success(f"normalized excel file saved to {save_path}")

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
        file_path = st.text_input("输入excel的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\normalize.xlsx**")

    # ---归一化选择---

    row_normalize_select = st.checkbox('是否进行列归一化（每一y列各自归一化）', value=True)
    global_normalize_select = st.checkbox('是否进行全局归一化（所有y列一起归一化）', value=False)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有excel文件的路径
            excel_files = [os.path.join(root, file) for root, _, files in os.walk(excel_farther_folder) for file in files if
                         file.endswith('.xlsx')]
            # 处理每个excel文件
            for file_path in excel_files:
                excel_normalize(file_path, row_normalize_select, global_normalize_select)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            excel_files = [os.path.join(excel_folder, file) for file in os.listdir(excel_folder) if file.endswith('.xlsx')]
            for file_path in excel_files:
                excel_normalize(file_path, row_normalize_select, global_normalize_select)
        elif mode == '模式三：处理单个excel':
            excel_normalize(file_path, row_normalize_select, global_normalize_select)
    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——excel数据归一化")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
