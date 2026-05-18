import json
import os


FILE_NAME = "schedule.json"


def load_schedule(date=None):
    """
    저장된 캘린더 기록을 불러오는 함수

    date가 None이면 전체 기록 반환
    date가 있으면 해당 날짜 기록만 반환
    """

    if not os.path.exists(FILE_NAME):
        return [] if date is None else None

    with open(FILE_NAME, "r", encoding="utf-8") as file:
        schedules = json.load(file)

    if date is None:
        return schedules

    for schedule in schedules:
        if schedule["date"] == date:
            return schedule

    return None


def save_schedule(date, outfit, memo):
    """
    날짜별 코디와 메모를 저장하는 함수

    date: "2026-05-11"
    outfit: ["후드티", "청바지"]
    memo: "친구 만남"
    """

    schedules = load_schedule()

    new_schedule = {
        "date": date,
        "outfit": outfit,
        "memo": memo
    }

    for i in range(len(schedules)):
        if schedules[i]["date"] == date:
            schedules[i] = new_schedule
            break
    else:
        schedules.append(new_schedule)

    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(schedules, file, ensure_ascii=False, indent=4)

    return new_schedule


def delete_schedule(date):
    """
    선택한 날짜의 기록을 삭제하는 함수

    삭제 성공: True
    삭제할 기록 없음: False
    """

    schedules = load_schedule()

    new_schedules = []
    deleted = False

    for schedule in schedules:
        if schedule["date"] == date:
            deleted = True
        else:
            new_schedules.append(schedule)

    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(new_schedules, file, ensure_ascii=False, indent=4)

    return deleted