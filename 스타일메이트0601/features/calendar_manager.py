import json
import os
from features.user_manager import get_current_user, get_user_data_path

def get_calendar_file():
    """현재 사용자의 캘린더 파일 경로"""
    username = get_current_user()
    if not username:
        return "data/calendar.json"
    return get_user_data_path(username, "calendar.json")

def load_schedule(date=None):
    """캘린더 데이터 불러오기"""
    file_path = get_calendar_file()

    if not os.path.exists(file_path):
        return [] if date is None else None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            schedules = json.load(f)
    except:
        schedules = []

    if date is None:
        return schedules

    for schedule in schedules:
        if schedule["date"] == date:
            return schedule

    return None

def save_schedule(date, outfit, mood, weather, memo):
    """캘린더 데이터 저장 (날씨 추가)"""
    schedules = load_schedule()

    new_schedule = {
        "date": date,
        "outfit": outfit,
        "mood": mood,
        "weather": weather,
        "memo": memo
    }

    for i in range(len(schedules)):
        if schedules[i]["date"] == date:
            schedules[i] = new_schedule
            break
    else:
        schedules.append(new_schedule)

    file_path = get_calendar_file()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=4)

    return new_schedule

def delete_schedule(date):
    """캘린더 기록 삭제"""
    schedules = load_schedule()
    new_schedules = [s for s in schedules if s["date"] != date]

    file_path = get_calendar_file()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(new_schedules, f, ensure_ascii=False, indent=4)

    return len(new_schedules) < len(schedules)

def get_dates_with_records():
    """기록이 있는 날짜 목록 반환"""
    schedules = load_schedule()
    return [s["date"] for s in schedules]
