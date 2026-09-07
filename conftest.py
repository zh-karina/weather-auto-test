import pytest
import requests
import os
from dotenv import load_dotenv
import yaml

# ==================== 注册自定义标记 ====================
def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: 冒烟测试（核心功能）")
    config.addinivalue_line("markers", "regression: 回归测试（完整功能）")
    config.addinivalue_line("markers", "slow: 慢速测试（耗时长）")
    config.addinivalue_line("markers", "weather: 天气相关测试")

# ==================== 加载配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

with open(os.path.join(BASE_DIR, "data.yaml"), "r", encoding="utf-8") as f:
    TEST_DATA = yaml.safe_load(f)["test_cities"]

# ==================== 全局 Fixture（所有测试文件都能用） ====================

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


@pytest.fixture(scope="session")
def api_config():
    """所有 API 配置（整个会话只读取一次）"""
    print("\n🔴 [Session] 读取 API 配置...")
    return {
        "base_url": CONFIG["api"]["base_url"],
        "timeout": CONFIG["api"]["timeout"],
        "units": CONFIG["api"]["units"],
        "api_key": os.getenv("API_KEY")
    }


@pytest.fixture(scope="function")
def http_session():
    """每个测试创建一个新的 Session"""
    print("\n🔵 [Function] 创建 HTTP Session...")
    session = requests.Session()
    session.headers.update({"User-Agent": "pytest-test"})
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


@pytest.fixture
def sample_city():
    """示例城市"""
    return {"city": "London", "country": "GB"}


@pytest.fixture
def invalid_city():
    """无效城市（用于异常测试）"""
    return "ThisCityDoesNotExist12345"