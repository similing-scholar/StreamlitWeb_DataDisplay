"""
page_2：对于原材料的一些信息进行展示
"""
import streamlit as st
import os
from pages.multipages import material_information


# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="wide")
# ----------路径----------
# excel_file_path = './StreamlitWeb/datas/化学品属性信息_ImgPath.xlsx'
data_catalog = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/Streamlit_数据平台'  # 【修改地址】
excel_file_path = os.path.join(data_catalog, '原材料数据/化学品属性信息20231129_ImgPath.xlsx')
# ----------调用内容----------
material_information.main(excel_file_path)
