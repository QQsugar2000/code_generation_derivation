from playwright.sync_api import sync_playwright
import logging
import sys
from typing import List, Tuple

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("render.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def render_and_capture(
    url: str,
    screenshot_path: str,
    wait_selector: str = None
) -> Tuple[bool, List[str]]:
    """
    :param url: 页面地址
    :param screenshot_path: 截图保存路径
    :param wait_selector: 可选，渲染完成后才出现的元素选择器
    :return: (success, errors)
        success=True 则截图成功；False 则渲染或截图失败
        errors 为收集到的所有 console/pageerror 消息
    """
    errors: List[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        page = ctx.new_page()

        # 收集 console 日志
        # page.on("console", lambda msg: errors.append(f"[{msg.type.upper()}] {msg.text}"))
        # 收集未捕获的页面错误
        page.on("pageerror", lambda exc: errors.append(f"[PAGE ERROR] {exc}"))

        try:
            page.goto(url, wait_until="networkidle")
            page.wait_for_load_state("networkidle")

            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=5000)

            page.wait_for_timeout(2000)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"🔄 截图已保存：{screenshot_path}")

            # 如果有错误信息，视为“渲染警告”而非脚本崩溃，依然返回截图，但标记 success=False
            if errors:
                logging.error("捕获到前端错误：\n" + "\n".join(errors))
                return False, errors

            return True, []

        except Exception as e:
            # Python 层面的异常也算作失败
            logging.exception("渲染或截图过程出错：")
            # errors.append(f"[PYTHON EXCEPTION] {e}")
            return False, errors

        finally:
            browser.close()

if __name__ == "__main__":
    url = "http://localhost:3000"
    success, error_list = render_and_capture(url, "page.png", wait_selector="#root")

    if not success:
        print("❌ 渲染/截图过程中出现错误：")
        for err in error_list:
            print(err)
    else:
        print("✅ 渲染并截图成功，无前端错误。")
