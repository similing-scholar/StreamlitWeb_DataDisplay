"""将keithley的txt测试数据转换为Excel文件"""
import pandas as pd
import re
import streamlit as st
import os


def kei_txt2excel(file_path, columns, current_unit):
    """注意原始txt列数，起始行的处理"""
    # 读取文件内容
    with open(file_path, 'r') as file:
        content = file.readlines()

    # 匹配一个或多个非 \t 字符，后面跟着 '测试数据' 字符串
    pattern = r'([^\t]+测试数据)'
    matches = re.findall(pattern, content[0])
    # 根据文字信息匹配测试模式
    if matches[0] == 'I-V测试数据':
        scan_model = 'CV'
        columns = ['Potential[V]', 'Current[mA]']
    elif matches[0] == '方波信号测试数据':
        scan_model = 'CA'
        columns = ['Time[s]', 'Potential[V]', 'Current[mA]']
    else:
        scan_model = 'Electricity'

    # 处理第一行内容，只保留'I-V测试数据'之前的部分
    content[0] = content[0].split(matches[0])[0].strip()

    # 提取电压和电流数据，并将其转换为浮点数
    data = [[float(value) for value in line.split()] for line in content]  # 从第二行开始处理，并将数据转换为浮点数
    df = pd.DataFrame(data, columns=columns)  # 【可修改第一列，第二列列名】

    # 将电流单位转为A
    if current_unit:
        df['Current[mA]'] = df['Current[mA]'] / 1000
        df.rename(columns={'Current[mA]': 'Current[A]'}, inplace=True)

    # 将数据保存为Excel文件，包含处理后的第一行，指定工作表名称为文件名
    file_name = file_path.split('.txt')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.txt', f'{scan_model}_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, index=False, header=True, startrow=0, sheet_name=scan_model)  # 从第一行开始写入数据，包含标题行
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Excel file saved to {excel_output_path}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有txt', '模式二：处理单个文件夹下的所有txt', '模式三：处理单个txt'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有txt':
        txt_farther_folder = st.text_input("输入txt所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
        st.warning('（除IV和方波信号）需要保证该目录下所有子文件夹内的txt格式一致，即列数相同')
    elif mode == '模式二：处理单个文件夹下的所有txt':
        txt_folder = st.text_input("输入txt所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
        st.warning('（除IV和方波信号）需要保证该文件夹内的txt格式一致，即列数相同')
    elif mode == '模式三：处理单个txt':
        txt_path = st.text_input("输入txt的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\kei.txt**")

    # ---colunms选择---
    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        columns_select = st.selectbox('选择原始txt对应的**所有列名**选项',
                                      ('Potential[V], Current[mA]',
                                       'time[s], Potential[V], Current[mA]'))
        st.warning('**I-V测试数据**和**方波信号测试数据**已实现自动列标题识别')
    with col2:
        columns_input = st.text_input('可自定义输入**所有列名**（需用英文逗号隔开），例如：Potential[V], Current[mA]')
    if columns_input:
        columns = [col.strip() for col in columns_input.split(',')]
    else:
        columns = [col.strip() for col in columns_select.split(',')]
    # st.text(columns)

    # ---电流单位选择---
    current_unit = st.checkbox('是否将电流单位转为A（原始数据是mA）', value=True)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有txt':
            # 获取所有txt文件的路径
            txt_files = [os.path.join(root, file) for root, _, files in os.walk(txt_farther_folder) for file in files if
                         file.endswith('.txt')]
            # 处理每个txt文件
            for file_path in txt_files:
                kei_txt2excel(file_path, columns=columns, current_unit=current_unit)
        elif mode == '模式二：处理单个文件夹下的所有txt':
            txt_files = [os.path.join(txt_folder, file) for file in os.listdir(txt_folder) if file.endswith('.txt')]
            for file_path in txt_files:
                kei_txt2excel(file_path, columns=columns, current_unit=current_unit)
        elif mode == '模式三：处理单个txt':
            kei_txt2excel(txt_path, columns=columns, current_unit=current_unit)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——keithley.txt文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
