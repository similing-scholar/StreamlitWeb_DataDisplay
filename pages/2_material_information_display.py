'''
multipage_2
'''
import streamlit as st
from pages.multipages import material_information


# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="wide")
# ----------调用内容----------
excel_file_path = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/方案设计/【数据】原材料数据/化学品属性信息_ImgPath.xlsx'
material_information.main(excel_file_path)
