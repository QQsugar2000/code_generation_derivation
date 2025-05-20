import os
import random
import csv
import re
from datetime import datetime
from utils.prompt import *
# from qwen_api import qwen_inference, qwen_inference_no_image
from utils.qwen_api import QwenClient
from utils.gpt_api import gpt_infer, gpt_infer_no_image
import json

qwen_code = QwenClient(
        api_key="EMPTY",
        base_url="http://10.44.53.178:8000/v1",
        model="qwen3-235b-a22b-fp8")

qwen_image = QwenClient(
        api_key="EMPTY",
        base_url="http://10.44.53.177:8000/v1",
        model="qwen2.5-vl-72b-instruct")

def read_code_from_csv(file_path):
    with open('test.csv', newline='') as f:
        reader = csv.reader(f)
    for row in reader:
        original_code = row[0].replace('""', '"')
        print(original_code)
    return original_code

def generate_code_withspec(image_path,spec, output_dir, spec_prompt: str, code_prompt: str):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec

    formatted_code_prompt = code_prompt.replace('{spec_input}', spec)

    # 2. 生成代码
    extracted_code = None

    for attempt in range(1, 4):
        # code_res = qwen_code.infer_text(formatted_code_prompt)
        code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_origin_code.json')

    data = {
        'image_path': image_path,
        'spec_res': spec,
        'code_response': code_res,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 数据已保存到 {json_path}')
    return extracted_code,spec

def generate_code_single(image_path, output_dir, spec_prompt: str, code_prompt: str):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec
    spec_res = qwen_image.infer_with_image(image_path, spec_prompt)
    # spec_res = gpt_infer(image_path, spec_prompt)
    match = re.search(r'```spec\n(.*?)\n```', spec_res, re.DOTALL)
    extracted_spec = match.group(1).strip()
    if extracted_spec:
        print('✅ spec 获取成功，开始生成代码')
    else:
        print(' spec 获取失败，开始生成代码')
        return None
    formatted_code_prompt = code_prompt.replace('{spec_input}', extracted_spec)

    # 2. 生成代码
    extracted_code = None

    for attempt in range(1, 4):
        # code_res = qwen_code.infer_text(formatted_code_prompt)
        code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_origin_code.json')

    data = {
        'image_path': image_path,
        'spec_res': spec_res,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 数据已保存到 {json_path}')
    return extracted_code,spec_res

def generate_code_withrag(image_path, output_dir):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec
    spec_res = qwen_image.infer_with_image(image_path, spc_dsx_v2)
    # spec_res = gpt_infer(image_path, spec_prompt)
    match = re.search(r'```spec\n(.*?)\n```', spec_res, re.DOTALL)
    extracted_spec = match.group(1).strip()
    formatted_code_prompt = code_prompt_v2.replace('{spec_input}', extracted_spec)
    formatted_code_prompt+=rag_prompt
    if extracted_spec:
        print('✅ spec 获取成功，开始生成代码')
    else:
        print(' spec 获取失败，开始生成代码')
        return None

    # 2. 生成代码
    extracted_code = None

    for attempt in range(1, 4):
        code_res = qwen_code.infer_text(formatted_code_prompt)
        # code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_origin_code.json')

    data = {
        'image_path': image_path,
        'spec_res': spec_res,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 数据已保存到 {json_path}')
    return extracted_code,spec_res

def derival_spec_single(image_path,spec, output_dir):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 新spec
    print('✅ 开始衍生新的spec')
    formatted_derival_prompt = spec_derive_dsx.replace('{spec_input}', spec)
    new_spec = qwen_code.infer_text(formatted_derival_prompt)
    # new_spec = gpt_infer_no_image(formatted_derival_prompt)
    match = re.search(r'```spec\n(.*?)\n```', new_spec, re.DOTALL)
    extracted_spec = match.group(1).strip()
    if extracted_spec:
        print('✅ 衍生spec 获取成功，开始生成代码')
    else:
        print(' spec 获取失败，开始生成代码')
        return None

    # 2. 生成代码
    formatted_code_prompt = code_prompt_new.replace('{spec_input}', extracted_spec)
    extracted_code = None

    # code_res = qwen_code.infer_text(formatted_code_prompt)
    
    # 3. 提取 ```jsx 和 ``` 之间的代码
    for attempt in range(1, 4):
        code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_derival_code.json')

    data = {
        'old_spec_res': spec,
        'new_spec_res': extracted_spec,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 衍生spec和衍生code数据已保存到 {json_path}')
    return extracted_code

# def generate_code_and_save_to_csv(folder_path, write_to_file=False):
#     # 获取当前时间戳，用于命名CSV文件
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     csv_file = f'spec_code_results_{timestamp}.csv'

#     # 获取所有图像文件
#     image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

#     # 读取现有CSV文件（如果存在），并将其内容存入字典中
#     existing_data = {}
#     if os.path.exists(csv_file):
#         with open(csv_file, mode='r') as file:
#             reader = csv.reader(file)
#             next(reader)  # 跳过表头
#             for row in reader:
#                 existing_data[row[0]] = {'spec_result': row[1], 'code_result': row[2]}

#     # 随机选择100张图像
#     random_images = random.sample(image_files, 100)

#     # 打开新的CSV文件以写入结果
#     with open(csv_file, mode='w', newline='') as file:
#         writer = csv.writer(file)
        
#         # 写入表头
#         writer.writerow(['Image', 'Spec Result', 'Code Result'])

#         # 循环处理每一张图像
#         for image in random_images:
#             image_path = os.path.join(folder_path, image)

#             # 如果图像已经处理过，跳过
#             if image_path in existing_data and existing_data[image_path]['spec_result'] != '':
#                 spec_res = existing_data[image_path]['spec_result']
#                 code_res = existing_data[image_path]['code_result']
#                 writer.writerow([image_path, spec_res, code_res])
#                 continue
            
#             try:
#                 # 获取spec_res（如果未处理过）
#                 spec_res = gpt_infer(image_path, spec_prompt_new)

#                 # 生成代码
#                 formatted_code_prompt = code_prompt_new.replace("{spec_input}", spec_res)

#                 code_res = gpt_infer_no_image(formatted_code_prompt)
                
#                 # 使用正则表达式提取 ```jsx 和 ``` 之间的代码
#                 code_pattern = r'```jsx\n(.*?)\n```'
#                 match = re.search(code_pattern, code_res, re.DOTALL)

#                 if match:
#                     extracted_code = match.group(1).strip()  # 提取并清理代码
                    
#                     # 如果标志符为True，写入指定的文件
#                     if write_to_file:
#                         with open('/home/c50047709/cyn-workspace/code-generation/code-generation/src/App.js', 'w') as code_file:
#                             code_file.write(extracted_code)
#                 else:
#                     extracted_code = 'Error: No valid code block found'

#                 # 保存结果到CSV
#                 writer.writerow([image_path, spec_res, extracted_code])
            
#             except Exception as e:
#                 # 打印错误信息，但继续处理下一个图像
#                 print(f"Error processing image {image_path}: {e}")
#                 # 如果有错误，依然写入该行，表示该图像未处理成功
#                 writer.writerow([image_path, 'Error', 'Error'])

#     print(f"Results have been saved to '{csv_file}'.")

# 使用示例：
# folder_path = "/home/c50047709/cyn-workspace/images"
# generate_code_and_save_to_csv(folder_path, write_to_file=False)  # 控制是否写入App.js

if __name__ == "__main__":
    extracted_code,spec = generate_code_withrag("/home/c50047709/cyn-workspace/code-generation/data/test_0506/9728_260702.jpg","/home/c50047709/cyn-workspace/code-generation/data/gen_code_withrag_0512")
    print(extracted_code)
#     prompt = """
# ### 1. UI整体描述
# 该UI是一个服务器管理界面，主要用于管理和监控服务器的状态。用户可以通过此界面查看服务器的详细信息，包括IP地址、管理状态、健康状态、型号、序列号、配置文件、所属组、标签等。此外，还可以进行添加服务器、创建分组等操作。该界面属于一个名为“FusionDirector”的产品，适用于IT运维人员或系统管理员在数据中心或企业环境中使用。

# ### 2. 页面构成
# - **头部区域**：包含产品Logo、语言切换按钮、搜索框、用户头像和帮助图标。
# - **侧边栏**：左侧为设备导航菜单，包含“所有服务器”及其子项列表。
# - **主体区域**：中间部分为服务器列表，显示服务器的详细信息和操作选项。
# - **底部区域**：底部有分页导航和每页显示条数的选择。

# ### 3. 视觉风格
# 页面整体采用简洁现代的设计风格，主要色调为白色和浅灰色，搭配蓝色和橙色作为点缀色。字体清晰易读，布局规整有序，符合专业软件的视觉标准。

# ### 4. 各个区域组件信息分述

# #### 头部区域
# - **组件类型**：导航栏
# - **承担的功能**：提供全局导航和快捷操作
# - **组件信息**：
#   - **产品Logo**：位于左上角，点击可返回首页。
#   - **语言切换按钮**：位于Logo右侧，提供中文和英文两种语言选择。
#   - **搜索框**：位于右侧，用于快速查找内容。
#   - **用户头像**：位于右上角，点击可进入用户设置页面。
#   - **帮助图标**：位于用户头像右侧，点击可获取帮助信息。

# #### 侧边栏
# - **组件类型**：垂直导航菜单
# - **承担的功能**：提供设备导航和分组视图的切换
# - **组件信息**：
#   - **设备导航**：默认选中状态，点击可展开子项列表。
#   - **分组视图**：未选中状态，点击可切换到分组视图模式。
#   - **所有服务器**：子项列表的第一项，点击可查看所有服务器信息。
#   - **G530_V01至G530_V15**：具体的服务器名称列表，点击可查看对应服务器的详细信息。

# #### 主体区域
# - **组件类型**：表格
# - **承担的功能**：展示服务器列表及其详细信息
# - **组件信息**：
#   - **标题栏**：包含“BMC IP”、“管理状态”、“健康状态”、“型号”、“序列号”、“配置文件”、“所属/组”、“标签”、“操作”等列标题。
#   - **数据行**：每行代表一个服务器，包含以下信息：
#     - **BMC IP**：例如“9.88.50.100”
#     - **管理状态**：例如“就绪”、“未管理”等，用不同颜色的圆点表示。
#     - **健康状态**：例如“正常”、“警告”、“紧急”等，用不同颜色的圆点表示。
#     - **型号**：例如“G560”
#     - **序列号**：例如“1234ad1234da”
#     - **配置文件**：例如“profile1”
#     - **所属/组**：例如“-”
#     - **标签**：例如“321dgdafsd”
#     - **操作**：包含“跳转到iBMC”、“KVM客户端”、“刷新”三个按钮。
#   - **顶部工具栏**：包含“全部类别”下拉菜单、搜索框、高级搜索按钮、添加服务器按钮、创建分组按钮、更多选项按钮等。

# #### 底部区域
# - **组件类型**：分页导航
# - **承担的功能**：提供分页浏览和每页显示条数的选择
# - **组件信息**：
#   - **总数**：显示当前列表的总记录数，例如“总数: 20”。
#   - **每页显示条数选择器**：默认显示10条，可选择其他数量。
#   - **分页导航**：包含页码按钮和跳转按钮，当前页码为5，总页数为2页。
#     """
#     formatted_code_prompt = code_prompt_v2.replace('{spec_input}', prompt)
#     print(formatted_code_prompt)
#     res = qwen_code.infer_text(formatted_code_prompt)
#     print(res)
    
