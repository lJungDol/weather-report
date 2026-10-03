"""
날씨 예보 프로그램 (Open-Meteo API)
- 사용자에게 지역을 입력받음 (기본값: 서울)
- 오늘, 내일, 모레까지 3일간의 날씨를 오전 6시, 오후 3시 기준으로 표시
- Open-Meteo API 사용 (인증키 불필요, 무료)
"""

import requests
from datetime import datetime, timedelta
import json
from typing import Optional, Tuple, Dict, Any

# 대한민국 주요 도시 위도 및 경도 좌표 매핑 테이블
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    "서울": (37.5665, 126.9780),
    "천안": (36.8151, 127.1139),
    "부산": (35.1796, 129.0756),
    "인천": (37.4563, 126.7052),
    "대구": (35.8714, 128.6014),
    "대전": (36.3504, 127.3845),
    "광주": (35.1595, 126.8526),
    "울산": (35.5384, 129.3114),
    "세종": (36.4800, 127.2890),
    "수원": (37.2636, 127.0286),
    "아산": (36.7898, 127.0018),
    "청주": (36.6424, 127.4890),
    "전주": (35.8242, 127.1480),
    "춘천": (37.8854, 127.7298),
    "강릉": (37.7519, 128.8761),
    "제주": (33.4996, 126.5312),
    "창원": (35.2280, 128.6811),
    "포항": (36.0190, 129.3435),
}

# WMO 날씨 코드 한국어 매핑
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "맑음",
    1: "주로 맑음",
    2: "구름 조금",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    56: "약한 어는 이슬비",
    57: "강한 어는 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    66: "약한 어는 비",
    67: "강한 어는 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "약한 눈 소나기",
    86: "강한 눈 소나기",
    95: "뇌우",
    96: "우박을 동반한 약한 뇌우",
    99: "우박을 동반한 강한 뇌우",
}


def get_weather_desc(code: int) -> str:
    """WMO 날씨 코드를 한글 설명 문자열로 변환합니다."""
    return WMO_WEATHER_CODES.get(code, "알 수 없음")


def get_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    """도시 이름을 받아 위도와 경도를 반환합니다.

    기본 사전에 정의되지 않은 도시는 Open-Meteo 지오코딩 API를 통해 조회합니다.
    """
    cleaned_name = city_name.strip()
    if cleaned_name in CITY_COORDINATES:
        return CITY_COORDINATES[cleaned_name]

    # '시', '군', '구' 제거 후 재시도 (예: '천안시' -> '천안')
    for suffix in ["시", "군", "구"]:
        if cleaned_name.endswith(suffix):
            prefix = cleaned_name[:-1]
            if prefix in CITY_COORDINATES:
                return CITY_COORDINATES[prefix]

    # Open-Meteo 지오코딩 API로 검색
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": cleaned_name,
            "count": 5,
            "language": "ko",
            "format": "json"
        }
        res = requests.get(geo_url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            if results:
                # 대한민국(KR) 결과 우선 선택
                for item in results:
                    if item.get("country_code") == "KR":
                        return round(item["latitude"], 4), round(item["longitude"], 4)
                # 없으면 첫 번째 결과 사용
                return round(results[0]["latitude"], 4), round(results[0]["longitude"], 4)
    except Exception as e:
        print(f"지오코딩 조회 중 오류 발생: {e}")

    return None


def fetch_weather_forecast(latitude: float, longitude: float, days: int = 3) -> Optional[Dict[str, Any]]:
    """Open-Meteo API를 호출하여 날씨 예보 데이터를 가져옵니다."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Seoul",
        "forecast_days": days
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API 요청 실패 (HTTP 상태 코드: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"네트워크 오류 발생: {e}")
        return None
