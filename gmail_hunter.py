import json
from playwright.sync_api import sync_playwright
import time
import logging
from typing import Tuple, List
from datetime import datetime
import argparse
import sys
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import os
import random

class BrowserManager:
    """浏览器管理类"""
    def __init__(self, headless: bool = True):
        self.headless = headless
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--window-size=1280,800', '--disable-blink-features=AutomationControlled']
        )
        context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        return context.new_page()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'browser'): self.browser.close()
        if hasattr(self, 'playwright'): self.playwright.stop()

class GmailRegistration:
    """Gmail 注册流程处理"""
    @staticmethod
    def init_registration(page) -> None:
        """初始注册流程"""
        logging.info("🌐 正在访问注册页面...")
        page.goto("https://accounts.google.com/signup")
        time.sleep(2)

        logging.info("📝 开始填写注册信息...")
        GmailRegistration._fill_basic_info(page)
        GmailRegistration._fill_birthday_and_gender(page)
        # Gmail新版流程：生日后直接进入用户名输入页面
        logging.info("✅ 注册信息填写完成，已进入用户名输入页面")
    
    @staticmethod
    def _fill_basic_info(page) -> None:
        """填写基本信息"""
        logging.info("👤 正在填写基本信息...")
        page.fill("input[name='firstName']", "Test")
        page.fill("input[name='lastName']", "User")
        page.get_by_role("button", name="下一步").click()
        time.sleep(2)
        logging.info("✅ 基本信息填写完成")
    
    @staticmethod
    def _fill_birthday_and_gender(page) -> None:
        """填写生日和性别 - 支持新版Gmail Material Design UI"""
        logging.info("📅 正在填写生日信息...")
        time.sleep(2)

        # 1. 填写年份（普通input）
        try:
            page.fill("input[name='year']", "1995")
            time.sleep(0.5)
        except:
            logging.warning("⚠️ 年份填写可能失败")

        # 2. 点击月份combobox并选择
        try:
            logging.info("   选择月份...")
            # Gmail新UI使用 div[role='combobox']
            month_trigger = page.locator("div[role='combobox']").first
            month_trigger.click()
            time.sleep(1.5)
            # 选择第一个选项（1月）
            page.locator("li[role='option'], div[role='option']").first.click(force=True)
            time.sleep(1)  # 等待popup完全关闭
            logging.info("   ✅ 月份选择成功")
        except Exception as e:
            logging.warning(f"⚠️ 月份选择失败: {e}")

        # 3. 填写日期（普通input）
        try:
            page.fill("input[name='day']", "15")
            time.sleep(0.5)
        except:
            logging.warning("⚠️ 日期填写可能失败")

        logging.info("✅ 生日信息填写完成")

        # 4. 选择性别（第二个combobox）
        try:
            logging.info("👤 正在选择性别...")
            gender_trigger = page.locator("div[role='combobox']").nth(1)
            gender_trigger.click()
            time.sleep(1.5)  # 等待dropdown展开
            # 使用键盘操作选择：向下箭头2次，然后回车
            page.keyboard.press("ArrowDown")
            time.sleep(0.3)
            page.keyboard.press("ArrowDown")
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(1)
            logging.info("✅ 性别选择完成")
        except Exception as e:
            logging.warning(f"⚠️ 性别选择失败: {e}")

        page.get_by_role("button", name="下一步").click()
        time.sleep(2)
    
    @staticmethod
    def _select_gmail_option(page) -> None:
        """选择 Gmail 地址选项"""
        logging.info("📧 正在处理 Gmail 地址选项...")
        time.sleep(3)  # 增加等待时间确保页面加载完成
        success = page.evaluate("""() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const targetLabel = labels.find(label =>
                label.textContent.includes('创建您自己的 Gmail 地址') ||
                label.textContent.includes('Create your own Gmail')
            );
            if (targetLabel) {
                targetLabel.click();
                return true;
            }
            const radios = document.querySelectorAll('input[type="radio"]');
            if (radios.length >= 3) {
                radios[2].click();
                return true;
            }
            return false;
        }""")

        if success:
            logging.info("✅ Gmail 地址选项选择成功")
        else:
            logging.warning("⚠️ Gmail 地址选项选择可能失败")

        time.sleep(2)
        page.get_by_role("button", name="下一步").click()
        time.sleep(3)  # 等待用户名页面加载
        logging.info("✅ Gmail 选项处理完成")

class GmailChecker:
    """Gmail 用户名检查类"""
    def __init__(self, headless: bool = True):
        self.browser_manager = BrowserManager(headless)
    
    def check_usernames_batch(self, usernames: List[str]) -> List[Tuple[str, bool, str]]:
        """批量检查用户名"""
        results = []
        try:
            logging.info("🚀 开始批量检查用户名...")
            with self.browser_manager as page:
                GmailRegistration.init_registration(page)
                total = len(usernames)
                for i, username in enumerate(usernames, 1):
                    logging.info(f"📍 正在检查第 {i}/{total} 个用户名...")
                    results.append(self._check_single_username(page, username))
            logging.info("✅ 批量检查完成")
            return results
        except Exception as e:
            logging.error(f"❌ 批量检查失败: {str(e)}")
            return results
    
    def check_username(self, username: str) -> Tuple[bool, str]:
        """检查单个用户名"""
        results = self.check_usernames_batch([username])
        return (results[0][1], results[0][2]) if results else (False, "检查失败")
    
    def _check_single_username(self, page, username: str) -> Tuple[str, bool, str]:
        """检查单个用户名的可用性"""
        try:
            logging.info(f"🔍 正在检查: {username}")
            logging.info("🔍 查找用户名输入框...")
            # 使用更精确的选择器定位用户名输入框
            username_input = page.wait_for_selector("input[name='Username']", timeout=5000)
            if not username_input:
                logging.error(f"❌ {username}: 无法找到用户名输入框")
                return (username, False, "无法找到用户名输入框")

            # 添加随机延迟 (200ms-3s)
            delay = random.uniform(0.2, 3)
            logging.info(f"⏳ 等待 {delay:.1f} 秒...")
            time.sleep(delay)

            username_input.fill(username)
            time.sleep(0.5)  # 填写后稍等

            page.get_by_role("button", name="下一步").click()

            logging.info("⏳ 等待检查结果...")
            time.sleep(3)  # 增加等待时间让错误信息完全加载

            # 检查是否跳转到密码页面（表示用户名可用）
            if page.locator("input[type='password']").count() > 0:
                logging.info(f"✅ {username}: 可用")
                page.go_back()
                time.sleep(1)
                return (username, True, "用户名可用")

            # 查找真正的错误信息 - aria-live=polite 才是错误信息！
            error_divs = page.locator("div[aria-live='polite']").all()
            for div in error_divs:
                text = div.text_content().strip()
                # 排除无关信息
                if text and text != "简体中文" and "输入的字符数" not in text:
                    # 这是真正的错误信息
                    if len(text) > 5:  # 有实际内容
                        logging.info(f"❌ {username}: {text}")
                        return (username, False, text)

            # 如果没有明确的错误，可能是其他问题
            logging.info(f"⚠️  {username}: 状态未知")
            return (username, False, "状态未知")

        except Exception as e:
            logging.error(f"❌ {username}: {str(e)}")
            return (username, False, str(e))

class ConsoleUI:
    """控制台交互界面"""
    def __init__(self, headless: bool = False):
        self.checker = GmailChecker(headless=headless)

    def start(self):
        """启动交互式界面"""
        try:
            print("\n=== Gmail 用户名检查工具 ===")
            
            choices = [
                Choice("1", "1. 检查单个用户名"),
                Choice("2", "2. 从文件批量检查"),
                Choice("3", "3. 手动输入多个用户名"),
                Separator(),
                Choice("4", "4. 使用说明"),
                Choice("0", "0. 退出程序")
            ]
            
            choice = inquirer.select(
                message="请选择操作：",
                choices=choices,
                default=choices[0],
                pointer="➜",
                amark="✓"
            ).execute()
            
            self._handle_choice(choice)
            
        except KeyboardInterrupt:
            print("\n\n👋 收到退出信号，正在安全退出...")
            sys.exit(0)
    
    def _handle_choice(self, choice: str):
        if choice == "0":
            print("\n👋 感谢使用，再见！")
            sys.exit(0)
            
        elif choice == "1":
            username = inquirer.text(
                message="请输入要检查的用户名:",
                validate=lambda x: len(x) > 0,
                invalid_message="用户名不能为空"
            ).execute()
            
            if username:
                available, message = self.checker.check_username(username)
                print("\n" + "-" * 50)
                print(f"📊 检查结果:")
                print(f"{'✅ 可用' if available else '❌ 不可用'}: {username}")
                print(f"📝 原因: {message}")
                print("-" * 50)
                sys.exit(0)
                
        elif choice == "2":
            filepath = inquirer.filepath(
                message="请输入文件路径:",
                validate=lambda x: len(x) > 0,
                invalid_message="文件路径不能为空"
            ).execute()
            
            if filepath:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        usernames = [line.strip() for line in f if line.strip()]
                    if usernames:
                        results = self.checker.check_usernames_batch(usernames)
                        ResultHandler.save_and_show_results(results)
                    else:
                        print("\n❌ 文件为空")
                except Exception as e:
                    print(f"\n❌ 读取文件失败: {str(e)}")
                sys.exit(0)
                
        elif choice == "3":
            print("\n📝 请输入要检查的用户名列表（每行一个，输入空行结束）：")
            usernames = []
            while True:
                line = inquirer.text(
                    message="",
                    instruction="(输入空行结束)",
                ).execute()
                
                if not line:
                    break
                usernames.append(line)
                
            if usernames:
                results = self.checker.check_usernames_batch(usernames)
                ResultHandler.save_and_show_results(results)
                sys.exit(0)
                
        elif choice == "4":
            self._show_help()
            self.start()
            
        else:
            print("\n❌ 无效的选项，请重试")
            self.start()
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n=== 使用说明 ===")
        print("1. 单个检查：直接输入用户名进行检查")
        print("2. 文件批量检查：准备一个文本文件，每行一个用户名")
        print("3. 手动输入多个：每行输入一个用户名，输入空行结束")
        print("4. 结果会自动保存到 JSON 文件中")
        print("注意：请确保网络连接正常，必要时使用代理")

class ResultHandler:
    """结果处理类"""
    @staticmethod
    def save_and_show_results(results: List[Tuple[str, bool, str]]) -> None:
        logging.info("📊 正在保存检查结果...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 确保 result 目录存在
        os.makedirs('result', exist_ok=True)
        
        # 保存 JSON 结果
        json_file = os.path.join('result', f"results_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([{
                "username": username,
                "available": available,
                "message": message,
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            } for username, available, message in results], f, ensure_ascii=False, indent=2)
        logging.info(f"📄 详细结果已保存到: {json_file}")
        
        # 保存可用用户名
        available_usernames = [(u, m) for u, a, m in results if a]
        available_file = None
        if available_usernames:
            available_file = os.path.join('result', f"available_{timestamp}.txt")
            with open(available_file, 'w', encoding='utf-8') as f:
                for username, _ in available_usernames:
                    f.write(f"{username}\n")
            logging.info(f"💾 可用的用户名已保存到: {available_file}")
        
        # 显示统计结果
        total = len(results)
        available_count = len(available_usernames)
        ResultHandler._print_statistics(total, available_count, json_file, available_file)
    
    @staticmethod
    def _print_statistics(total: int, available: int, json_file: str, available_file: str = None) -> None:
        print("\n" + "-" * 50)
        print(f"📊 检查完成! 共检查 {total} 个用户名")
        print(f"✅ 可用: {available} 个")
        print(f"❌ 不可用: {total - available} 个")
        print("-" * 50)
        if available > 0 and available_file:
            print(f"\n💾 可用的用户名已保存到: {available_file}")
        print(f"📄 详细结果已保存到: {json_file}")

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Gmail 用户名可用性检查工具')
    parser.add_argument('username', nargs='?', help='要检查的用户名')
    parser.add_argument('-f', '--file', help='包含用户名列表的文件路径')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    
    args = parser.parse_args()
    setup_logging()
    
    try:
        checker = GmailChecker(headless=args.headless)
        
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f if line.strip()]
            results = checker.check_usernames_batch(usernames)
        elif args.username:
            available, message = checker.check_username(args.username)
            results = [(args.username, available, message)]
        else:
            ConsoleUI(headless=args.headless).start()
            return
            
        ResultHandler.save_and_show_results(results)
        
    except KeyboardInterrupt:
        print("\n\n👋 收到退出信号，正在安全退出...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")
        logging.error(f"程序出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
