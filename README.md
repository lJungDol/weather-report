# 🌦 날씨 예보 프로그램 (Weather Report)

Open-Meteo API를 활용하여 3일간의 날씨 예보(오전 6시, 오후 3시 기준)를 제공하는 파이썬 프로그램입니다.

- **GitHub 저장소:** [https://github.com/lJungDol/weather-report](https://github.com/lJungDol/weather-report)

---

## 📌 주요 기능
1. **지역별 날씨 조회**:
   - 사용자가 원하는 지역명을 입력받아 날씨를 조회합니다 (기본값: 서울).
   - 한국 주요 도시(서울, 천안, 부산, 인천, 대구, 대전 등) 좌표 내장 및 Open-Meteo 지오코딩 API를 통한 전세계/국내 지역 자동 탐색.
2. **3일간 예보 (오전 6시 / 오후 3시)**:
   - 오늘, 내일, 모레의 오전 06:00 및 오후 15:00 날씨 상태, 기온, 강수확률, 습도, 풍속 출력.
   - 일일 최저 기온 및 최고 기온 표시.
3. **날씨 데이터 JSON 파일 저장**:
   - `y` 입력 시 `weather_{지역명}_{YYYYMMDD}_{HHMMSS}.json` 파일로 저장.
4. **무료 오픈 API 연동**:
   - 별도의 API 키 발급 없이 사용 가능한 Open-Meteo Forecast API 및 Geocoding API 활용.

---

## 🛠 설치 및 실행 방법

### 1. 패키지 설치
```bash
pip install requests
```

### 2. 프로그램 실행
```bash
python API_weather.py
```

---

## 🌿 Git 브랜치 전략 및 사용 내역
본 프로젝트는 최소 5개 이상의 기능 브랜치를 활용하여 순차적으로 개발 및 병합(`--no-ff`)되었습니다.

1. `feature/coordinates`: 도시 좌표 사전 정의 및 지오코딩 조회 기능 구현
2. `feature/weather-api`: Open-Meteo API 연동 및 WMO 날씨 코드 매핑 로직 구현
3. `feature/forecast-display`: 오전 6시/오후 3시 기준 3일치 예보 출력 UI 포맷팅
4. `feature/json-export`: 날씨 예보 데이터 JSON 파일 저장 기능 추가
5. `feature/docs-and-refactor`: GitHub 저장소 링크 주석 추가, 문서화 및 예외 처리 강화
