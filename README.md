# 天气接口自动化测试框架 🌤️

基于 **Pytest + Requests + Allure + Jenkins** 的接口自动化测试框架

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pytest](https://img.shields.io/badge/Pytest-9.1.1-green)
![Allure](https://img.shields.io/badge/Allure-2.27.0-orange)
![Jenkins](https://img.shields.io/badge/Jenkins-2.568.3-red)

---

## 📖 项目介绍

本项目是一个完整的天气接口自动化测试框架，基于 OpenWeather API 实现。覆盖**正向测试、异常测试、业务逻辑测试**等多种场景，并集成了 **Allure 报告** 和 **Jenkins 持续集成**，实现了自动化测试的完整闭环。

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10 | 编程语言 |
| Pytest | 9.1.1 | 测试框架 |
| Requests | 2.31.0 | HTTP 客户端 |
| PyYAML | 6.0.1 | 数据驱动 |
| Allure | 2.27.0 | 测试报告 |
| Jenkins | 2.568.3 | 持续集成 |
| pytest-html | 4.1.1 | HTML 报告 |

---

## 📁 项目结构
weather_auto_test/
├── .env # 环境变量（API Key，不上传）
├── config.yaml # 配置文件
├── data.yaml # 测试数据
├── conftest.py # Pytest 共享配置
├── test_demo.py # 测试用例
├── send_email.py # 邮件发送脚本
├── requirements.txt # 依赖清单
└── reports/ # 测试报告目录
├── html/ # HTML 报告
├── logs/ # 日志文件
└── allure-results/ # Allure 原始数据

text

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/zh-karina/weather-auto-test.git
cd weather-auto-test
2. 安装依赖
bash
pip install -r requirements.txt
3. 配置环境变量
在项目根目录创建 .env 文件，填入你的 OpenWeather API Key：

text
API_KEY=你的API_KEY
BASE_URL=https://api.openweathermap.org/data/2.5
获取免费 API Key：https://home.openweathermap.org/api_keys

4. 运行测试
bash
# 基础运行
pytest test_demo.py -v

# 生成 HTML 报告
pytest test_demo.py -v --html=reports/html/report.html

# 生成 Allure 报告
pytest test_demo.py -v --alluredir=reports/allure-results
allure serve reports/allure-results
🧪 测试用例
本框架共包含 8 个测试用例，覆盖以下场景：

编号	用例名称	类型	说明
1	test_weather_api	正向	查询 7 个城市的天气
2	test_weather_api_invalid_city	异常	查询不存在的城市，验证 404
3	test_weather_empty_city	异常	查询空城市名
4	test_weather_special_chars	异常	查询特殊字符
5	test_weather_missing_api_key	异常	缺少 API Key，验证 401
6	test_weather_temperature_range	业务	温度合理性校验
7	test_weather_description_not_empty	业务	天气描述非空校验
8	test_weather_response_fields	业务	返回字段完整性校验
📊 测试报告
Allure 报告
可视化展示测试结果

按功能模块分类

支持趋势分析

详细步骤和失败原因

HTML 报告
轻量级报告

无需额外工具

自动生成

🔄 持续集成
Jenkins 配置
定时执行：每天凌晨 1:01 自动运行

构建步骤：

安装依赖
执行 Pytest 测试
生成 Allure 报告
发送邮件通知
邮件通知
构建完成后自动发送测试报告

邮件包含：构建状态、编号、执行时间、报告附件

📈 项目亮点
✅ 数据驱动：测试数据通过 YAML 管理，易于维护

✅ 配置分离：敏感信息通过 .env 管理，安全可靠

✅ 多场景覆盖：正向、异常、业务逻辑测试全覆盖

✅ 报告可视化：Allure + HTML 双报告

✅ 持续集成：Jenkins 定时执行 + 邮件通知

✅ 代码规范：Pytest 高级用法（fixture、参数化、标记）

🤝 贡献
欢迎提交 Issue 和 Pull Request！

📝 作者
zh-karina

GitHub: @zh-karina
