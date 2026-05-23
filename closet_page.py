"""
StyleMate - 옷장 관리 모듈
기능: 옷 데이터 저장/불러오기/추가/삭제/수정 (JSON 기반)

저장 데이터 형식:
{
    "id":         "자동 생성 UUID",
    "name":       "검정 후드티",
    "category":   "상의",          ← 대분류
    "subcategory":"후드",           ← 세부 유형
    "color":      "블랙",
    "mood":       ["캐주얼", "힙"],
    "exclude_from_recommendation": false,
    "created_at": "2026-05-08 12:00:00"
}
"""

import json
import os
import uuid
from datetime import datetime

# ────────────────────────────────────────────────
# 상수: 카테고리 / 색상 / 무드
# ────────────────────────────────────────────────

# 대분류 → 세부 유형 매핑
CATEGORIES: dict[str, list[str]] = {
    "상의":      ["긴소매 티셔츠", "반소매 티셔츠", "셔츠", "블라우스", "니트/스웨터",
                  "맨투맨", "후드", "슬리브리스", "트레이닝 상의", "기타 상의"],
    "아우터":    ["가디건", "재킷", "집업/점퍼", "바람막이", "래더재킷", "트렌치코트",
                  "트위드재킷", "사파리재킷", "베스트", "숏코트", "하프코트", "롱코트",
                  "숏패딩", "롱패딩", "경량패딩", "퍼코트", "무스탕", "레인코트", "기타 아우터"],
    "바지":      ["데님 팬츠", "일자 팬츠", "슬랙스 팬츠", "와이드 팬츠", "스키니 팬츠",
                  "부츠컷 팬츠", "트레이닝 팬츠", "조거 팬츠", "숏 팬츠", "레깅스", "기타 하의"],
    "원피스/세트": ["미니원피스", "미디원피스", "롱원피스", "투피스", "점프수트", "기타 세트"],
    "스커트":    ["미니스커트", "미디스커트", "롱스커트", "기타 스커트"],
    "신발":      ["스니커즈", "스포츠화", "구두", "부츠/워커", "샌들/슬리퍼", "패딩/퍼 신발", "기타 신발"],
    "잡화":      ["모자", "스카프/머플러", "시계", "벨트", "아이웨어", "장갑", "기타 잡화"],
}

COLORS: list[str] = [
    "화이트", "아이보리", "그레이", "차콜", "블랙",
    "핑크", "스카이블루", "블루", "민트", "네이비",
    "베이지", "브라운", "그린", "카키",
    "레드", "버건디", "옐로우", "퍼플", "오렌지",
    "실버", "골드", "기타",
]

MOODS: list[str] = [
    "캐주얼", "러블리", "스트릿", "미니멀", "시크", "모던",
    "엘레강스", "프레피", "글램", "애슬레저", "레트로", "클래식",
    "비즈니스 캐주얼", "빈티지", "펑크", "기타",
]

# UI용 색상 hex 코드 (카드 색상 chip 표시에 사용)
COLOR_HEX: dict[str, str] = {
    "화이트": "#F8F8F8", "아이보리": "#FFFFF0", "그레이": "#9E9E9E",
    "차콜": "#455A64",   "블랙": "#212121",    "핑크": "#F48FB1",
    "스카이블루": "#81D4FA", "블루": "#1565C0", "민트": "#80CBC4",
    "네이비": "#1A237E",  "베이지": "#D7CCC8", "브라운": "#6D4C41",
    "그린": "#388E3C",    "카키": "#827717",   "레드": "#C62828",
    "버건디": "#6D1F35",  "옐로우": "#F9A825", "퍼플": "#6A1B9A",
    "오렌지": "#E65100",  "실버": "#B0BEC5",   "골드": "#F57F17",
    "기타": "#BDBDBD",
}

# UI용 카테고리 배지 배경색
CATEGORY_BADGE_COLOR: dict[str, str] = {
    "상의": "#FFE0E0",    "아우터": "#D6E4FF",  "바지": "#D6F5E3",
    "원피스/세트": "#F9D6FF", "스커트": "#FFF3D6", "신발": "#D6F5FF",
    "잡화": "#E8D6FF",
}

# ────────────────────────────────────────────────
# 내부 유틸 함수
# ────────────────────────────────────────────────

DATA_DIR = "data"


def _get_user_filepath(username: str) -> str:
    """사용자 이름 기반 JSON 파일 경로 반환"""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{username}_wardrobe.json")


def _read_json(filepath: str) -> dict:
    """JSON 파일 읽기. 파일 없으면 빈 구조 반환"""
    if not os.path.exists(filepath):
        return {"username": "", "clothes": []}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(filepath: str, data: dict) -> None:
    """dict를 JSON 파일에 저장"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _validate_item(item: dict) -> tuple[bool, str]:
    """
    옷 데이터 유효성 검사.

    Returns:
        (True, "")          : 유효
        (False, 오류메시지) : 유효하지 않음
    """
    # 필수 키 확인
    for key in ["name", "category", "color", "mood"]:
        if key not in item:
            return False, f"필수 항목 누락: '{key}'"

    # name
    if not isinstance(item["name"], str) or not item["name"].strip():
        return False, "'name'은 비어 있을 수 없습니다."

    # category: 대분류
    if item["category"] not in CATEGORIES:
        return False, f"'category'는 {list(CATEGORIES.keys())} 중 하나여야 합니다."

    # subcategory: 선택 항목 — 있으면 해당 대분류의 세부 유형인지 확인
    if "subcategory" in item and item["subcategory"]:
        valid_subs = CATEGORIES[item["category"]]
        if item["subcategory"] not in valid_subs:
            return False, f"'subcategory'는 [{', '.join(valid_subs)}] 중 하나여야 합니다."

    # color
    if item["color"] not in COLORS:
        return False, f"'color'는 정의된 색상 목록 중 하나여야 합니다."

    # mood
    if not isinstance(item["mood"], list) or len(item["mood"]) == 0:
        return False, "'mood'는 하나 이상의 태그를 포함한 리스트여야 합니다."
    for tag in item["mood"]:
        if not isinstance(tag, str) or not tag.strip():
            return False, "'mood' 태그는 비어 있지 않은 문자열이어야 합니다."
        if tag not in MOODS:
            return False, f"'{tag}'는 정의된 무드 목록에 없습니다. MOODS를 확인하세요."

    return True, ""


# ────────────────────────────────────────────────
# 핵심 기능 함수
# ────────────────────────────────────────────────

def load_clothes(username: str) -> list[dict]:
    """
    사용자의 옷장 데이터를 JSON 파일에서 불러옵니다.

    Args:
        username (str): 사용자 이름 (식별자)

    Returns:
        list[dict]: 옷 목록. 파일이 없으면 빈 리스트 반환.

    Example:
        >>> clothes = load_clothes("홍길동")
    """
    if not username or not username.strip():
        print("[오류] 사용자 이름이 비어 있습니다.")
        return []

    filepath = _get_user_filepath(username)
    data = _read_json(filepath)
    clothes = data.get("clothes", [])
    print(f"[불러오기 완료] '{username}'의 옷장 — {len(clothes)}개 항목")
    return clothes


def add_clothes(username: str, item: dict) -> bool:
    """
    옷장에 새 옷을 추가하고 JSON에 저장합니다.

    Args:
        username (str): 사용자 이름
        item (dict):
            - name        (str)       필수 | 옷 이름
            - category    (str)       필수 | 대분류  예) "상의"
            - subcategory (str)       선택 | 세부유형 예) "후드"
            - color       (str)       필수 | 색상    예) "블랙"
            - mood        (list[str]) 필수 | 무드 태그 예) ["캐주얼", "스트릿"]

    Returns:
        bool: 성공 True / 실패 False

    Example:
        >>> add_clothes("홍길동", {
        ...     "name": "검정 후드티", "category": "상의", "subcategory": "후드",
        ...     "color": "블랙", "mood": ["캐주얼", "스트릿"]
        ... })
        True
    """
    if not username or not username.strip():
        print("[오류] 사용자 이름이 비어 있습니다.")
        return False

    is_valid, error_msg = _validate_item(item)
    if not is_valid:
        print(f"[오류] 유효하지 않은 데이터: {error_msg}")
        return False

    filepath = _get_user_filepath(username)
    data = _read_json(filepath)
    data["username"] = username

    new_item = {
        "id":           str(uuid.uuid4()),
        "name":         item["name"].strip(),
        "category":     item["category"],
        "subcategory":  item.get("subcategory", "").strip(),
        "color":        item["color"],
        "mood":         [tag.strip() for tag in item["mood"]],
        "exclude_from_recommendation": item.get("exclude_from_recommendation", False),
        "created_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    data["clothes"].append(new_item)
    _write_json(filepath, data)
    print(f"[추가 완료] '{new_item['name']}' ({new_item['category']} · {new_item['subcategory']}) ID: {new_item['id']}")
    return True


def delete_clothes(username: str, item_id: str) -> bool:
    """
    옷장에서 특정 옷을 ID 기준으로 삭제합니다.

    Args:
        username (str): 사용자 이름
        item_id  (str): 삭제할 옷의 UUID

    Returns:
        bool: 성공 True / 해당 ID 없음·실패 False

    Example:
        >>> delete_clothes("홍길동", "abc-uuid-...")
        True
    """
    if not username or not username.strip():
        print("[오류] 사용자 이름이 비어 있습니다.")
        return False
    if not item_id or not item_id.strip():
        print("[오류] 삭제할 옷의 ID가 비어 있습니다.")
        return False

    filepath = _get_user_filepath(username)
    data = _read_json(filepath)

    target = next((c for c in data["clothes"] if c.get("id") == item_id), None)
    if target is None:
        print(f"[오류] ID '{item_id}'에 해당하는 옷을 찾을 수 없습니다.")
        return False

    data["clothes"] = [c for c in data["clothes"] if c.get("id") != item_id]
    _write_json(filepath, data)
    print(f"[삭제 완료] '{target['name']}' (ID: {item_id})")
    return True


def update_clothes(username: str, item_id: str, updated_fields: dict) -> bool:
    """
    옷 정보를 부분 수정합니다. 변경할 필드만 딕셔너리로 전달하면 됩니다.

    수정 가능한 필드: name, category, subcategory, color, mood, exclude_from_recommendation
    수정 불가 필드 : id, created_at

    Args:
        username       (str) : 사용자 이름
        item_id        (str) : 수정할 옷의 UUID
        updated_fields (dict): 변경할 필드와 값

    Returns:
        bool: 성공 True / 실패 False

    Example:
        >>> update_clothes("홍길동", "abc-uuid-...", {
        ...     "color": "그레이",
        ...     "mood": ["미니멀", "모던"]
        ... })
        True
    """
    if not username or not username.strip():
        print("[오류] 사용자 이름이 비어 있습니다.")
        return False
    if not item_id or not item_id.strip():
        print("[오류] 수정할 옷의 ID가 비어 있습니다.")
        return False
    if not updated_fields:
        print("[오류] 수정할 내용이 없습니다.")
        return False

    # 수정 불가 필드 차단
    for field in ("id", "created_at"):
        if field in updated_fields:
            print(f"[오류] '{field}' 필드는 수정할 수 없습니다.")
            return False

    filepath = _get_user_filepath(username)
    data = _read_json(filepath)

    target_index = next((i for i, c in enumerate(data["clothes"]) if c.get("id") == item_id), None)
    if target_index is None:
        print(f"[오류] ID '{item_id}'에 해당하는 옷을 찾을 수 없습니다.")
        return False

    # 기존 데이터에 변경 내용 병합 후 유효성 검사
    merged = {**data["clothes"][target_index], **updated_fields}
    if "mood" in merged and isinstance(merged["mood"], list):
        merged["mood"] = [t.strip() for t in merged["mood"]]

    is_valid, error_msg = _validate_item(merged)
    if not is_valid:
        print(f"[오류] 수정 후 데이터가 유효하지 않습니다: {error_msg}")
        return False

    merged["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["clothes"][target_index] = merged
    _write_json(filepath, data)
    print(f"[수정 완료] '{merged['name']}' (ID: {item_id})")
    return True


# ────────────────────────────────────────────────
# 필터링 보조 함수 (코디 추천 알고리즘 연동용)
# ────────────────────────────────────────────────

def filter_clothes(
    username: str,
    category: str = None,
    subcategory: str = None,
    color: str = None,
    mood_tags: list[str] = None,
    exclude_hidden: bool = True,
) -> list[dict]:
    """
    조건에 맞는 옷 목록을 반환합니다.
    코디 추천 알고리즘(이예빈 담당)에서 카테고리·무드 기준으로 호출합니다.

    Args:
        username      (str)       : 사용자 이름
        category      (str)       : 대분류 필터      예) "상의"
        subcategory   (str)       : 세부유형 필터     예) "후드"
        color         (str)       : 색상 필터        예) "블랙"
        mood_tags     (list[str]) : 무드 태그 필터 (하나라도 포함이면 통과)
        exclude_hidden (bool)     : True → 추천 제외 옷 숨김

    Returns:
        list[dict]: 조건에 맞는 옷 목록

    Example:
        >>> filter_clothes("홍길동", category="상의", mood_tags=["캐주얼"])
    """
    clothes = load_clothes(username)

    if exclude_hidden:
        clothes = [c for c in clothes if not c.get("exclude_from_recommendation", False)]
    if category:
        clothes = [c for c in clothes if c.get("category") == category]
    if subcategory:
        clothes = [c for c in clothes if c.get("subcategory") == subcategory]
    if color:
        clothes = [c for c in clothes if c.get("color") == color]
    if mood_tags:
        clothes = [c for c in clothes if any(t in c.get("mood", []) for t in mood_tags)]

    print(f"[필터 결과] {len(clothes)}개")
    return clothes


# ────────────────────────────────────────────────
# 테스트
# ────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("StyleMate 옷장 관리 모듈 테스트")
    print("=" * 55)
    USER = "테스트유저"

    print("\n▶ 옷 추가")
    add_clothes(USER, {"name": "검정 후드티",  "category": "상의",    "subcategory": "후드",        "color": "블랙",  "mood": ["캐주얼", "스트릿"]})
    add_clothes(USER, {"name": "와이드 데님",  "category": "바지",    "subcategory": "데님 팬츠",   "color": "블루",  "mood": ["캐주얼", "빈티지"]})
    add_clothes(USER, {"name": "화이트 셔츠",  "category": "상의",    "subcategory": "셔츠",        "color": "화이트","mood": ["미니멀", "비즈니스 캐주얼"]})
    add_clothes(USER, {"name": "숏패딩",       "category": "아우터",  "subcategory": "숏패딩",      "color": "네이비","mood": ["캐주얼"]})
    add_clothes(USER, {"name": "스니커즈",     "category": "신발",    "subcategory": "스니커즈",    "color": "화이트","mood": ["캐주얼", "스트릿"]})

    print("\n▶ 불러오기")
    for c in load_clothes(USER):
        print(f"  [{c['category']}·{c['subcategory']}] {c['name']} / {c['color']} / {c['mood']}")

    print("\n▶ 수정 (와이드 데님 색상 → 블랙)")
    clist = load_clothes(USER)
    update_clothes(USER, clist[1]["id"], {"color": "블랙", "mood": ["캐주얼", "시크", "빈티지"]})

    print("\n▶ 필터 (상의 + 캐주얼)")
    for c in filter_clothes(USER, category="상의", mood_tags=["캐주얼"]):
        print(f"  {c['name']} / {c['mood']}")

    print("\n▶ 삭제 (첫 번째 항목)")
    delete_clothes(USER, clist[0]["id"])
    print(f"  남은 항목: {len(load_clothes(USER))}개")

    print("\n▶ 유효성 검사 (잘못된 색상)")
    add_clothes(USER, {"name": "테스트", "category": "상의", "color": "빨강", "mood": ["캐주얼"]})