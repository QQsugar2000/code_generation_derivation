import os
import random
import csv
from prompt import *
from qwen_api import qwen_inference, qwen_inference_no_image
from gpt_api import gpt_infer, gpt_infer_no_image

# 设置文件夹路径
folder_path = "/home/c50047709/cyn-workspace/images"
csv_file = 'spec_code_results_3.csv'

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

# 打开CSV文件以写入结果
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    
    # 如果CSV为空，则写入表头
    if file.tell() == 0:
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
            spec_res = qwen_inference(image_path, spec_prompt_new)

            # 生成代码
            formatted_code_prompt = code_prompt_new.replace("{spec_input}", spec_res)
            code_res = qwen_inference_no_image(formatted_code_prompt)
            
            # 保存结果到CSV
            writer.writerow([image_path, spec_res, code_res])
        
        except Exception as e:
            # 打印错误信息，但继续处理下一个图像
            print(f"Error processing image {image_path}: {e}")
            # 如果有错误，依然写入该行，表示该图像未处理成功
            writer.writerow([image_path, 'Error', 'Error'])

print("Results have been saved to 'spec_code_results.csv'.")
