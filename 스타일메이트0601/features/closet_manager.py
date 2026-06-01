import json
import os
from features.user_manager import get_current_user, get_user_data_path

CLOTHES_ICONS = {
    "상의": {"티셔츠": "👕", "셔츠": "👔", "후드티": "🧥", "맨투맨": "👚", "니트": "🧶"},
    "하의": {"청바지": "👖", "슬랙스": "👔", "반바지": "🩳", "치마": "👗", "레깅스": "🧘"},
    "아우터": {"자켓": "🧥", "코트": "🧥", "패딩": "🧥", "가디건": "🧶", "점퍼": "🧥"},
    "신발": {"운동화": "👟", "구두": "👞", "부츠": "🥾", "슬리퍼": "🩴", "샌들": "👡"},
    "악세서리": {"모자": "🎩", "가방": "👜", "목걸이": "📿", "시계": "⌚", "안경": "👓"}
}

def get_clothes_icon(category, type_name):
    """옷 종류에 맞는 아이콘 반환"""
    if category in CLOTHES_ICONS:
        return CLOTHES_ICONS[category].get(type_name, "👔")
    return "👔"

def get_clothes_file():
    """현재 사용자의 옷장 파일 경로"""
    username = get_current_user()
    if not username:
        return "data/clothes.json"
    return get_user_data_path(username, "clothes.json")

def load_clothes():
    """옷 데이터 불러오기"""
    file_path = get_clothes_file()

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def add_clothes(clothes_data):
    """옷 추가"""
    clothes = load_clothes()

    # 아이콘 자동 추가
    if "icon" not in clothes_data:
        clothes_data["icon"] = get_clothes_icon(
            clothes_data.get("category", ""),
            clothes_data.get("type", "")
        )

    clothes.append(clothes_data)

    file_path = get_clothes_file()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(clothes, f, ensure_ascii=False, indent=4)

    return True

def delete_clothes(index):
    """옷 삭제"""
    clothes = load_clothes()

    if 0 <= index < len(clothes):
        clothes.pop(index)

        file_path = get_clothes_file()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(clothes, f, ensure_ascii=False, indent=4)

        return True

    return False

def update_clothes(index, new_data):
    """옷 정보 수정"""
    clothes = load_clothes()

    if 0 <= index < len(clothes):
        clothes[index] = new_data

        file_path = get_clothes_file()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(clothes, f, ensure_ascii=False, indent=4)

        return True

    return False

def filter_clothes(category=None, color=None, mood=None, season=None):
    """옷 필터링"""
    clothes = load_clothes()
    result = []

    for item in clothes:
        if category and item.get("category") != category:
            continue
        if color and item.get("color") != color:
            continue
        if mood and mood not in item.get("mood", []):
            continue
        if season and season not in item.get("season", ["봄", "여름", "가을", "겨울"]):
            continue
        if item.get("excluded", False):
            continue

        result.append(item)

    return result

def get_available_clothes():
    """추천 가능한 옷만 반환"""
    clothes = load_clothes()
    return [item for item in clothes if not item.get("excluded", False)]
