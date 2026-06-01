import requests
import json

# OpenWeatherMap API (무료)
# API 키 발급: https://openweathermap.org/api

def get_weather(city="Seoul", api_key=None):
    """
    실시간 날씨 정보 가져오기

    Returns:
        {
            "temperature": 온도(°C),
            "weather": "맑음/흐림/비/눈",
            "description": "상세 날씨",
            "humidity": 습도(%),
            "wind_speed": 풍속(m/s),
            "city": 도시명
        }
    """

    if not api_key:
        return {
            "error": "날씨 API 키가 설정되지 않았습니다.",
            "temperature": None,
            "weather": None
        }

    try:
        # OpenWeatherMap API 호출
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # 섭씨 온도
            "lang": "kr"        # 한국어
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "error": f"날씨 정보를 가져올 수 없습니다. (코드: {response.status_code})",
                "temperature": None,
                "weather": None
            }

        data = response.json()

        # 날씨 코드를 한글로 변환
        weather_code = data["weather"][0]["main"].lower()
        weather_map = {
            "clear": "맑음",
            "clouds": "흐림",
            "rain": "비",
            "drizzle": "비",
            "snow": "눈",
            "thunderstorm": "천둥번개",
            "mist": "안개",
            "fog": "안개",
            "haze": "흐림"
        }

        weather_kr = weather_map.get(weather_code, "흐림")
        temperature = round(data["main"]["temp"])

        # 체감 날씨 판단
        if temperature >= 28:
            weather_kr = "더움"
        elif temperature <= 5:
            weather_kr = "추움"

        return {
            "temperature": temperature,
            "weather": weather_kr,
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "city": city,
            "icon": data["weather"][0]["icon"],
            "error": None
        }

    except requests.exceptions.Timeout:
        return {
            "error": "날씨 API 응답 시간 초과",
            "temperature": None,
            "weather": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"네트워크 오류: {str(e)}",
            "temperature": None,
            "weather": None
        }

    except Exception as e:
        return {
            "error": f"날씨 정보 처리 중 오류: {str(e)}",
            "temperature": None,
            "weather": None
        }

def get_weather_icon_emoji(weather):
    """날씨를 이모지로 변환"""
    weather_emoji = {
        "맑음": "☀️",
        "흐림": "☁️",
        "비": "🌧️",
        "눈": "❄️",
        "더움": "🔥",
        "추움": "🧊",
        "천둥번개": "⛈️",
        "안개": "🌫️"
    }

    return weather_emoji.get(weather, "🌤️")

# 한국 주요 도시 목록
KOREAN_CITIES = [
    "Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
    "Gwangju", "Ulsan", "Suwon", "Changwon", "Goyang",
    "Yongin", "Seongnam", "Cheongju", "Jeonju", "Cheonan",
    "Pohang", "Gimhae", "Jeju"
]

# 도시명 한글-영문 매핑
CITY_NAME_MAP = {
    "서울": "Seoul",
    "부산": "Busan",
    "인천": "Incheon",
    "대구": "Daegu",
    "대전": "Daejeon",
    "광주": "Gwangju",
    "울산": "Ulsan",
    "수원": "Suwon",
    "창원": "Changwon",
    "고양": "Goyang",
    "용인": "Yongin",
    "성남": "Seongnam",
    "청주": "Cheongju",
    "전주": "Jeonju",
    "천안": "Cheonan",
    "포항": "Pohang",
    "김해": "Gimhae",
    "제주": "Jeju"
}

def get_city_english_name(korean_city):
    """한글 도시명을 영문으로 변환"""
    return CITY_NAME_MAP.get(korean_city, korean_city)
