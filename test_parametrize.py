import pytest
import requests

# ==================== 基础参数化 ====================

@pytest.mark.parametrize("city, country", [
    ("London", "GB"),
    ("Beijing", "CN"),
    ("Tokyo", "JP"),
    ("Paris", "FR"),
])
def test_weather_basic(api_key, base_url, http_session, city, country):
    """基础参数化：测试多个城市"""
    url = f"{base_url}/weather"
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == city
    
    print(f"\n✅ {city}, {country}: {data['main']['temp']}°C")


# ==================== 参数化 + 预期结果 ====================

@pytest.mark.parametrize("city, country, expected_temp_min", [
    ("London", "GB", -5),
    ("Beijing", "CN", -15),
    ("Tokyo", "JP", -5),
    ("Dubai", "AE", 10),    # 迪拜冬天也很热
])
def test_weather_with_expected(api_key, base_url, http_session, city, country, expected_temp_min):
    """参数化 + 预期温度校验"""
    url = f"{base_url}/weather"
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    
    data = response.json()
    current_temp = data["main"]["temp"]
    
    # 断言：当前温度必须大于预期最低温度
    assert current_temp > expected_temp_min, f"{city} 温度 {current_temp}°C 低于预期 {expected_temp_min}°C"
    
    print(f"\n✅ {city}: {current_temp}°C > {expected_temp_min}°C")


# ==================== 参数化 + 异常测试 ====================

@pytest.mark.parametrize("invalid_city, expected_status", [
    ("ThisCityDoesNotExist", 404),
    ("", 400),  # 空字符串返回 400
    ("abc123456", 404),
])
def test_invalid_cities(api_key, base_url, http_session, invalid_city, expected_status):
    """参数化：测试多个无效城市"""
    url = f"{base_url}/weather"
    params = {
        "q": invalid_city,
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    
    assert response.status_code == expected_status, f"{invalid_city}: 期望 {expected_status}，实际 {response.status_code}"
    
    print(f"\n✅ {invalid_city}: 返回 {response.status_code}")


# ==================== 参数化 + 标记组合 ====================

@pytest.mark.smoke
@pytest.mark.parametrize("city", ["London", "Beijing"])
def test_smoke_cities(api_key, base_url, http_session, city):
    """冒烟测试：只测核心城市"""
    url = f"{base_url}/weather"
    params = {
        "q": f"{city}",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    
    print(f"\n✅ {city}")


# ==================== 从 YAML 读取数据做参数化 ====================

@pytest.fixture
def all_cities_data(all_cities):
    """从 conftest.py 获取所有城市数据"""
    return all_cities


@pytest.mark.parametrize("city_data", [
    {"city": "London", "country": "GB"},
    {"city": "Beijing", "country": "CN"},
    {"city": "Tokyo", "country": "JP"},
])
def test_with_dict_data(api_key, base_url, http_session, city_data):
    """使用字典作为参数"""
    city = city_data["city"]
    country = city_data["country"]
    
    url = f"{base_url}/weather"
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": "metric"
    }
    
    response = http_session.get(url, params=params)
    assert response.status_code == 200
    
    print(f"\n✅ {city}, {country}")