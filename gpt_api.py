from openai import OpenAI
import os
import base64
import sys
from PIL import Image
from io import BytesIO

# os.environ["http_proxy"] = ""
# os.environ["https_proxy"] = ""


# url = 'https://mian.456478.xyz/v1'
url = 'https://api.openai.com/v1/'
token = os.getenv("OPENAI_API_KEY")

if not token:
    print("Error: 环境变量 OPENAI_API_KEY 未设置！")
    sys.exit(1)
model = os.getenv("model_choice")

if not model:
    print("Error: 环境变量 model_choice 未设置！")
    sys.exit(1)
#  base 64 编码格式
def encode_image(image_path: str, max_size: int = 1280) -> str:
    """
    打开 image_path 指定的图片，
    如果宽或高的最大值 > max_size，则按等比缩小到最长边为 max_size，
    然后转换为 RGB 模式并以 JPEG 格式编码，返回 base64 字符串。
    """
    with Image.open(image_path) as img:
        w, h = img.size
        max_dim = max(w, h)
        if max_dim > max_size:
            scale = max_size / max_dim
            new_size = (int(w * scale), int(h * scale))
            img = img.resize(new_size, Image.LANCZOS)

        # 如果有透明通道，转换为 RGB
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

spec_prompt = """
你是UI设计专家。请参考我的页面描述，描述图片中的页面，给出页面的布局结构、基本颜色样式、页面组件结构，必须全面的描述图片中的所有组件。参考描述如下：
                1. 布局结构
界面采用清晰的后台管理系统布局，左侧为导航栏，主体内容区域采用白色卡片式布局，数据展示清晰直观，整体布局简洁大方。

2. 颜色样式
系统使用蓝色作为主色调，搭配红色、绿色、橙色等辅助色彩，涉及到icon时采用红色党建风格。数据卡片使用纯白背景，图表采用蓝粉对比色展示数据，整体配色专业清爽。


4. 页面组件结构
    4.1 顶部导航
从左到右分别是：
系统名称：党建logo+智慧党建系统
组织概览、一级菜单等导航项，分别是一个页签，组织概览选中时为红色
用户信息及通知
    4.2 左侧菜单
数据概览
异常检测
数据分析
实时监管
数据管理等功能模块
排列紧凑，分别由对应icon和菜单名组成菜单项
    4.3 数据总览区
一行包括5个数据卡片，展示党委、党总支、党支部、党小组、党员等核心数据，5个卡片占满一行
每个卡片包含一个对应图标、标题和数值。卡片背景色为玻璃质感渐变色，色彩透明度较高，卡片本身带有阴影
    4.4 组织架构图
    标题为组织名单
以横向的流程图方式展示组织层级关系
每个流程图节点包含编号、名称
通过虚线连接表示上下级关系
主要内容包括：欧尚汽车党委事业部-长安福特党委-长安马自达党委-江北发动机厂党总支-渝北工厂党小组-研发系统党支部-凯程汽车党小组
    4.5 党员分析区
   一行分为两个主要容器，每个容器包括两个图表
左侧容器包括两个部分，左边为党员性别结构环形图，右边为学历分布环形图
右侧容器包括两个表格，左边党员年龄分布表，右侧是党员年龄表
图表配有清晰的图例和数据标注
    4.6 底部操作栏
保存进度、返回、提交等操作按钮，靠右侧
采用蓝色主按钮突出主要操作
"""

code_prompt = '''用react和antdesign、recharts尽量细致地还原这一页面,直接返回App.js代码，尽量考虑页面的协调性和精美性,不要修改css。页面描述如下：
                1. 布局结构
                    界面采用清晰的后台管理系统布局，左侧为导航栏，主体内容区域采用白色卡片式布局，数据展示清晰直观，整体布局简洁大方。

                    2. 颜色样式
                    系统使用蓝色作为主色调，搭配红色、绿色、橙色等辅助色彩。数据卡片使用纯白背景，图表采用蓝粉对比色展示数据，整体配色专业清爽。

                    3. 文案内容
                    内容以党建管理相关的数据统计为主，包括党委、党总支、党支部等组织架构数据，以及党员性别、学历、年龄等维度的统计分析。文案风格简洁规范。

                    4. 页面结构
                        4.1 顶部导航
                    系统logo及名称
                    组织概览、一级菜单等导航项
                    右上角用户信息及通知
                        4.2 左侧菜单
                    数据概览
                    异常检测
                    数据分析
                    实时监管
                    数据管理等功能模块
                        4.3 数据总览区
                    5个数据卡片，展示党委、党总支、党支部、党小组、党员等核心数据
                    每个卡片包含图标、标题和数值
                        4.4 组织架构图
                    以流程图方式展示组织层级关系
                    包含编号、名称等信息
                    通过虚线连接表示上下级关系
                        4.5 党员分析区
                    左侧党员性别结构环形图
                    中间学历分布环形图
                    右侧党员年龄、岗位分布条形图
                    图表配有清晰的图例和数据标注
                        4.6 底部操作栏
                    保存进度、返回、提交等操作按钮
                    采用蓝色主按钮突出主要操作'''

                    
def gpt_infer(image_url, prompt):
    base64_image = encode_image(image_url)
    client = OpenAI(
        api_key=token,
        base_url=url,
    )
    completion = client.chat.completions.create(
        # model="gpt-4o",
        model=model,
        messages=[
        {"role": "user", "content": [
                # {"type": "image_url", "image_url":f"data:image/jpg;base64,{base64_image}"},
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                        "url": f"data:image/jpg;base64,{base64_image}",
                        "detail": "high"
                    },}
        ]}
        ],
        # response_format={"type": "json_object"}
    )
    print(completion.usage)
    return completion.choices[0].message.content

def gpt_infer_no_image(prompt):
    client = OpenAI(
        api_key=token,
        base_url=url
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "user", "content": prompt}
        ],
        # response_format={"type": "json_object"}
    )
    print(completion.usage)
    return completion.choices[0].message.content

# file_url = 'images/152331_2497697.jpg'
# # result = gpt_infer(file_url, spec_prompt)
# result = gpt_infer_no_image(code_prompt)
# print(result)
