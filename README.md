# GmailHunter

一个简单的 Gmail 用户名可用性检查工具。

## ✨ 特性

- 🔍 支持单个和批量检查用户名
- 🤖 自动填写注册信息
- 🎯 准确识别用户名可用性
- 💾 自动保存检查结果
- 🌐 支持无头模式运行
- 📝 详细的日志记录
- 🎨 美观的交互式界面

## 🛠️ 安装

1. 克隆仓库并安装依赖：
```bash
git clone https://github.com/yourusername/GmailHunter.git
cd GmailHunter
pip install -r requirements.txt
playwright install chromium
```

2. 环境要求：
- Python 3.8+
- Chrome/Chromium 浏览器

## 📖 使用方法

### 命令行模式

```bash
# 检查单个用户名
python gmail_hunter.py username

# 从文件批量检查
python gmail_hunter.py -f usernames.txt

# 无头模式（不显示浏览器）
python gmail_hunter.py -f usernames.txt --headless
```

### 交互式模式

```bash
python gmail_hunter.py
```

## 📝 输出示例

```
🚀 开始批量检查用户名...
🌐 正在初始化浏览器...
📝 正在填写基本信息...
🔍 正在检查: test123
✅ test123: 可用
🔍 正在检查: test456
❌ test456: 此用户名已被使用

📊 检查完成! 共检查 2 个用户名
✅ 可用: 1 个
❌ 不可用: 1 个

💾 可用的用户名已保存到: available_xxx.txt
📄 详细结果已保存到: results_xxx.json
```

## ⚠️ 注意事项

- 建议使用代理以避免 IP 被限制
- 仅供学习和研究使用

## 🔧 常见问题

1. 如果遇到浏览器启动失败：
```bash
playwright install chromium --force
```

2. 如果遇到网络问题，可以：
- 检查网络连接
- 使用代理
- 增加等待时间

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
