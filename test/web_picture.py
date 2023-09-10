import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid
from st_aggrid.shared import JsCode
import base64


# 读取本地图片文件并将其转换为Base64编码的字符串
def ReadPictureFile(wch_fl):
    try:
        return base64.b64encode(open(wch_fl, 'rb').read()).decode()
    # 读取或转换失败，则返回空字符串
    except:
        return ""


# JavaScript代码定义了一个函数，在表格的每个单元格中显示图片
# 单元格的 ImgPath 数据，如果不为空，则创建一个包含图片的 img 元素
# 将 img 元素和文本内容添加到一个 span 元素中，并返回该 span 元素作为单元格的内容。
ShowImage = JsCode("""function (params) {
            var element = document.createElement("span");
            var imageElement = document.createElement("img");
                
            if (params.data.ImgPath != '') {
                imageElement.src = params.data.ImgPath;
                imageElement.width = "30";
                imageElement.height = "30"; 
            } else { imageElement.src = ""; }
            element.appendChild(imageElement);
            element.appendChild(document.createTextNode(params.value));
            return element;
            }""")

df = pd.DataFrame({'Name': ['Iron Man', 'Walter White', 'Wonder Woman', 'Bat Woman'],
                   'Face': ['', '', '', ''],
                   'ImgLocation': ['Local', 'Local', 'Web', 'Web'],
                   'ImgPath': ['D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/方案设计/【数据】原材料数据/化学品结构与表征信息/1,4-二丙烯酰基哌嗪_Struct.png',
                               'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/方案设计/【数据】原材料数据/化学品结构与表征信息/1,4-二丙烯酰基哌嗪_Struct.png',
                               '',
                               'https://img00.deviantart.net/85f5/i/2012/039/a/3/batwoman_headshot_4_by_ricber-d4p1y86.jpg']})

# 对数据进行处理，如果 'ImgLocation' 为 'Local'，则将 'ImgPath' 列的图片文件转换为Base64编码的字符串，并更新 'ImgPath' 列的值。
if df.shape[0] > 0:  # DataFrame的行数＞0
    for i, row in df.iterrows():  # 逐行访问DataFrame中的数据，返回当前行的索引和包含当前行数据的Series对象
        if row.ImgLocation == 'Local':
            imgExtn = row.ImgPath[-4:]  # 提取后四个字符，确定图片的类型
            # 构建一个包含Base64编码图像数据的数据URI
            row.ImgPath = f'data:image/{imgExtn};base64,' + ReadPictureFile(row.ImgPath)

# 构建一个用于Ag-Grid的选项配置
gb = GridOptionsBuilder.from_dataframe(df)
# 配置 'Face' 列的单元格渲染器为前面定义的 ShowImage 函数
gb.configure_column('ImgPath', cellRenderer=ShowImage)
# 配置 'ImgPath' 列隐藏
# gb.configure_column("ImgPath", hide="True")


# 使用 AgGrid 创建一个Ag-Grid数据表格，传入DataFrame (df) 和之前创建的选项配置 (vgo)。
# 设置表格的主题为 'blue'，高度为 150 像素，并允许不安全的JavaScript代码执行
vgo = gb.build()
AgGrid(df, gridOptions=vgo, theme='blue', height=150, allow_unsafe_jscode=True)