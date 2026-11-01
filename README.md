# 天气接口自动化测试框架 🌤️

基于 **Pytest + Requests + Allure + Docker + Jenkins** 的接口自动化测试与持续集成框架

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pytest](https://img.shields.io/badge/Pytest-9.1.1-green)
![Allure](https://img.shields.io/badge/Allure-2.27.0-orange)
![Docker](https://img.shields.io/badge/Docker-Desktop-blue)
![Jenkins](https://img.shields.io/badge/Jenkins-2.568.3-red)

---

## 📖 项目介绍

本项目是一个完整的天气接口自动化测试系统，基于 OpenWeather API 实现。覆盖**正向测试、异常测试、业务逻辑测试**等多种场景。项目采用 **Docker** 进行测试环境隔离，并集成了 **Jenkins 持续集成流水线**，实现了从代码提交、自动构建、容器内测试、Allure 报告生成到邮件通知的完整自动化闭环，全程零人工干预。

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10 | 编程语言 |
| Pytest | 9.1.1 | 测试框架 |
| Requests | 2.31.0 | HTTP 客户端 |
| PyYAML | 6.0.1 | 数据驱动配置 |
| Allure | 2.27.0 | 可视化测试报告 |
| Docker | Latest | 测试环境容器化隔离 |
| Jenkins | 2.568.3 | CI/CD 持续集成流水线 |

---

## 📁 项目结构
```text
weather_auto_test/
├── .env                  # 环境变量（API Key，已加入 .gitignore，不上传）
├── Dockerfile            # Docker 镜像构建文件
├── config.yaml           # 接口超时、单位等配置文件
├── data.yaml             # 城市参数化测试数据
├── conftest.py           # Pytest 共享配置及 fixture
├── test_demo.py          # 核心测试用例
├── send_email.py         # 自动化邮件发送脚本
├── requirements.txt      # Python 依赖清单
└── reports/              # 测试结果及报告目录
    ├── html/             # HTML 摘要报告
    ├── logs/             # 运行日志
    └── allure-results/   # Allure 原始数据
🚀 快速开始
1. 克隆项目
bash
git clone https://github.com/zh-karina/weather-auto-test.git
cd weather-auto-test
2. 配置环境变量
在项目根目录创建 .env 文件，填入你的 OpenWeather API Key（注：当前免费 Key 需要等待约 10-20 分钟生效）：

text
API_KEY=你的API_KEY
BASE_URL=https://api.openweathermap.org/data/2.5
获取免费 API Key：OpenWeather 官网

3. 本地运行测试
bash
# 安装依赖
pip install -r requirements.txt

# 运行测试并生成 Allure 结果
pytest test_demo.py -v -s --alluredir=reports/allure-results

# 本地查看 Allure 报告
allure serve reports/allure-results
4. 使用 Docker 运行测试
bash
# 构建镜像 (无缓存模式)
docker build -t weather-test .

# 启动容器并运行测试 (通过数据卷将结果挂载到本地)
docker run --rm -e API_KEY="你的API_KEY" -v "%cd%\reports:/app/reports" weather-test
🧪 测试用例
本框架共包含 14 个测试用例，基于 Pytest 参数化驱动，覆盖以下核心场景：

测试模块	用例数量	说明
正向测试	7	参数化查询 London、Beijing、Tokyo 等 7 个核心城市的天气
异常测试	3	查询无效城市 (404)、查询空城市名 (400)、查询特殊字符 (404)
鉴权测试	1	缺少 API Key，验证返回 401 Unauthorized
业务逻辑	3	温度合理性校验、天气描述非空、返回 JSON 字段完整性校验
🔄 Jenkins 持续集成与工程化实践
本项目深度集成了 Jenkins 流水线，解决了多项 CI/CD 工程化难点：

安全凭据管理：使用 Jenkins Credentials 插件管理 API Key，在流水线中动态注入环境变量。控制台日志自动进行脱敏打码 (****)，防止敏感信息泄露。

Docker 构建优化：弃用 --no-cache，利用 Docker 本地缓存机制，将镜像构建及环境准备时间从数分钟压缩至 几秒内。

数据卷挂载：在容器运行命令中使用 -v 将容器内生成的 Allure 结果实时同步至宿主机，解决容器销毁后报告丢失的问题。

异常重试机制：针对调用第三方 API 时偶发的网络抖动或 SSL 握手断开问题（SSLEOFError），在代码层引入 Retry 重试机制，大幅降低测试误报率。

自动化通知：流水线末尾自动生成 HTML 摘要报告，并通过 SMTP 协议发送带附件的测试结果邮件，根据测试成功/失败状态精准推送。

📊 测试报告展示
Allure 报告：可视化展示测试结果、步骤耗时、失败原因，支持历史趋势分析。

HTML 报告：轻量级摘要，方便邮件直接附带发送。

日志记录：在 reports/logs 目录下生成每次运行的详细执行日志，便于排查问题。

📈 项目亮点
✅ 环境隔离：Docker 容器化保证测试环境的一致性
✅ 安全可靠：配置与敏感数据分离，Jenkins 凭据动态注入与脱敏
✅ 高效反馈：Docker 缓存优化 + Jenkins 自动触发，秒级构建
✅ 抗抖动强：完善的异常捕获与网络重试机制
✅ 闭环管理：测试 -> 报告 -> 邮件通知，一键自动完成

🤝 贡献
欢迎提交 Issue 和 Pull Request！

📝 作者
zh-karina
GitHub: @zh-karina
