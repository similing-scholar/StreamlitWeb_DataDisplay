import pandas as pd
import streamlit as st
import os


def CV_segment(df, curve_label, writer):
    # 初始化变量
    segment_number = 1
    prev_potential = df.loc[0, 'Potential[V]']
    is_forward = True if df.loc[1, 'Potential[V]'] > prev_potential else False

    # 创建空列表用于存储分段的DataFrame
    segment_list = []

    # 初始化空字典，用于存储当前 segment 数据
    segment_data = {
        'Time[s]': [],
        'Potential[V]': [],
        'Current[A]': []
    }

    # 遍历数据行，检测电位变化并识别 segment
    for i in range(len(df)):
        current_potential = df.loc[i, 'Potential[V]']

        # 检查电位翻转并标记 segment
        if (is_forward and current_potential < prev_potential) or \
                (not is_forward and current_potential > prev_potential):
            # 将当前 segment 的数据存储到一个临时 DataFrame 中
            temp_df = pd.DataFrame(segment_data)
            temp_df.columns = [
                f'Segment {segment_number} Time[s]',
                f'Segment {segment_number} Potential[V]',
                f'Segment {segment_number} Current[A]'
            ]
            # 将临时 DataFrame 添加到 segment_list
            segment_list.append(temp_df)

            # 更新变量以开始新的 segment
            segment_number += 1
            is_forward = not is_forward

            # 重置 segment 数据
            segment_data = {
                'Time[s]': [],
                'Potential[V]': [],
                'Current[A]': []
            }

        # 将当前行数据添加到 segment 数据中
        segment_data['Time[s]'].append(df.loc[i, 'Time[s]'])
        segment_data['Potential[V]'].append(df.loc[i, 'Potential[V]'])
        segment_data['Current[A]'].append(df.loc[i, 'Current[A]'])

        prev_potential = current_potential

    # 最后一个 segment 也需要添加到 segment_list 中
    temp_df = pd.DataFrame(segment_data)
    temp_df.columns = [
        f'Segment {segment_number} Time[s]',
        f'Segment {segment_number} Potential[V]',
        f'Segment {segment_number} Current[A]'
    ]
    segment_list.append(temp_df)

    # 将所有 segment 合并成一个大的 DataFrame
    segments_df = pd.concat(segment_list, axis=1)

    # 保存到 Excel 文件
    segments_df.to_excel(writer, sheet_name='CV_segment', index=False)
    st.success(f"CV segment data saved to Excel file with curve label: {curve_label}")


def GCD_segment(df, curve_label, writer):
    # 初始化变量
    segment_number = 1
    prev_current = df.loc[0, 'Current[A]']
    is_positive = True if df.loc[1, 'Current[A]'] > 0 else False

    # 创建空列表用于存储分段的DataFrame
    segment_list = []

    # 初始化空字典，用于存储当前 segment 数据
    segment_data = {
        'Time[s]': [],
        'Current[A]': [],
        'Potential[V]': []
    }

    # 遍历数据行，检测电流反向并识别 segment
    for i in range(len(df)):
        current_current = df.loc[i, 'Current[A]']

        # 检查电流反转并标记 segment
        if (is_positive and current_current < 0) or (not is_positive and current_current > 0):
            # 将当前 segment 的数据存储到一个临时 DataFrame 中
            temp_df = pd.DataFrame(segment_data)
            temp_df.columns = [
                f'Segment {segment_number} Time[s]',
                f'Segment {segment_number} Current[A]',
                f'Segment {segment_number} Potential[V]'
            ]
            # 将临时 DataFrame 添加到 segment_list
            segment_list.append(temp_df)

            # 更新变量以开始新的 segment
            segment_number += 1
            is_positive = not is_positive

            # 重置 segment 数据
            segment_data = {
                'Time[s]': [],
                'Current[A]': [],
                'Potential[V]': []
            }

        # 将当前行数据添加到 segment 数据中
        segment_data['Time[s]'].append(df.loc[i, 'Time[s]'])
        segment_data['Current[A]'].append(df.loc[i, 'Current[A]'])
        segment_data['Potential[V]'].append(df.loc[i, 'Potential[V]'])

        prev_current = current_current

    # 最后一个 segment 也需要添加到 segment_list 中
    temp_df = pd.DataFrame(segment_data)
    temp_df.columns = [
        f'Segment {segment_number} Time[s]',
        f'Segment {segment_number} Current[A]',
        f'Segment {segment_number} Potential[V]'
    ]
    segment_list.append(temp_df)

    # 将所有 segment 合并成一个大的 DataFrame
    segments_df = pd.concat(segment_list, axis=1)

    # 保存到 Excel 文件
    segments_df.to_excel(writer, sheet_name='GCD_segment', index=False)
    st.success(f"GCD segment data saved to Excel file with curve label: {curve_label}")


def split_segment(folder_path):
    single_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

    for single_file_name in single_files:
        single_file_path = os.path.join(folder_path, single_file_name)
        # 读取excel文件数据
        workbook = pd.ExcelFile(single_file_path)
        sheet_names = workbook.sheet_names
        df = workbook.parse(sheet_names[0])
        # 获取file_name，即电学曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]
        # 保存路径
        save_path = os.path.join(folder_path, 'segment_' + single_file_name)

        # 初始化新的 Excel writer
        with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
            if 'CV' in sheet_names[0]:
                CV_segment(df, curve_label, writer)
            elif 'GCD' in sheet_names[0]:
                GCD_segment(df, curve_label, writer)

            # 保留其他 sheet 的数据
            for sheet_name in sheet_names[1:]:
                df_other = workbook.parse(sheet_name)
                df_other.to_excel(writer, sheet_name=sheet_name, index=False)

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input(
            "输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    st.warning('根据文件名自动区分CV/GCD')

    # ---按mode执行---
    if st.button('运行数据分列程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有子文件夹的路径
            subfolders = [os.path.join(excel_farther_folder, subfolder) for subfolder in
                          os.listdir(excel_farther_folder)]
            for subfolder in subfolders:
                split_segment(subfolder)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            split_segment(excel_folder)

    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——CV/GCD.excel数据分列")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
