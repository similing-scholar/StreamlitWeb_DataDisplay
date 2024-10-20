import pandas as pd
import streamlit as st
import os


def LANDHE_csv2excel(file_path):
    """将LANDHE的csv测试数据转换为Excel文件"""
    # 读取csv文件内容
    df = pd.read_csv(file_path, delimiter=',', header=0,  encoding='GB2312')

    # 根据电流单位自动进行转换
    current_column = df.columns[df.columns.str.contains('电流')][0]
    if 'uA' in current_column:
        df['Current[A]'] = df[current_column] / 1e6  # 从 uA 转换为 A
    elif 'mA' in current_column:
        df['Current[A]'] = df[current_column] / 1e3  # 从 mA 转换为 A
    elif 'A' in current_column:
        df['Current[A]'] = df[current_column]  # 单位已经是 A，不需要转换

    # 创建新的 DataFrame
    new_df = pd.DataFrame({
        "Time[s]": df["测试时间/Sec"],  # 提取测试时间
        "Current[A]": df['Current[A]'],  # 使用自动转换后的电流
        "Potential[V]": df["电压/V"]  # 提取电压
    })

    df = new_df.astype(float).dropna()  # 转换为浮点数类型，并去除空白行

    # 将 DataFrame 保存为 Excel 文件
    file_name = file_path.split('.csv')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.csv', f'GCD_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path) as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, sheet_name='GCD', index=False)
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Excel file saved to {excel_output_path}")



@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有csv', '模式二：处理单个文件夹下的所有csv', '模式三：处理单个csv'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有csv':
        csv_farther_folder = st.text_input(
            "输入csv所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有csv':
        csv_folder = st.text_input("输入csv所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个csv':
        csv_path = st.text_input("输入csv的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\FTIR.csv**")

    # ---按mode执行---
    st.warning('蓝电系统的csv文件一般包括‘测试时间/Sec’、‘电流/uA’、‘电压/V’等列')
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有csv':
            csv_files = [os.path.join(root, file) for root, _, files in os.walk(csv_farther_folder) for file in files if
                         file.lower().endswith('.csv')]
            for file_path in csv_files:
                LANDHE_csv2excel(file_path)
        elif mode == '模式二：处理单个文件夹下的所有csv':
            csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if
                         file.lower().endswith('.csv')]  # 避免大小写问题
            for csv_file in csv_files:
                LANDHE_csv2excel(csv_file)
        elif mode == '模式三：处理单个csv':
            LANDHE_csv2excel(csv_path)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——LANDHE.csv文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()