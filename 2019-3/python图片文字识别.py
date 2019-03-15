
"""
Python 图片文字识别：
1、安装百度AI ： pip install baidu-aip 
2、到 https://console.bce.baidu.com/ai/#/ai/ocr/app/list 创建文字识别应用，获取APP_ID、API_KEY、SECRET_KEY
"""


from aip import AipOcr


# 定义常量  
# APP_ID = '10379743'
# API_KEY = 'QGGvDG2yYiVFvujo6rlX4SvD'
# SECRET_KEY = 'PcEAUvFO0z0TyiCdhwrbG97iVBdyb3Pk'
APP_ID = '11716753'
API_KEY = 'IF8RzaeiHUv44ehkfSKcVmIL'
SECRET_KEY = 'qxwg7lwgh2n01rpWKGDLcEBPP9hOjfkK'

# 初始化文字识别分类器
aipOcr=AipOcr(APP_ID, API_KEY, SECRET_KEY)

# 读取图片  
filePath = r"C:\Users\Administrator\Desktop\img_tgb\2009-06-26_CQ9CUM75SH97.jpg"
# filePath = r'C:\Users\Administrator\Desktop\b.jpg'

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 定义参数变量
options = {
    'detect_direction': 'true',
    'language_type': 'CHN_ENG',
}

# 网络图片文字文字识别接口
result = aipOcr.webImage(get_file_content(filePath),options)

# 如果图片是url 调用示例如下
# result = apiOcr.webImage('http://www.xxxxxx.com/img.jpg')

print(result)
print(result['words_result'])
