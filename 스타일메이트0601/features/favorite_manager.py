import json
import os
from features.user_manager import get_current_user, get_user_data_path

def get_favorite_file():
    """현재 사용자의 즐겨찾기 파일 경로"""
    username = get_current_user()
    if not username:
        return "data/favorite.json"
    return get_user_data_path(username, "favorite.json")

def load_favorite():
    """즐겨찾기 불러오기"""
    file_path = get_favorite_file()

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def add_favorite(outfit_data):
    """즐겨찾기 추가"""
    favorites = load_favorite()

    # 중복 검사
    for fav in favorites:
        if fav == outfit_data:
            return False, "이미 즐겨찾기에 등록된 코디입니다."

    favorites.append(outfit_data)

    file_path = get_favorite_file()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

    return True, "즐겨찾기에 저장되었습니다!"

def delete_favorite(index):
    """즐겨찾기 삭제"""
    favorites = load_favorite()

    if 0 <= index < len(favorites):
        favorites.pop(index)

        file_path = get_favorite_file()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(favorites, f, ensure_ascii=False, indent=4)

        return True

    return False

def analyze_style():
    """스타일 통계 분석"""
    favorites = load_favorite()

    style_count = {}
    color_count = {}
    mood_count = {}

    for fav in favorites:
        # 스타일 통계
        style = fav.get("style", "알 수 없음")
        style_count[style] = style_count.get(style, 0) + 1

        # 색상 통계
        outfit = fav.get("outfit", {})
        for part in ["top", "bottom", "outer"]:
            item = outfit.get(part)
            if item and isinstance(item, dict):
                color = item.get("color", "")
                if color:
                    color_count[color] = color_count.get(color, 0) + 1

        # 무드 통계
        mood = fav.get("mood", "")
        if mood:
            mood_count[mood] = mood_count.get(mood, 0) + 1

    return {
        "style_frequency": style_count,
        "color_frequency": color_count,
        "mood_frequency": mood_count,
        "total_favorites": len(favorites)
    }
