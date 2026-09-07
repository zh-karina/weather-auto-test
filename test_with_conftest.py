import pytest

# ==================== 这些 fixture 都来自 conftest.py ====================
# 不需要 import，pytest 会自动发现

def test_first_city_with_conftest(first_city, api_config, http_session):
    """使用 conftest.py 里的 fixture"""
    city = first_city["city"]
    country = first_city["country"]
    
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
    
    print(f"\n✅ {city}, {country}: {data['main']['temp']}°C")


def test_london_with_conftest(api_key, base_url, http_session):
    """使用 conftest.py 里的 fixture"""
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


def test_all_cities(all_cities, api_config, http_session):
    """测试所有城市"""
    print(f"\n📝 共 {len(all_cities)} 个城市")
    
    for item in all_cities[:3]:
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