import json
from playwright.sync_api import sync_playwright
import time
import logging
from typing import Tuple
from pathlib import Path
from datetime import datetime

class GmailChecker:
    def __init__(self, headless: bool = True):
        self.headless = headless
    
    def check_username(self, username: str) -> Tuple[bool, str]:
        """检查用户名是否可用"""
        playwright = None
        browser = None
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            
            logging.info("1. 访问注册页面...")
            page.goto(
                "https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp",
                wait_until="networkidle"
            )
            
            logging.info("2. 等待并填写姓名...")
            first_name_input = page.wait_for_selector("input[type='text']", timeout=5000)
            first_name_input.fill("John")
            
            last_name_input = page.locator("input[type='text']").nth(1)
            last_name_input.fill("Doe")
            
            logging.info("3. 点击第一个下一步...")
            next_button = page.get_by_text("下一步").first
            next_button.click()
            
            logging.info("4. 等待生日页面加载...")
            # 等待月份选择框出现
            page.wait_for_selector("select", timeout=5000)
            time.sleep(1)  # 等待页面完全加载
            
            logging.info("5. 填写生日信息...")
            try:
                # 1. 选择月份 (1月)
                logging.info("选择月份...")
                month_select = page.locator("select").first
                month_select.select_option("1")
                time.sleep(0.5)
                
                # 2. 直接输入日期 (1号)
                logging.info("输入日期...")
                day_input = page.locator("input[name='day']")
                day_input.click()
                day_input.press("Backspace")
                day_input.type("1")
                time.sleep(0.5)
                
                # 3. 直接输入年份 (2000年)
                logging.info("输入年份...")
                year_input = page.locator("input[name='year']")
                year_input.click()
                year_input.press("Backspace")
                year_input.type("2000")
                time.sleep(0.5)
                
                # 4. 选择性别 (男)
                logging.info("选择性别...")
                gender_select = page.locator("select").nth(1)
                gender_select.select_option("1")
                time.sleep(0.5)
                
                # 保存填写后的页面状态
                page.screenshot(path="birthday_filled.png")
                logging.info("已完成生日信息填写")
                
                logging.info("6. 点击生日页面的下一步...")
                next_button = page.get_by_text("下一步").first
                next_button.click()
                time.sleep(1)
                
                logging.info("7. 等待用户名页面...")
                # 等待用户名输入框，使用多个可能的选择器
                username_input = None
                selectors = [
                    "input[type='email']",
                    "input[name='Username']",
                    "input.whsOnd.zHQkBf"
                ]
                
                for selector in selectors:
                    try:
                        username_input = page.wait_for_selector(selector, timeout=5000)
                        if username_input:
                            logging.info(f"找到用户名输入框: {selector}")
                            break
                    except:
                        continue
                
                if not username_input:
                    page.screenshot(path="username_page_error.png")
                    return False, "无法找到用户名输入框"
                
                logging.info("8. 填写用户名...")
                username_input.fill(username)
                
                logging.info("9. 点击用户名页面的下一步...")
                next_button = page.get_by_text("下一步").first
                next_button.click()
                
                logging.info("10. 检查结果...")
                try:
                    # 等待可能的结果：要么是错误提示，要么是密码页面
                    result = page.wait_for_selector(
                        "div[aria-live='assertive'], input[type='password']",  # 错误提示 或 密码输入框
                        timeout=3000
                    )
                    
                    if result:
                        # 检查元素类型和属性
                        aria_live = result.get_attribute("aria-live")
                        
                        if aria_live == "assertive":
                            # 找到错误提示，说明用户名已被使用
                            error_text = result.text_content()
                            logging.info(f"发现错误提示: {error_text}")
                            return False, error_text or "用户名已被使用"
                        else:
                            # 找到密码输入框，说明用户名可用
                            logging.info("已进入密码设置页面")
                            return True, "用户名可用"
                                
                except Exception as e:
                    logging.error(f"检查结果时出错: {str(e)}")
                    page.screenshot(path="error_state.png")
                    return False, f"检查失败: {str(e)}"
                
            except Exception as e:
                logging.error(f"处理过程中出错: {str(e)}")
                page.screenshot(path="error_state.png")
                return False, f"处理失败: {str(e)}"
                
        except Exception as e:
            logging.error(f"检查失败: {str(e)}")
            if page:
                page.screenshot(path="error_state.png")
            return False, f"检查失败: {str(e)}"
        finally:
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

def main():
    """主函数"""
    # 设置日志
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"gmail_checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )
    
    # 检查用户名
    username = "firebase331q"
    
    logging.info(f"开始检查用户名: {username}")
    
    checker = GmailChecker(headless=False)  # 设为 False 以便观察
    status, message = checker.check_username(username)
    
    # 打印结果
    print("\n检查结果:")
    print("-" * 30)
    print(f"用户名: {username}")
    print(f"状态: {'✅ 可用' if status else '❌ 不可用'}")
    print(f"详细信息: {message}")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 30)
    
    # 保存结果
    result = {
        "username": username,
        "available": status,
        "message": message,
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
