'''
multipage_2
'''
import streamlit as st
from pages.multipages import Material_information


# 调用内容
excel_file_path = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/方案设计/【数据】原材料数据/化学品属性信息_ImgPath.xlsx'
Material_information.main(excel_file_path)
