import pytest
import time

# ==================== 这些 fixture 都来自 conftest.py ====================

@pytest.mark.smoke      # ← 冒烟测试标记
@pytest.mark.weather    # ← 天气测试标记
def test_london_weather(api_key, base_url, http_session):
    """测试 London 天气（冒烟测试）"""
    url = f"{base_url}/weather"
    params = {
        "q": "London,GB",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "London"
    
    print(f"\n✅ London: {data['main']['temp']}°C")


@pytest.mark.smoke      # ← 冒烟测试标记
@pytest.mark.weather    # ← 天气测试标记
def test_beijing_weather(api_key, base_url, http_session):
    """测试 Beijing 天气（冒烟测试）"""
    url = f"{base_url}/weather"
    params = {
        "q": "Beijing,CN",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Beijing"
    
    print(f"\n✅ Beijing: {data['main']['temp']}°C")


@pytest.mark.regression  # ← 回归测试标记
@pytest.mark.weather     # ← 天气测试标记
def test_all_cities_weather(api_config, http_session, all_cities):
    """测试所有城市天气（回归测试）"""
    print(f"\n📝 共 {len(all_cities)} 个城市")
    
    for item in all_cities:
        city = item["city"]
        country = item["country"]
        
        url = f"{api_config['base_url']}/weather"
        params = {
            "q": f"{city},{country}",
            "appid": api_config["api_key"],
            "units": api_config["units"]
        }
        
        response = http_session.get(url, params=params, timeout=api_config["timeout"])
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == city
        print(f"   ✅ {city}: {data['main']['temp']}°C")


@pytest.mark.slow        # ← 慢速测试标记
def test_slow_api_call(api_key, base_url, http_session):
    """模拟慢速测试（故意等待）"""
    print("\n🐢 慢速测试：等待 3 秒...")
    time.sleep(3)
    
    url = f"{base_url}/weather"
    params = {
        "q": "Tokyo,JP",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    
    print(f"\n✅ Tokyo: 测试完成")


@pytest.mark.regression
def test_invalid_city(api_key, base_url, http_session):
    """测试无效城市（回归测试）"""
    url = f"{base_url}/weather"
    params = {
        "q": "ThisCityDoesNotExist",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 404
    
    print("\n✅ 无效城市测试通过")