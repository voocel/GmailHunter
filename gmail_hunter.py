import json
from playwright.sync_api import sync_playwright
import time
import logging
from typing import Tuple, List
from pathlib import Path
from datetime import datetime
import argparse

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
                logging.info("选择月份...")
                month_select = page.locator("select").first
                month_select.select_option("1")
                time.sleep(0.5)

                logging.info("输入日期...")
                day_input = page.locator("input[name='day']")
                day_input.click()
                day_input.press("Backspace")
                day_input.type("1")
                time.sleep(0.5)

                logging.info("输入年份...")
                year_input = page.locator("input[name='year']")
                year_input.click()
                year_input.press("Backspace")
                year_input.type("2000")
                time.sleep(0.5)

                logging.info("选择性别...")
                gender_select = page.locator("select").nth(1)
                gender_select.select_option("2")
                time.sleep(0.5)
                
                # 保存填写后的页面状态
                page.screenshot(path="birthday_filled.png")
                logging.info("已完成生日信息填写")
                
                logging.info("6. 点击生日页面的下一步...")
                next_button = page.get_by_text("下一步").first
                next_button.click()
                time.sleep(1)
                
                logging.info("7. 等待用户名页面...")
                # 尝试查找单选按钮或用户名输入框
                try:
                    # 首先快速检查是否有单选按钮
                    radio_buttons = page.query_selector_all("input[type='radio']")
                    if radio_buttons:
                        logging.info(f"找到 {len(radio_buttons)} 个选项")
                        # 选择最后一个选项（创建自己的 Gmail 地址）
                        last_radio = radio_buttons[-1]
                        last_radio.click()
                        logging.info("已选择'创建您自己的 Gmail 地址'选项")
                        time.sleep(1)
                except Exception as e:
                    logging.info("未找到单选按钮，尝试直接查找用户名输入框")
                
                # 等待并填写用户名
                username_input = None
                selectors = [
                    "input[type='text']",
                    "input[name='Username']",
                    "input[type='email']"
                ]
                
                for selector in selectors:
                    try:
                        username_input = page.wait_for_selector(selector, timeout=3000)
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
                        "div[aria-live='assertive'], input[type='password']",
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

def check_usernames_from_file(checker: GmailChecker, filename: str) -> List[dict]:
    """从文件批量检查用户名"""
    results = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            usernames = [line.strip() for line in f if line.strip()]
            
        logging.info(f"从文件 {filename} 中读取到 {len(usernames)} 个用户名")
        
        for username in usernames:
            logging.info(f"\n{'='*30}\n开始检查用户名: {username}")
            status, message = checker.check_username(username)
            
            result = {
                "username": username,
                "available": status,
                "message": message,
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(result)
            
            # 打印单个结果
            print(f"\n检查结果:")
            print("-" * 30)
            print(f"用户名: {username}")
            print(f"状态: {'✅ 可用' if status else '❌ 不可用'}")
            print(f"详细信息: {message}")
            print(f"检查时间: {result['check_time']}")
            print("-" * 30)
            
    except Exception as e:
        logging.error(f"读取文件失败: {str(e)}")
        
    return results

def main():
    """主函数"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='Gmail 用户名可用性检查工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('username', nargs='?', help='要检查的用户名')
    group.add_argument('-f', '--file', help='包含用户名列表的文件路径')
    parser.add_argument('--headless', action='store_true', help='使用无头模式（不显示浏览器）')
    args = parser.parse_args()
    
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
    
    # 创建检查器实例
    checker = GmailChecker(headless=args.headless)
    
    # 保存结果的列表
    results = []
    
    # 根据参数执行检查
    if args.file:
        # 批量检查
        results = check_usernames_from_file(checker, args.file)
    else:
        # 单个用户名检查
        logging.info(f"开始检查用户名: {args.username}")
        status, message = checker.check_username(args.username)
        
        result = {
            "username": args.username,
            "available": status,
            "message": message,
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        results.append(result)
        
        # 打印结果
        print("\n检查结果:")
        print("-" * 30)
        print(f"用户名: {args.username}")
        print(f"状态: {'✅ 可用' if status else '❌ 不可用'}")
        print(f"详细信息: {message}")
        print(f"检查时间: {result['check_time']}")
        print("-" * 30)
    
    # 保存所有结果到 JSON 文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"results_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logging.info(f"结果已保存到 results_{timestamp}.json")

if __name__ == "__main__":
    main()
