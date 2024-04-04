"""
page_3：将化学氧化聚合数据进行整合与展示，以便于分析数据
"""
import streamlit as st
from pages.multipages import chemical_polymerization


# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="wide")
# ----------调用内容----------
excel_file_path = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/PJ_数据整理/化学氧化聚合数据/氧化聚合实验溶液数据_分析.xlsx'
chemical_polymerization.main(excel_file_path)