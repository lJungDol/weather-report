"""
날씨 예보 프로그램 (Open-Meteo API)
- 사용자에게 지역을 입력받음 (기본값: 서울)
- 오늘, 내일, 모레까지 3일간의 날씨를 오전 6시, 오후 3시 기준으로 표시
- Open-Meteo API 사용 (인증키 불필요, 무료)
"""

import requests
from datetime import datetime, timedelta
import json
from typing import Optional, Tuple, Dict, Any, List

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
                for item in results:
                    if item.get("country_code") == "KR":
                        return round(item["latitude"], 4), round(item["longitude"], 4)
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


def display_weather_forecast(city: str, weather_data: Dict[str, Any]) -> None:
    """날씨 예보 데이터를 정해진 서식에 맞추어 화면에 출력합니다."""
    print("==================================================")
    print(f"📍 {city} 날씨 예보 (오전 6시 / 오후 3시 기준)")
    print("==================================================")

    hourly = weather_data.get("hourly", {})
    daily = weather_data.get("daily", {})
    hourly_times: List[str] = hourly.get("time", [])
    daily_times: List[str] = daily.get("time", [])

    day_labels = ["오늘", "내일", "모레"]

    for i, date_str in enumerate(daily_times):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        month_day_str = dt.strftime("%m.%d.")
        label_prefix = day_labels[i] if i < len(day_labels) else f"{i}일 후"

        print(f"\n📅 {label_prefix} ({month_day_str})")
        print("----------------------------------------")

        # 오전 06:00 데이터
        time_06 = f"{date_str}T06:00"
        if time_06 in hourly_times:
            idx_06 = hourly_times.index(time_06)
            code_06 = hourly["weather_code"][idx_06]
            temp_06 = round(hourly["temperature_2m"][idx_06])
            pop_06 = round(hourly["precipitation_probability"][idx_06])
            hum_06 = round(hourly["relative_humidity_2m"][idx_06])
            wind_06 = round(hourly["wind_speed_10m"][idx_06])

            print("🌅 오전 06:00")
            print(f"   날씨: {get_weather_desc(code_06)}")
            print(f"   기온: {temp_06} °C")
            print(f"   강수확률: {pop_06}%")
            print(f"   습도: {hum_06}%")
            print(f"   풍속: {wind_06} m/s")

        # 오후 15:00 데이터
        time_15 = f"{date_str}T15:00"
        if time_15 in hourly_times:
            idx_15 = hourly_times.index(time_15)
            code_15 = hourly["weather_code"][idx_15]
            temp_15 = round(hourly["temperature_2m"][idx_15])
            pop_15 = round(hourly["precipitation_probability"][idx_15])
            hum_15 = round(hourly["relative_humidity_2m"][idx_15])
            wind_15 = round(hourly["wind_speed_10m"][idx_15])

            print("\n🌇 오후 15:00")
            print(f"   날씨: {get_weather_desc(code_15)}")
            print(f"   기온: {temp_15} °C")
            print(f"   강수확률: {pop_15}%")
            print(f"   습도: {hum_15}%")
            print(f"   풍속: {wind_15} m/s")

        # 일일 최저 / 최고 기온
        if i < len(daily.get("temperature_2m_min", [])) and i < len(daily.get("temperature_2m_max", [])):
            min_temp = round(daily["temperature_2m_min"][i])
            max_temp = round(daily["temperature_2m_max"][i])
            print(f"\n🌡 일일 기온: 최저 {min_temp} °C / 최고 {max_temp} °C")

        print("\n==================================================")


def save_weather_to_json(city: str, weather_data: Dict[str, Any]) -> str:
    """조회한 날씨 예보 데이터를 JSON 파일로 저장합니다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weather_{city}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=4)
    return filename


def main() -> None:
    print("🌦 날씨 예보 프로그램 (Open-Meteo API)")
    print("--------------------------------------------------")
    print("오전 6시, 오후 3시 기준으로 3일간 날씨를 제공합니다.\n")

    input_city = input("날씨를 확인할 지역을 입력하세요 (기본값: 서울): ").strip()
    city = input_city if input_city else "서울"

    coords = get_coordinates(city)
    if not coords:
        print(f"❌ '{city}' 지역의 위치 정보를 찾을 수 없습니다. 지역명을 확인해주세요.")
        return

    lat, lon = coords
    print(f"📍 {city} (위도: {lat}, 경도: {lon}) 의 날씨 정보를 가져옵니다...\n")

    weather_data = fetch_weather_forecast(lat, lon, days=3)
    if not weather_data:
        print("❌ 날씨 정보를 가져오는 데 실패했습니다.")
        return

    display_weather_forecast(city, weather_data)

    save_choice = input("\n날씨 정보를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
    if save_choice == "y":
        filename = save_weather_to_json(city, weather_data)
        print(f"날씨 정보가 '{filename}'에 성공적으로 저장되었습니다.")


if __name__ == "__main__":
    main()
