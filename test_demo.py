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
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

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
@allure.story("查询城市天气")
@allure.severity(allure.severity_level.CRITICAL)
def test_weather_api():
    """测试：调用 OpenWeather 天气接口，检查返回结果"""
    
    url = f"{BASE_URL}/weather"
    timeout = CONFIG["api"]["timeout"]
    units = CONFIG["api"]["units"]
    
    log_info("=" * 60)
    log_info(f"开始执行测试，共 {len(TEST_DATA)} 个城市")
    log_info("=" * 60)
    
    total = len(TEST_DATA)
    passed = 0
    failed = 0
    results = []
    
    for idx, item in enumerate(TEST_DATA, 1):
        city = item["city"]
        country = item["country"]
        expected_min = item["expected_temp_min"]
        
        log_info(f"\n[{idx}/{total}] 测试城市：{city}, {country}")
        
        try:
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
            assert current_temp > expected_min, f"温度异常：{current_temp}°C < {expected_min}°C"
            
            humidity = data["main"]["humidity"]
            assert 0 <= humidity <= 100, f"湿度异常：{humidity}%"
            
            weather_desc = data["weather"][0]["description"]
            
            passed += 1
            results.append({
                "city": city,
                "status": "✅ PASSED",
                "temp": current_temp,
                "humidity": humidity,
                "weather": weather_desc,
                "elapsed_ms": elapsed
            })
            log_info(f"   ✅ {city} 测试通过！温度：{current_temp}°C，湿度：{humidity}%，天气：{weather_desc}")
            
        except AssertionError as e:
            failed += 1
            results.append({
                "city": city,
                "status": "❌ FAILED",
                "error": str(e)
            })
            log_error(f"   ❌ {city} 测试失败：{e}")
            
        except requests.exceptions.RequestException as e:
            failed += 1
            results.append({
                "city": city,
                "status": "❌ FAILED",
                "error": f"网络异常：{e}"
            })
            log_error(f"   ❌ {city} 网络异常：{e}")
    
    html_path = generate_html_report(results, total, passed, failed)
    
    log_info("=" * 60)
    log_info("📊 测试执行完毕！")
    log_info(f"   总计：{total} 个用例")
    log_info(f"   通过：{passed} 个 ✅")
    log_info(f"   失败：{failed} 个 ❌")
    log_info(f"   通过率：{round(passed/total*100, 1)}%")
    log_info(f"   日志文件：{LOG_FILE}")
    log_info(f"   HTML报告：{html_path}")
    log_info("=" * 60)
    
    if failed > 0:
        pytest.fail(f"有 {failed} 个用例失败")


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


# ==================== HTML 报告生成 ====================

def generate_html_report(results, total, passed, failed):
    """生成漂亮的 HTML 测试报告"""
    
    html_file = os.path.join(HTML_DIR, f"weather_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>天气接口自动化测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            padding: 40px;
        }}
        .header {{
            text-align: center;
            padding-bottom: 30px;
            border-bottom: 3px solid #f0f0f0;
        }}
        .header h1 {{ font-size: 28px; color: #2d3436; margin-bottom: 8px; }}
        .header .subtitle {{ color: #636e72; font-size: 14px; }}
        .summary {{
            display: flex;
            justify-content: center;
            gap: 40px;
            padding: 25px 0;
            flex-wrap: wrap;
        }}
        .summary-item {{
            text-align: center;
            padding: 10px 30px;
            border-radius: 12px;
            background: #f8f9fa;
            min-width: 120px;
        }}
        .summary-item .number {{ font-size: 32px; font-weight: bold; }}
        .summary-item .label {{ font-size: 14px; color: #636e72; margin-top: 4px; }}
        .summary-item.pass .number {{ color: #00b894; }}
        .summary-item.fail .number {{ color: #e17055; }}
        .summary-item.total .number {{ color: #0984e3; }}
        .summary-item.rate .number {{ color: #6c5ce7; }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0 25px 0;
        }}
        .progress-bar .fill {{
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(90deg, #00b894, #00cec9);
            width: {round(passed/total*100, 1)}%;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }}
        th {{
            background: #2d3436;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-pass {{ background: #d4edda; color: #155724; }}
        .badge-fail {{ background: #f8d7da; color: #721c24; }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
            color: #b2bec3;
            font-size: 13px;
        }}
        .footer .time {{ color: #636e72; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ 天气接口自动化测试报告</h1>
            <p class="subtitle">OpenWeather API · 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="summary">
            <div class="summary-item total">
                <div class="number">{total}</div>
                <div class="label">📋 总计用例</div>
            </div>
            <div class="summary-item pass">
                <div class="number">{passed}</div>
                <div class="label">✅ 通过</div>
            </div>
            <div class="summary-item fail">
                <div class="number">{failed}</div>
                <div class="label">❌ 失败</div>
            </div>
            <div class="summary-item rate">
                <div class="number">{round(passed/total*100, 1)}%</div>
                <div class="label">📈 通过率</div>
            </div>
        </div>
        <div class="progress-bar"><div class="fill"></div></div>
        <table>
            <thead>
                <tr><th>#</th><th>城市</th><th>状态</th><th>温度</th><th>湿度</th><th>天气</th><th>耗时</th></tr>
            </thead>
            <tbody>
'''
    
    for idx, r in enumerate(results, 1):
        if r["status"] == "✅ PASSED":
            html_content += f'''
                <tr>
                    <td>{idx}</td>
                    <td><strong>{r["city"]}</strong></td>
                    <td><span class="badge badge-pass">✅ PASSED</span></td>
                    <td>{r["temp"]}°C</td>
                    <td>{r["humidity"]}%</td>
                    <td>{r["weather"]}</td>
                    <td>{r["elapsed_ms"]}ms</td>
                </tr>
'''
        else:
            html_content += f'''
                <tr>
                    <td>{idx}</td>
                    <td><strong>{r["city"]}</strong></td>
                    <td><span class="badge badge-fail">❌ FAILED</span></td>
                    <td colspan="4" style="color:#e17055;">{r.get("error", "未知错误")}</td>
                </tr>
'''
    
    html_content += f'''
            </tbody>
        </table>
        <div class="footer">
            <p>📁 日志文件：{os.path.basename(LOG_FILE)}</p>
            <p class="time">报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
'''
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_file


if __name__ == "__main__":
    try:
        test_weather_api()
        test_weather_api_invalid_city()
        print("\n🎉 所有测试全部通过！查看 reports/html/ 获取详细报告")
    except AssertionError as e:
        print(f"\n⚠️ 有测试用例失败，请查看日志和报告")
    except Exception as e:
        print(f"\n❌ 执行出错：{e}")
