"""
page_0：将数据从原始格式转换为统一格式，并初步进行批量预处理
"""
import streamlit as st

from pages.preprocess import (keithley_txt2excel, ichy_csv2excel, IV_excel2fig_merge, electricity_excel2fig,
                              uv_sca2excel, uv_excel_merge2fig,
                              avantes_raw2excel, avantes_excel2fig_split, olympus_csv2excel,
                              XRD_txt2excel, XRD_excel2fig, FTIR_csv2excel, FTIR_excel2fig,
                              image_add_name_scale, files_remove, files_copy)

# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="wide")

# 设置选项按钮，选择运行哪个数据预处理程序
tools = ['keithley.txt转excel', 'ichy.csv转excel', '电阻.excel数据合并与画图', '其他电学.excel数据画图',
         'uv.sca转excel', 'uv.excel数据合并与画图',
         'avantes.raw转excel', 'avantes.excel数据画图与拆分',
         'olympus.csv转excel', 'XRD.txt转excel', 'XRD.excel数据画图', 'FTIR.csv转excel', 'FTIR.excel数据画图',
         'image添加名称与比例尺', '批量删除文件', '批量复制/移动文件']
option = st.sidebar.selectbox('选择运行哪个数据**批量预处理**小程序', tools)
if option == 'keithley.txt转excel':
    keithley_txt2excel.st_main()
elif option == 'ichy.csv转excel':
    ichy_csv2excel.st_main()
elif option == '电阻.excel数据合并与画图':
    IV_excel2fig_merge.st_main()
elif option == '其他电学.excel数据画图':
    electricity_excel2fig.st_main()
elif option == 'uv.sca转excel':
    uv_sca2excel.st_main()
elif option == 'uv.excel数据合并与画图':
    uv_excel_merge2fig.st_main()
elif option == 'avantes.raw转excel':
    avantes_raw2excel.st_main()
elif option == 'olympus.csv转excel':
    olympus_csv2excel.st_main()
elif option == 'avantes.excel数据画图与拆分':
    avantes_excel2fig_split.st_main()
elif option == 'XRD.txt转excel':
    XRD_txt2excel.st_main()
elif option == 'XRD.excel数据画图':
    XRD_excel2fig.st_main()
elif option == 'FTIR.csv转excel':
    FTIR_csv2excel.st_main()
elif option == 'FTIR.excel数据画图':
    FTIR_excel2fig.st_main()
elif option == 'image添加名称与比例尺':
    image_add_name_scale.st_main()
elif option == '批量删除文件':
    files_remove.st_main()
elif option == '批量复制/移动文件':
    files_copy.st_main()

