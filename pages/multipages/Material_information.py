'''
展示材料基本属性的streamlit页面
'''
import streamlit as st
import pandas as pd
import base64
from st_aggrid import GridOptionsBuilder, AgGrid
from st_aggrid.shared import JsCode


# 定义一个用于显示图片的JavaScript函数，在表格的每个单元格中显示图片
# 根据列名修改params.data中的属性，单元格的数据不为空，则创建一个包含图片的img元素
# 将img元素和文本内容添加到一个span元素中，并返回该span元素作为单元格的内容。
ShowImage = JsCode("""
    function (params) {
        var element = document.createElement("span");
        var imageElement = document.createElement("img");
        var columnName = params.column.getColId();

        if (params.data[columnName] !== '') {
            imageElement.src = params.data[columnName];
            imageElement.width = "30"; 
        } else { 
            imageElement.src = ""; 
            return element; 
        }

        element.appendChild(imageElement);
        return element;
    };
""")


# @st.cache_data  # 缓存加载数据
# 读取Excel文件函数
def load_data(excel_file_path, sheet_name):
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    return df


# 将本地的图片转为web可读的uri格式
def create_image_uri(image_path):
    try:
        image_bs64 = base64.b64encode(open(image_path, 'rb').read()).decode()  # 读取本地图片文件并将其转换为Base64编码的字符串
        image_format = image_path[-4:]  # 后四个字符是图片的格式类型
        return f'data:image/{image_format};base64,' + image_bs64
    # 读取或转换失败，则返回空字符串
    except:
        return ""


def display_solute_information(df_solute):
    # -----📓-----
    st.subheader(":notebook:溶质基本属性信息查询")
    # 使用apply方法，在DataFrame的每一行上应用写入uri信息函数
    for row in ['Struct', 'UV', 'NearIR', 'IR', 'HNMR', 'MS']:
        df_solute[row] = df_solute[row].apply(create_image_uri)

    # 多项选择按钮，用于选择要显示的列
    selected_columns = st.multiselect('多项选择框中为默认排序，可根据需要选择显示的数据列', df_solute.columns,
                                      default=['Chinese Name', 'Molecular Formula', 'Struct', 'Molecular Weight',
                                               'Classification', 'Water Soluble', 'Polar Surface Area',
                                               'UV', 'NearIR', 'IR', 'HNMR', 'MS'])
    # 根据选择的列过滤DataFrame
    df_solute = df_solute[selected_columns]
    df_solute_copy = df_solute.copy()

    # 使用ImageColumn展示图片
    column_config = {
        'Struct': st.column_config.ImageColumn('Struct', help="化学品结构式图片"),
        'UV': st.column_config.ImageColumn('UV', help="化学品紫外光谱图片"),
        'NearIR': st.column_config.ImageColumn('NearIR', help="化学品近红外光谱图片"),
        'IR': st.column_config.ImageColumn('IR', help="化学品红外光谱图片"),
        'HNMR': st.column_config.ImageColumn('HNMR', help="化学品核磁氢谱图片"),
        'MS': st.column_config.ImageColumn('MS', help="化学品质谱图片")
    }
    st.data_editor(df_solute, column_config=column_config, height=500, hide_index=True)

    # -----📓-----
    st.text('根据以上表格的内容自动配置一个新的Ag-Grid表格，通过以下表格可以实现更完善的筛选功能')
    # 构建一个用于Ag-Grid的选项配置
    builder = GridOptionsBuilder.from_dataframe(df_solute_copy, enableRowGroup=True)
    # 默认设置：给每一列设置为最小列宽
    builder.configure_default_column(min_colunms_width=1, pinned='left', aggFunc='sum',
                                     groupable=True, wrapText=True, autoHeight=True)
    # 配置行选择模式为多选
    builder.configure_selection('multiple', use_checkbox=True,
                                groupSelectsChildren="Group checkbox select children")
    # 配置Ag-Grid的侧边栏
    builder.configure_side_bar()
    # 配置Struct UV NearIR IR HNMR MS列，使用cellRenderer参数来指定一个用于显示图片的JavaScript函数。
    builder.configure_columns(['Struct', 'UV', 'NearIR', 'IR', 'HNMR', 'MS'], cellRenderer=ShowImage)
    go = builder.build()
    # 在web上显示DataFrame对象
    AgGrid(df_solute_copy, gridOptions=go, theme='light', height=300, allow_unsafe_jscode=True)

    return None


def display_solvent_information(df_solvent):
    # -----📓-----
    st.subheader(":notebook:溶剂基本属性信息查询")
    # 使用apply方法，在DataFrame的每一行上应用写入uri信息函数
    for row in ['Struct', 'UV', 'NearIR', 'IR', 'HNMR', 'MS']:
        df_solvent[row] = df_solvent[row].apply(create_image_uri)

    # 多项选择按钮，用于选择要显示的列
    selected_columns = st.multiselect('多项选择框中为默认排序，可根据需要选择显示的数据列', df_solvent.columns,
                                      default=df_solvent.columns.tolist())
    # 根据选择的列过滤DataFrame
    df_solvent = df_solvent[selected_columns]

    # 使用ImageColumn展示图片
    column_config = {
        'Struct': st.column_config.ImageColumn('Struct', help="化学品结构式图片"),
        'UV': st.column_config.ImageColumn('UV', help="化学品紫外光谱图片"),
        'NearIR': st.column_config.ImageColumn('NearIR', help="化学品近红外光谱图片"),
        'IR': st.column_config.ImageColumn('IR', help="化学品红外光谱图片"),
        'HNMR': st.column_config.ImageColumn('HNMR', help="化学品核磁氢谱图片"),
        'MS': st.column_config.ImageColumn('MS', help="化学品质谱图片")
    }
    st.data_editor(df_solvent, column_config=column_config, height=500, hide_index=True)

    # -----📓-----
    st.text('根据以上表格的内容自动配置一个新的Ag-Grid表格，通过以下表格可以实现更完善的筛选功能')
    # 构建一个用于Ag-Grid的选项配置
    builder = GridOptionsBuilder.from_dataframe(df_solvent, enableRowGroup=True)
    # 默认设置：给每一列设置为最小列宽
    builder.configure_default_column(min_colunms_width=1, pinned='left', groupable=True, wrapText=True,
                                     autoHeight=True)
    # 配置行选择模式为多选
    builder.configure_selection('multiple', use_checkbox=True,
                                groupSelectsChildren="Group checkbox select children")
    # 配置Ag-Grid的侧边栏
    builder.configure_side_bar()
    # 配置Struct UV NearIR IR HNMR MS列，使用cellRenderer参数来指定一个用于显示图片的JavaScript函数。
    builder.configure_columns(['Struct', 'UV', 'NearIR', 'IR', 'HNMR', 'MS'], cellRenderer=ShowImage)
    go = builder.build()
    # 在web上显示DataFrame对象
    AgGrid(df_solvent, gridOptions=go, theme='light', height=300, allow_unsafe_jscode=True)

    return None


# 主函数
def main(excel_file_path):
    # ----------页面属性控制----------
    # 设置页面宽度必须在第一句
    st.set_page_config(layout="wide")
    # -----📚-----
    st.title(':books:化学品基本属性信息展示')

    # 使用侧边栏选择要展示的多页面
    page = st.sidebar.selectbox("通过下拉框选择化学品类别", ["溶质", "溶剂"])

    # ----------第一展示区----------
    if page == "溶质":
        df_solute = load_data(excel_file_path, 'solute')
        display_solute_information(df_solute)

    # ----------第二展示区----------
    if page == "溶剂":
        df_solvent = load_data(excel_file_path, 'solvent')
        display_solvent_information(df_solvent)

    return None


if __name__ == "__main__":
    # 替换为您的Excel文件路径
    excel_file_path = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/方案设计/【数据】原材料数据/化学品属性信息_ImgPath.xlsx'
    main(excel_file_path)




