from gen_code_with_spec import generate_code_single, derival_spec_single, generate_code_withspec
# import code_check.render
from code_debug import iterative_debug
import sys,os
import time,json
from utils.prompt import base_spec_propmt, code_prompt_v2,spc_dsx_v2
def batch_process_images(
    src_folder: str,
    code_path: str,
    port: int,
    wait_selector: str,
    dest_folder: str
):
    """
    对 src_folder 中的所有图片：
      1. 调用 generate_code_single 生成代码并写入 code_path
      2. 调用 iterative_debug 进行渲染+调试，截图保存在 dest_folder
      如果目标文件已存在，则跳过该图片
    """
    if not os.path.isdir(src_folder):
        print(f"⚠️ 源文件夹不存在：{src_folder}")
        return

    os.makedirs(dest_folder, exist_ok=True)

    for fname in os.listdir(src_folder):
        
        if not fname.lower().endswith((".json", ".jpg", ".jpeg")):
            continue

        base_name = os.path.splitext(fname)[0]
        spec_img_path = os.path.join(dest_folder, f"{base_name}.png")

        # 跳过已存在的截图
        if os.path.exists(spec_img_path):
            print(f"⏭️ {fname} 对应的截图已存在，跳过")
            continue
        time.sleep(1)
        spec_path = os.path.join(src_folder, fname)
        print(f"\n🔄 处理spec：{spec_path}")
        with open(spec_path, 'r', encoding='utf-8') as f:
            data = json.load(f)   # data 现在是一个 Python 字典（dict）
            spec = data['spec_res']
            img_path = data['image_path']

        # 1. 生成代码并写入 App.js
        try:
            code,spec = generate_code_withspec(img_path, spec,DEST_FOLDER,spc_dsx_v2, code_prompt_v2)
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            print("✅ 生成并写入代码成功")
        except Exception as e:
            print(f"⚠️ 生成或写入代码失败：{e}")
            continue
        # 2. 调用 iterative_debug，生成专属截图
        success = iterative_debug(
            code_path,
            port,
            wait_selector,
            screenshot=spec_img_path,
            log_dir=DEST_FOLDER
        )

        if success:
            print(f"✅ {fname} 调试并截图完成：{spec_img_path}")
        else:
            print(f"❌ {fname} 调试未成功，请查看 json 和 GPT 建议")

        # # 3. 对spec进行衍生
        # try:
        #     newcode = derival_spec_single(img_path,spec,DEST_FOLDER)
        #     with open(code_path, "w", encoding="utf-8") as f:
        #         f.write(newcode)
        #     print("✅ 衍生新spec并写入代码成功")
        # except Exception as e:
        #     print(f"⚠️ 衍生后的spec生成或写入代码失败：{e}")
        #     continue
        # screenshot_path = os.path.join(dest_folder, f"derived_{base_name}.png")
        # # 2. 调用 iterative_debug，生成专属截图
        # success = iterative_debug(
        #     code_path,
        #     port,
        #     wait_selector,
        #     screenshot=screenshot_path
        # )

        # if success:
        #     print(f"✅ {fname} 衍生后调试并截图完成：{screenshot_path}")
        # else:
        #     print(f"❌ {fname} 衍生后调试未成功，请查看 json 和 GPT 建议")


if __name__ == "__main__":
    SRC_FOLDER   = r"D:\xdw_test\myfolder\code-generation\data\all_spec_0516"
    # SRC_FOLDER = "/home/c50047709/cyn-workspace/images"
    DEST_FOLDER  = r"D:\xdw_test\myfolder\code-generation\data\sft_data_v2_qwen3235b"
    CODE_PATH    = r"D:\xdw_test\code-generation\code-generation\src\App.js"
    WAIT_SELECTOR = "#root"
    PORT         = 3001
    os.makedirs(DEST_FOLDER, exist_ok=True)
    batch_process_images(
        SRC_FOLDER,
        CODE_PATH,
        PORT,
        WAIT_SELECTOR,
        DEST_FOLDER
    )
