'''
针对原材料数据，将'Struct', 'UV', 'IR', 'NearIR', 'HNMR', 'MS'图片的路径写入excel表格中
当项目被复制到一个新的文件夹时，需要重新运行这个文件，将图片最新的路径写入excel表格中
'''
import streamlit as st
import pandas as pd
import os


def update_excel_with_image_paths(input_file, output_file, image_folder):
    # 读取Excel文件的所有sheet
    all_sheets = pd.read_excel(input_file, sheet_name=None)

    # -----合并"单体"、"配体"和"氧化剂" sheet-----
    monomer_sheet = all_sheets['monomer']
    ligand_sheet = all_sheets['ligand']
    oxidant_sheet = all_sheets['oxidant']
    merged_solute_df = pd.concat([monomer_sheet, ligand_sheet, oxidant_sheet], ignore_index=True)

    # 在新的Excel文件中添加结构式、紫外光谱等图片列的路径
    for index, row in merged_solute_df.iterrows():
        chinese_name = row['Chinese Name']
        image_types = ['Struct', 'UV', 'IR', 'NearIR', 'HNMR', 'MS']
        for image_type in image_types:
            image_path = os.path.join(image_folder, f'{chinese_name}_{image_type}.png')
            if os.path.exists(image_path):
                merged_solute_df.loc[index, image_type] = image_path
        print(f'{chinese_name}图片路径已更新')


    # -----处理"溶剂" sheet-----
    solvent_sheet = all_sheets['solvent']
    merged_solvent_df = pd.concat([solvent_sheet], ignore_index=True)

    # 在新的Excel文件中添加结构式、紫外光谱等图片列的路径
    for index, row in merged_solvent_df.iterrows():
        chinese_name = row['Chinese Name']
        image_types = ['Struct', 'UV', 'IR', 'NearIR', 'HNMR', 'MS']
        for image_type in image_types:
            image_path = os.path.join(image_folder, f'{chinese_name}_{image_type}.png')
            if os.path.exists(image_path):
                merged_solvent_df.loc[index, image_type] = image_path
        print(f'{chinese_name}图片路径已更新')

    # -----创建新的Excel文件-----
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    # 将合并后的数据写入新的Excel文件
    merged_solute_df.to_excel(writer, sheet_name='solute', index=False)
    merged_solvent_df.to_excel(writer, sheet_name='solvent', index=False)
    # 保存新的Excel文件
    writer.save()

    return st.success(f'新的path已更新到：{output_file}')


def st_main(data_folder):
    st.subheader('对化学品原材料的`Struct`, `UV`, `IR`, `NearIR`, `HNMR`, `MS`图片的路径更新')
    input_file = st.text_input('化学品属性信息.xlsx的绝对路径：',
                               value=os.path.join(data_folder, '原材料数据\\化学品属性信息.xlsx'))
    output_file = st.text_input('化学品属性信息_ImgPath.xlsx的绝对路径：',
                                value=input_file.replace('.xlsx', '_ImgPath.xlsx'))
    image_folder = st.text_input('[images]化学品结构与表征信息文件夹的绝对路径：',
                                 value=os.path.join(data_folder, '原材料数据\\[images]化学品结构与表征信息'))
    if st.button('更新**化学品属性信息_ImgPath**.excel文件'):
        update_excel_with_image_paths(input_file, output_file, image_folder)




if __name__ == "__main__":
    # ./为访问同级目录 ../为访问上级目录 ../../为访问上上级目录
    input_folder = 'D:/BIT课题研究/微型光谱成像仪/【数据】导电聚合物数据/Streamlit_数据平台'
    input_file = os.path.join(input_folder, '化学品属性信息20230908.xlsx')
    output_file = os.path.join(input_folder, '化学品属性信息_ImgPath.xlsx')
    image_folder = os.path.join(input_folder, '化学品结构与表征信息')

    update_excel_with_image_paths(input_file, output_file, image_folder)