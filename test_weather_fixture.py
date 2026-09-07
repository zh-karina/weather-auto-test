import pytest
import requests
import os
from dotenv import load_dotenv
import yaml

# ==================== 加载配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

with open(os.path.join(BASE_DIR, "data.yaml"), "r", encoding="utf-8") as f:
    TEST_DATA = yaml.safe_load(f)["test_cities"]


# ==================== 定义 Fixture ====================

@pytest.fixture(scope="session")
def api_key():
    """API Key（整个会话只读取一次）"""
    print("\n🔴 [Session] 读取 API Key...")
    return os.getenv("API_KEY")


@pytest.fixture(scope="session")
def base_url():
    """API 基础地址（整个会话只读取一次）"""
    print("\n🔴 [Session] 读取 Base URL...")
    return CONFIG["api"]["base_url"]


@pytest.fixture(scope="function")
def http_session():
    """每个测试创建一个新的 Session"""
    print("\n🔵 [Function] 创建 HTTP Session...")
    session = requests.Session()
    yield session
    session.close()
    print("🔵 [Function] 关闭 HTTP Session...")


@pytest.fixture
def all_cities():
    """所有测试城市数据"""
    return TEST_DATA


@pytest.fixture
def first_city(all_cities):
    """第一个城市"""
    return all_cities[0]


# ==================== 测试用例 ====================

def test_first_city(api_key, base_url, http_session, first_city):
    """测试第一个城市"""
    city = first_city["city"]
    country = first_city["country"]
    
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


def test_london(api_key, base_url, http_session):
    """直接测试 London"""
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