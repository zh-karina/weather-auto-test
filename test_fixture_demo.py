import pytest
import requests
import time
from datetime import datetime

# ==================== 基础 Fixture ====================

@pytest.fixture
def api_client():
    """准备 API 客户端（测试前执行）"""
    print("\n🔧 [Setup] 正在初始化 API 客户端...")
    base_url = "https://api.openweathermap.org/data/2.5"
    
    # 这里可以做一些初始化工作
    client = {
        "base_url": base_url,
        "timeout": 10,
        "session": requests.Session()
    }
    
    yield client  # ← 测试执行到这里
    
    # 测试结束后执行（teardown）
    print("\n🧹 [Teardown] 正在清理 API 客户端...")
    client["session"].close()


@pytest.fixture
def api_key():
    """返回 API Key（从环境变量读取，这里硬编码方便演示）"""
    return "abefa8035b045b2c1d861567212ec370"


@pytest.fixture
def test_cities():
    """返回测试数据"""
    return [
        {"city": "London", "country": "GB"},
        {"city": "Beijing", "country": "CN"},
        {"city": "Tokyo", "country": "JP"},
    ]


# ==================== 使用 Fixture 的测试用例 ====================

def test_weather_with_fixture(api_client, api_key, test_cities):
    """使用 fixture 测试天气接口"""
    
    print(f"\n📝 测试城市：{len(test_cities)} 个")
    
    for item in test_cities[:2]:  # 只测前两个
        city = item["city"]
        country = item["country"]
        
        url = f"{api_client['base_url']}/weather"
        params = {
            "q": f"{city},{country}",
            "appid": api_key,
            "units": "metric"
        }
        
        response = api_client["session"].get(url, params=params, timeout=api_client["timeout"])
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == city
        
        print(f"   ✅ {city}: {data['main']['temp']}°C")


def test_multiple_fixtures(api_client, api_key):
    """多个 fixture 组合使用"""
    
    print(f"\n📝 测试单个城市：London")
    url = f"{api_client['base_url']}/weather"
    params = {"q": "London,GB", "appid": api_key, "units": "metric"}
    
    response = api_client["session"].get(url, params=params)
    assert response.status_code == 200
    
    data = response.json()
    assert "weather" in data
    print(f"   ✅ London 天气：{data['weather'][0]['description']}")