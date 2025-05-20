from openai import OpenAI
import os
import base64
import sys
from PIL import Image
from io import BytesIO
import httpx

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
url = 'https://mian.456478.xyz/v1'
# url = 'http://8.129.24.9:20000/v1'
# url = 'https://api.openai.com/v1/'
token = os.getenv("OPENAI_API_KEY", "填入token")
if not token:
    print("Error: 环境变量 OPENAI_API_KEY 未设置！")
    sys.exit(1)
model = os.getenv("model_choice", "o3")
if not model:
    print("Error: 环境变量 model_choice 未设置！")
    sys.exit(1)
# model = "qwen3-235b-a22b"
model = "o4-mini"
# model = "o3"
model = "claude-3-7-sonnet-thinking"
# model = "gpt-4.1"

#  base 64 编码格式
def encode_image(image_path: str, max_size: int = 480) -> str:
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

                    
def gpt_infer(image_url, prompt):
    base64_image = encode_image(image_url)
    headers = {'Content-Type': 'application/json'}
    insecure_http_client = httpx.Client(headers=headers, verify=False, follow_redirects=True)  # 同步版
    client = OpenAI(
        api_key=token,
        base_url=url,
        http_client=insecure_http_client
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
    # print(completion.usage)
    # return completion
    return completion.choices[0].message.content

def gpt_infer_no_image(prompt,model_used = model):
    headers = {'Content-Type': 'application/json'}
    # 客户端不再超时（交给网关处理）：
    insecure_http_client = httpx.Client(headers=headers, verify=False, follow_redirects=True, timeout=None)
    client = OpenAI(api_key=token, base_url=url, http_client=insecure_http_client)
    print('😃使用模型调用中',model_used)
    completion = client.chat.completions.create(
        model=model_used,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=70000,
        stream=True
    )

    result = []
    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            # print(delta.content, end="", flush=True)
            result.append(delta.content)

    print('\n👉 调用完毕')
    return "".join(result)


result = gpt_infer_no_image("我在测试能否联通你，请返回“成功联通”")
print(result)
