import os
import random
import csv
import re
from datetime import datetime
from prompt import *
from qwen_api import qwen_inference, qwen_inference_no_image
from gpt_api import gpt_infer, gpt_infer_no_image
import json

def read_code_from_csv(file_path):
    with open('test.csv', newline='') as f:
        reader = csv.reader(f)
    for row in reader:
        original_code = row[0].replace('""', '"')
        print(original_code)
    return original_code

    
def generate_code_single(image_path, output_dir='/home/c50047709/cyn-workspace/code-generation/gen_code_result'):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec
    spec_res = gpt_infer(image_path, spec_v1_dsx)
    formatted_code_prompt = code_prompt_new.replace('{spec_input}', spec_res)
    print('✅ spec 获取成功，开始生成代码')

    # 2. 生成代码
    code_res = gpt_infer_no_image(formatted_code_prompt)

    # 3. 提取 ```jsx 和 ``` 之间的代码
    code_pattern = r'```jsx\n(.*?)\n```'
    match = re.search(code_pattern, code_res, re.DOTALL)
    if match:
        extracted_code = match.group(1).strip()
    else:
        extracted_code = 'Error: No valid code block found'

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

def derival_spec_single(image_path,spec, output_dir='/home/c50047709/cyn-workspace/code-generation/gen_code_result'):
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
    new_sepc = gpt_infer_no_image(formatted_derival_prompt)

    # 2. 生成代码
    formatted_code_prompt = code_prompt_new.replace('{spec_input}', new_sepc)
    print('✅ 衍生spec 获取成功，开始生成代码')    
    code_res = gpt_infer_no_image(formatted_code_prompt)

    # 3. 提取 ```jsx 和 ``` 之间的代码
    code_pattern = r'```jsx\n(.*?)\n```'
    match = re.search(code_pattern, code_res, re.DOTALL)
    if match:
        extracted_code = match.group(1).strip()
    else:
        extracted_code = 'Error: No valid code block found'

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_derival_code.json')

    data = {
        'old_spec_res': spec,
        'new_spec_res': new_sepc,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 衍生spec和衍生code数据已保存到 {json_path}')
    return extracted_code,spec

def generate_code_and_save_to_csv(folder_path, write_to_file=False):
    # 获取当前时间戳，用于命名CSV文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'spec_code_results_{timestamp}.csv'

    # 获取所有图像文件
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    # 读取现有CSV文件（如果存在），并将其内容存入字典中
    existing_data = {}
    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过表头
            for row in reader:
                existing_data[row[0]] = {'spec_result': row[1], 'code_result': row[2]}

    # 随机选择100张图像
    random_images = random.sample(image_files, 100)

    # 打开新的CSV文件以写入结果
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # 写入表头
        writer.writerow(['Image', 'Spec Result', 'Code Result'])

        # 循环处理每一张图像
        for image in random_images:
            image_path = os.path.join(folder_path, image)

            # 如果图像已经处理过，跳过
            if image_path in existing_data and existing_data[image_path]['spec_result'] != '':
                spec_res = existing_data[image_path]['spec_result']
                code_res = existing_data[image_path]['code_result']
                writer.writerow([image_path, spec_res, code_res])
                continue
            
            try:
                # 获取spec_res（如果未处理过）
                spec_res = gpt_infer(image_path, spec_prompt_new)

                # 生成代码
                formatted_code_prompt = code_prompt_new.replace("{spec_input}", spec_res)

                code_res = gpt_infer_no_image(formatted_code_prompt)
                
                # 使用正则表达式提取 ```jsx 和 ``` 之间的代码
                code_pattern = r'```jsx\n(.*?)\n```'
                match = re.search(code_pattern, code_res, re.DOTALL)

                if match:
                    extracted_code = match.group(1).strip()  # 提取并清理代码
                    
                    # 如果标志符为True，写入指定的文件
                    if write_to_file:
                        with open('/home/c50047709/cyn-workspace/code-generation/code-generation/src/App.js', 'w') as code_file:
                            code_file.write(extracted_code)
                else:
                    extracted_code = 'Error: No valid code block found'

                # 保存结果到CSV
                writer.writerow([image_path, spec_res, extracted_code])
            
            except Exception as e:
                # 打印错误信息，但继续处理下一个图像
                print(f"Error processing image {image_path}: {e}")
                # 如果有错误，依然写入该行，表示该图像未处理成功
                writer.writerow([image_path, 'Error', 'Error'])

    print(f"Results have been saved to '{csv_file}'.")

# 使用示例：
# folder_path = "/home/c50047709/cyn-workspace/images"
# generate_code_and_save_to_csv(folder_path, write_to_file=False)  # 控制是否写入App.js

# if __name__ == "__main__":
    
