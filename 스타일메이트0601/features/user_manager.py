import json
import os

USERS_FILE = "data/users.json"
CURRENT_USER_FILE = "data/current_user.txt"


def get_user_data_path(username, filename):
    """사용자별 데이터 파일 경로 생성"""
    user_folder = os.path.join("data", "users", username)
    os.makedirs(user_folder, exist_ok=True)
    return os.path.join(user_folder, filename)


def load_users():
    """등록된 사용자 목록 불러오기"""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def add_user(username):
    """새 사용자 추가"""
    users = load_users()
    if username not in users:
        users.append(username)
        os.makedirs("data", exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
    return True


def set_current_user(username):
    """현재 로그인한 사용자 설정"""
    add_user(username)
    os.makedirs("data", exist_ok=True)
    with open(CURRENT_USER_FILE, "w", encoding="utf-8") as f:
        f.write(username)


def get_current_user():
    """현재 로그인한 사용자 가져오기"""
    if not os.path.exists(CURRENT_USER_FILE):
        return None
    try:
        with open(CURRENT_USER_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    except Exception:
        return None


def save_user_profile(username, profile):
    """사용자 프로필 저장 (무드, 체형, 선호 색상)"""
    file_path = get_user_data_path(username, "profile.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=4)


def load_user_profile(username=None):
    """사용자 프로필 불러오기"""
    if not username:
        username = get_current_user()
    if not username:
        return {}
    file_path = get_user_data_path(username, "profile.json")
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
