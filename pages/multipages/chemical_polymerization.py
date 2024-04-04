'''
展示化学氧化聚合制备电致变色薄膜的streamlit页面
'''
import pandas as pd
import streamlit as st
import base64
import os
import PIL.Image as Image
from st_aggrid import GridOptionsBuilder, AgGrid
from st_aggrid.shared import JsCode


ShowImage = JsCode("""
    function (params) {
        var element = document.createElement("span");
        var imageElement = document.createElement("img");
        var columnName = params.column.getColId();

        if (params.data[columnName] !== '') {
            imageElement.src = params.data[columnName];
            imageElement.width = "100"; 
        } else { 
            imageElement.src = ""; 
            return element; 
        }

        element.appendChild(imageElement);
        return element;
    };
""")


def create_image_uri(image_path):
    """读取本地图片文件并将其转换为Base64编码的字符串
    """
    try:
        image_bs64 = base64.b64encode(open(image_path, 'rb').read()).decode()
        image_format = image_path[-4:]
        return f'data:image/{image_format};base64,' + image_bs64
    except:
        return ""


def string_to_list(path_string, separator=','):
    """将逗号分隔的多个路径字符串转换为列表
    """
    if isinstance(path_string, str):
        path_list = path_string.split(separator)
        path_list = [path.strip() for path in path_list]
        return path_list
    else:
        return []


def img_paths_to_dataframe(path_list):
    # 创建一个字典，其中键是列名，值是路径列表中的对应路径
    data = {}
    # 遍历路径列表
    for path in path_list:
        if path.lower().endswith('.png'):
            column_name = os.path.basename(path)
            # 创建Base64编码的URI并将其存储为值
            data[column_name] = [create_image_uri(path)]
    # 返回只有图片的dataframe
    return pd.DataFrame(data)


def resize_image(image_path, target_height=50):
    image = Image.open(image_path)
    width, height = image.size
    target_width = int((width / height) * target_height)
    resized_image = image.resize((target_width, target_height), Image.ANTIALIAS)
    return resized_image


# @st.cache_resource
def show_raw_data(excel_file_path):
    """-----📋原始数据展示-----"""
    # 读取Excel文件
    df = pd.read_excel(excel_file_path, sheet_name='solution_analyze')
    # 将日期格式化为YYYY-MM-DD
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    # 使用Pandas切片[::-1]反转数据帧
    reversed_df = df[::-1]
    # 创建streamlit表格，倒叙展示数据行
    st.dataframe(reversed_df)
    return None


# @st.cache_data(experimental_allow_widgets=True)
def data_analysis(excel_file_path):
    """-----🔎数据分析-----"""
    # ---读取Excel文件---
    df = pd.read_excel(excel_file_path, sheet_name='solution_analyze')
    # 使用Pandas切片[::-1]反转数据帧
    df = df[::-1]
    # 将日期格式化为YYYY-MM-DD
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

    # ---通过日期和编号锁定样品---
    selected_date = st.multiselect('选择需要的Date作为初次筛选条件', df['Date'].tolist())  # 创建多项选择框
    # 使用布尔索引筛选出指定日期的行
    filtered_df = df[df['Date'].isin(selected_date)]  # 传入日期列表
    # 筛选出指定编号的行
    selected_number = st.multiselect('选择需要的Solution Number', filtered_df['Solution Number'].tolist())
    filtered_df = filtered_df[filtered_df['Solution Number'].isin(selected_number)]
    # 添加选择按钮，一键选择该日期下所有编号
    select_all_number = st.checkbox('选择该日期下所有编号')
    if select_all_number:
        filtered_df = df[df['Date'].isin(selected_date)]
        selected_number = filtered_df['Solution Number'].tolist()

    # ---反应后水溶液表观状态---
    st.markdown("- **反应后混合溶液的表观状态**")
    col1, col2 = st.columns([0.3, 0.4])

    with col1:
        # 将"Solution Number"列设置为索引
        filtered_df.set_index('Solution Number', inplace=True)
        # 使用transpose()方法将数据转置
        solution_state_df = filtered_df[['Viscosity', 'Graininess', 'Phase', 'Other Phenomena',
                                         'Capillary Height (Filtered)', 'Capillary Height (Unfiltered)']].transpose()
        st.data_editor(solution_state_df)

        # 将所选编号对应的图片显示在网页上
        for solution_number in selected_number:
            # 读取单元格中的图片路径，并将其转换为列表
            solution_image_paths = string_to_list(filtered_df.loc[solution_number, 'Solution Image'])
            # 将图片路径列表转换为dataframe，其中路径转为Base64编码的URI
            solution_image_df = img_paths_to_dataframe(solution_image_paths)
            # 使用Ag-Grid在网页上显示图片
            builder = GridOptionsBuilder.from_dataframe(solution_image_df, enableRowGroup=True)
            builder.configure_default_column(min_colunms_width=1, wrapText=True, autoHeight=True)
            builder.configure_columns(solution_image_df.columns, cellRenderer=ShowImage)
            go = builder.build()
            AgGrid(solution_image_df, gridOptions=go, theme='fresh', height=130, allow_unsafe_jscode=True)





def main(excel_file_path):
    # -----🔬-----
    st.title(':microscope: 化学氧化聚合过程数据分析')

    # -----📋原始数据展示-----
    st.subheader(":clipboard: 原始数据展示")
    show_raw_data(excel_file_path)

    # -----🔎数据分析-----
    st.subheader(":mag_right: 数据分析")
    data_analysis(excel_file_path)

    return None


if __name__ == "__main__":
    excel_file_path = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/PJ_数据整理/化学氧化聚合数据/氧化聚合实验数据_分析.xlsx'
    main(excel_file_path)
