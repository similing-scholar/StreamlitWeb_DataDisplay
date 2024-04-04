"""
page_3：对数据的调用路径进行更新
"""
import streamlit as st
from pages.newpath import material_information_path2excel


# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="wide")
st.title(":horse_racing: 更新数据调用路径")  # 🏇


# ----------页面内容（路径更新）----------
data_catalog = st.text_input('输入数据总目录的绝对路径，如**D:\\BIT\\PJ_数据整理**',
                             value='D:\\BIT课题研究\\微型光谱成像仪\\【数据】导电聚合物数据\\PJ_数据整理')
material_information_path2excel.st_main(data_catalog)


# ----------页面内容（数据展示的调用）----------
