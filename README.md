# 天气接口自动化测试框架 🌤️

基于 Pytest + Requests + Jenkins 的接口自动化测试框架

## 技术栈

- Python 3.10
- Pytest（测试框架）
- Requests（HTTP 客户端）
- PyYAML（数据驱动）
- Jenkins（持续集成）
- HTML 报告（pytest-html）

## 项目结构
weather_auto_test/
├── config.yaml # 配置文件
├── data.yaml # 测试数据
├── conftest.py # Pytest 共享配置
├── test_demo.py # 测试用例
├── send_email.py # 邮件发送脚本
└── requirements.txt # 依赖清单

text

## 快速开始

```bash
# 克隆项目
git clone https://github.com/zh-karina/weather-auto-test.git

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest test_demo.py -v --html=reports/html/report.html
持续集成
Jenkins 每天凌晨 1:01 自动执行测试，并发送邮件通知。

作者
zh-karina
