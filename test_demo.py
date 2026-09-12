# -*- coding: utf-8 -*-
import requests
import logging
import time
import os
from datetime import datetime
import yaml
from dotenv import load_dotenv
import pytest
import allure

# ==================== 获取当前脚本所在目录 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 强制创建目录（使用绝对路径） ====================
LOG_DIR = os.path.join(BASE_DIR, "reports", "logs")
HTML_DIR = os.path.join(BASE_DIR, "reports", "html")

# 确保目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
if not os.path.exists(HTML_DIR):
    os.makedirs(HTML_DIR)

# ==================== 加载配置 ====================
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 从环境变量读取 API Key（不写在代码里，避免泄露）
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.openweathermap.org/data/2.5")

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

with open(os.path.join(BASE_DIR, "data.yaml"), "r", encoding="utf-8") as f:
    TEST_DATA = yaml.safe_load(f)["test_cities"]

# ==================== 日志文件路径 ====================
LOG_FILE = os.path.join(LOG_DIR, f"test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


# ==================== 自定义日志函数 ====================
def log_info(msg):
    """输出 INFO 级别日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"{timestamp} - INFO - {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_error(msg):
    """输出 ERROR 级别日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"{timestamp} - ERROR - {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ==================== 测试用例 ====================

@allure.feature("天气接口")
@allure.story("查询单个城市天气")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("city, country", [
    ("London", "GB"),
    ("Beijing", "CN"),
    ("Tokyo", "JP"),
    ("Moscow", "RU"),
    ("Sydney", "AU"),
    ("Paris", "FR"),
    ("New York", "US"),
])
def test_weather_each_city(city, country):
    """测试：查询单个城市的天气"""
    url = f"{BASE_URL}/weather"
    timeout = CONFIG["api"]["timeout"]
    units = CONFIG["api"]["units"]

    log_info(f"\n测试城市：{city}, {country}")

    params = {
        "q": f"{city},{country}",
        "appid": API_KEY,
        "units": units
    }
    start_time = time.time()
    response = requests.get(url, params=params, timeout=timeout, verify=False)
    elapsed = round((time.time() - start_time) * 1000)

    log_info(f"   状态码：{response.status_code}，耗时：{elapsed}ms")

    assert response.status_code == 200, f"状态码异常：{response.status_code}"

    data = response.json()
    assert data["name"] == city, f"城市名不匹配：期望 {city}，实际 {data['name']}"
    assert data["sys"]["country"] == country, f"国家代码不匹配：期望 {country}，实际 {data['sys']['country']}"

    current_temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    weather_desc = data["weather"][0]["description"]

    log_info(f"   ✅ {city} 测试通过！温度：{current_temp}°C，湿度：{humidity}%，天气：{weather_desc}")


@allure.feature("天气接口")
@allure.story("查询无效城市")
@allure.severity(allure.severity_level.NORMAL)
def test_weather_api_invalid_city():
    """测试：查询不存在的城市，应该返回 404"""
    log_info("\n" + "=" * 60)
    log_info("执行异常场景测试：无效城市")

    url = f"{BASE_URL}/weather"
    invalid_city = CONFIG["test"]["invalid_city"]

    params = {
        "q": invalid_city,
        "appid": API_KEY,
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    log_info(f"   状态码：{response.status_code}")

    assert response.status_code == 404, f"期望 404，实际 {response.status_code}"

    data = response.json()
    assert data["cod"] == "404", f"期望 cod=404，实际 {data['cod']}"
    assert "city not found" in data["message"].lower(), f"错误信息不正确：{data['message']}"

    log_info("   ✅ 无效城市测试通过！")


@allure.feature("天气接口")
@allure.story("空城市名查询")
@allure.severity(allure.severity_level.NORMAL)
def test_weather_empty_city():
    """测试：查询空城市名，应该返回错误"""
    log_info("\n" + "=" * 60)
    log_info("执行异常场景测试：空城市名")

    url = f"{BASE_URL}/weather"
    params = {
        "q": "",
        "appid": API_KEY,
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    log_info(f"   状态码：{response.status_code}")

    assert response.status_code in [400, 404], f"期望 400 或 404，实际 {response.status_code}"

    log_info("   ✅ 空城市名测试通过！")


@allure.feature("天气接口")
@allure.story("特殊字符查询")
@allure.severity(allure.severity_level.NORMAL)
def test_weather_special_chars():
    """测试：查询包含特殊字符的城市名，应该返回错误"""
    log_info("\n" + "=" * 60)
    log_info("执行异常场景测试：特殊字符")

    url = f"{BASE_URL}/weather"
    params = {
        "q": "!@#$%^&*()",
        "appid": API_KEY,
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    log_info(f"   状态码：{response.status_code}")

    assert response.status_code == 404, f"期望 404，实际 {response.status_code}"

    log_info("   ✅ 特殊字符测试通过！")


@allure.feature("天气接口")
@allure.story("缺少API Key")
@allure.severity(allure.severity_level.CRITICAL)
def test_weather_missing_api_key():
    """测试：不传 API Key，应该返回 401"""
    log_info("\n" + "=" * 60)
    log_info("执行异常场景测试：缺少 API Key")

    url = f"{BASE_URL}/weather"
    params = {
        "q": "London,GB",
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    log_info(f"   状态码：{response.status_code}")

    assert response.status_code == 401, f"期望 401，实际 {response.status_code}"

    log_info("   ✅ 缺少 API Key 测试通过！")


@allure.feature("天气接口")
@allure.story("温度合理性校验")
@allure.severity(allure.severity_level.NORMAL)
def test_weather_temperature_range():
    """测试：检查返回的温度是否在合理范围内"""
    log_info("\n" + "=" * 60)
    log_info("执行业务逻辑测试：温度合理性")

    url = f"{BASE_URL}/weather"
    params = {
        "q": "London,GB",
        "appid": API_KEY,
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    assert response.status_code == 200

    data = response.json()
    temp = data["main"]["temp"]

    assert -90 <= temp <= 60, f"温度超出合理范围：{temp}°C"

    log_info(f"   ✅ 温度 {temp}°C 在合理范围内")


@allure.feature("天气接口")
@allure.story("天气描述非空")
@allure.severity(allure.severity_level.MINOR)
def test_weather_description_not_empty():
    """测试：检查返回的天气描述是否非空"""
    log_info("\n" + "=" * 60)
    log_info("执行业务逻辑测试：天气描述非空")

    url = f"{BASE_URL}/weather"
    params = {
        "q": "Beijing,CN",
        "appid": API_KEY,
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    assert response.status_code == 200

    data = response.json()
    weather_desc = data["weather"][0]["description"]

    assert weather_desc != "", "天气描述为空"
    assert len(weather_desc) > 0, "天气描述长度不够"

    log_info(f"   ✅ 天气描述：{weather_desc}")


@allure.feature("天气接口")
@allure.story("返回字段完整性")
@allure.severity(allure.severity_level.NORMAL)
def test_weather_response_fields():
    """测试：检查返回的 JSON 是否包含必要字段"""
    log_info("\n" + "=" * 60)
    log_info("执行业务逻辑测试：返回字段完整性")

    url = f"{BASE_URL}/weather"
    params = {
        "q": "Tokyo,JP",
        "appid": API_KEY,
        "units": CONFIG["api"]["units"]
    }

    response = requests.get(url, params=params, timeout=CONFIG["api"]["timeout"], verify=False)
    assert response.status_code == 200

    data = response.json()

    required_fields = ["name", "main", "weather", "sys", "wind"]
    for field in required_fields:
        assert field in data, f"缺少必要字段：{field}"

    assert "temp" in data["main"], "main 中缺少 temp"
    assert "humidity" in data["main"], "main 中缺少 humidity"
    assert "country" in data["sys"], "sys 中缺少 country"

    log_info("   ✅ 所有必要字段都存在")


# ==================== 生成 HTML 报告 ====================

def generate_html_report(results, total, passed, failed):
    """生成漂亮的 HTML 测试报告"""
    html_file = os.path.join(HTML_DIR, f"weather_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>天气接口自动化测试报告</title>
</head>
<body>
    <h1>天气接口自动化测试报告</h1>
    <p>总计：{total}，通过：{passed}，失败：{failed}</p>
</body>
</html>
'''

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_file
