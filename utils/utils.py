import base64


def create_image_uri(image_path):
    try:
        image_bs64 = base64.b64encode(open(image_path, 'rb').read()).decode()  # 读取本地图片文件并将其转换为Base64编码的字符串
        image_format = image_path[-4:]  # 后四个字符是图片的格式类型
        return f'data:image/{image_format};base64,' + image_bs64
    # 读取或转换失败，则返回空字符串
    except:
        return ""