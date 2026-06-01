import json
import os

SETTINGS_FILE = "data/settings.json"


def load_settings():
    """설정 불러오기 (config.py 우선 적용)"""
    try:
        import config
        return {
            "openai_api_key": getattr(config, "OPENAI_API_KEY", ""),
            "weather_api_key": getattr(config, "WEATHER_API_KEY", ""),
            "default_city": getattr(config, "DEFAULT_CITY", "Seoul")
        }
    except ImportError:
        pass

    if not os.path.exists(SETTINGS_FILE):
        return {"openai_api_key": "", "weather_api_key": "", "default_city": "Seoul"}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"openai_api_key": "", "weather_api_key": "", "default_city": "Seoul"}


def save_settings(settings):
    """설정 저장"""
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def get_openai_key():
    return load_settings().get("openai_api_key", "")


def get_weather_key():
    return load_settings().get("weather_api_key", "")


def get_default_city():
    return load_settings().get("default_city", "Seoul")
