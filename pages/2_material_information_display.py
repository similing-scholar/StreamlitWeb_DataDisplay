'''
multipage_2
'''
import streamlit as st
from pages.multipages import material_information


# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="wide")
# ----------调用内容----------
excel_file_path = './StreamlitWeb/testdata/化学品属性信息_ImgPath.xlsx'
material_information.main(excel_file_path)
