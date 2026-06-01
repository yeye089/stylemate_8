import json
import os
import random

from features.closet_manager import filter_clothes, load_clothes
from features.favorite_manager import analyze_style, load_favorite
from features.user_manager import get_current_user, get_user_data_path, load_user_profile

# OpenAI 임포트 (없으면 fallback 사용)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 무드 유사 그룹 (비슷한 무드 추천에 사용)
SIMILAR_MOODS = {
    "힙":    ["스트릿", "캐주얼"],
    "포멀":  ["심플", "모던"],
    "페미닌": ["심플", "캐주얼"],
    "스트릿": ["힙", "캐주얼"],
    "캐주얼": ["심플", "스트릿"],
    "심플":  ["캐주얼", "포멀"],
    "빈티지": ["힙", "캐주얼"],
    "모던":  ["포멀", "심플"],
    "화려한": ["페미닌", "힙"],
}

# 날씨별 AI 멘트
WEATHER_MESSAGES = {
    "맑음":   "맑은 날씨예요! 좋아하는 스타일로 마음껏 입어보세요 ☀️",
    "흐림":   "흐린 날이네요. 가벼운 아우터 하나 챙기면 좋겠어요 ☁️",
    "비":     "비가 오고 있어요! 방수 소재나 어두운 색이 잘 어울려요 ☂️",
    "눈":     "눈이 와요! 따뜻하고 포근한 레이어드 코디가 최고예요 ❄️",
    "더움":   "날씨가 더워요! 얇고 시원한 소재가 좋겠어요 🌡️",
    "추움":   "날씨가 추워요! 따뜻한 레이어링을 추천드려요 🧥",
    "천둥번개": "천둥번개가 쳐요! 어둡고 무거운 색감도 멋스러워요 ⛈️",
    "안개":   "안개가 꼈네요. 차분한 컬러로 코디해보는 건 어때요? 🌫️",
}

client = None


def init_openai(api_key=None):
    """OpenAI API 초기화"""
    global client
    if not OPENAI_AVAILABLE:
        return False
    if not api_key:
        from features.settings_manager import get_openai_key
        api_key = get_openai_key()
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            return True
        except Exception:
            client = None
    return False


def get_feedback_file():
    username = get_current_user()
    if not username:
        return "data/feedback.json"
    return get_user_data_path(username, "feedback.json")


def load_feedback_data():
    file_path = get_feedback_file()
    if not os.path.exists(file_path):
        return {"liked": [], "disliked": []}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"liked": [], "disliked": []}


def save_feedback(outfit_data, is_liked):
    """피드백 저장"""
    import datetime
    feedback = load_feedback_data()
    item = {
        "outfit": outfit_data,
        "timestamp": datetime.datetime.now().isoformat()
    }
    if is_liked:
        feedback["liked"].append(item)
    else:
        feedback["disliked"].append(item)
    feedback["liked"] = feedback["liked"][-50:]
    feedback["disliked"] = feedback["disliked"][-50:]

    file_path = get_feedback_file()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(feedback, f, ensure_ascii=False, indent=4)


def analyze_user_preference():
    """사용자 선호도 분석 (피드백 + 즐겨찾기 + 프로필)"""
    feedback = load_feedback_data()
    stats = analyze_style()
    profile = load_user_profile()

    liked_styles = {}
    liked_colors = {}
    liked_moods = {}

    # 프로필 기반 초기값
    for mood in profile.get("preferred_moods", []):
        liked_moods[mood] = liked_moods.get(mood, 0) + 2
    for color in profile.get("favorite_colors", []):
        liked_colors[color] = liked_colors.get(color, 0) + 2

    # 즐겨찾기 기반
    for key, cnt in stats.get("style_frequency", {}).items():
        liked_styles[key] = liked_styles.get(key, 0) + cnt
    for key, cnt in stats.get("mood_frequency", {}).items():
        liked_moods[key] = liked_moods.get(key, 0) + cnt
    for key, cnt in stats.get("color_frequency", {}).items():
        liked_colors[key] = liked_colors.get(key, 0) + cnt

    # 피드백 기반
    for item in feedback.get("liked", []):
        outfit = item.get("outfit", {})
        style = outfit.get("style", "")
        mood = outfit.get("mood", "")
        if style:
            liked_styles[style] = liked_styles.get(style, 0) + 1
        if mood:
            liked_moods[mood] = liked_moods.get(mood, 0) + 1
        for part in ["top", "bottom", "outer"]:
            piece = outfit.get("outfit", {}).get(part, {})
            if isinstance(piece, dict):
                color = piece.get("color", "")
                if color:
                    liked_colors[color] = liked_colors.get(color, 0) + 1

    disliked_styles = {}
    disliked_colors = {}
    for item in feedback.get("disliked", []):
        outfit = item.get("outfit", {})
        style = outfit.get("style", "")
        if style:
            disliked_styles[style] = disliked_styles.get(style, 0) + 1
        for part in ["top", "bottom", "outer"]:
            piece = outfit.get("outfit", {}).get(part, {})
            if isinstance(piece, dict):
                color = piece.get("color", "")
                if color:
                    disliked_colors[color] = disliked_colors.get(color, 0) + 1

    return {
        "liked_styles": liked_styles,
        "liked_colors": liked_colors,
        "liked_moods": liked_moods,
        "disliked_styles": disliked_styles,
        "disliked_colors": disliked_colors,
        "favorite_stats": stats,
        "profile": profile,
    }


def _get_season(date):
    if not date:
        return None
    try:
        month = int(date.split("-")[1])
        if month in [3, 4, 5]:
            return "봄"
        elif month in [6, 7, 8]:
            return "여름"
        elif month in [9, 10, 11]:
            return "가을"
        else:
            return "겨울"
    except Exception:
        return None


def _score_item(item, preferred_colors, preferred_moods, body_type):
    """옷 아이템 점수 계산"""
    score = 0
    color = item.get("color", "")
    moods = item.get("mood", [])

    if color in preferred_colors:
        score += preferred_colors[color] * 2
    for m in moods:
        if m in preferred_moods:
            score += preferred_moods[m]

    # 체형 보너스
    item_type = item.get("type", "")
    if body_type == "슬림":
        if any(kw in item_type for kw in ["오버핏", "루즈"]):
            score += 1
    elif body_type == "볼륨":
        if any(kw in item_type for kw in ["치마", "슬랙스"]):
            score += 1

    return score


def recommend_outfit_simple(weather=None, mood=None, date=None, also_recommend_similar=True):
    """룰 기반 추천 (OpenAI 없을 때 / fallback)"""
    season = _get_season(date)
    prefs = analyze_user_preference()
    profile = prefs.get("profile", {})
    body_type = profile.get("body_type", "보통")

    # 무드 결정 (우선순위: 입력값 > 즐겨찾기 학습 > 프로필)
    if mood is None:
        if prefs["liked_moods"]:
            mood = max(prefs["liked_moods"].items(), key=lambda x: x[1])[0]
        elif profile.get("preferred_moods"):
            mood = profile["preferred_moods"][0]

    # 유사 무드 리스트
    similar = SIMILAR_MOODS.get(mood, []) if mood else []

    def pick_best(items, preferred_colors, preferred_moods):
        if not items:
            return None
        scored = [(i, _score_item(i, preferred_colors, preferred_moods, body_type)) for i in items]
        scored.sort(key=lambda x: x[1], reverse=True)
        # 상위 3개 중 랜덤 (다양성 확보)
        top = scored[:3]
        return random.choice(top)[0]

    liked_colors = prefs["liked_colors"]
    liked_moods = prefs["liked_moods"]

    tops = filter_clothes(category="상의", mood=mood, season=season)
    bottoms = filter_clothes(category="하의", mood=mood, season=season)
    outers = filter_clothes(category="아우터", mood=mood, season=season)

    if not tops:
        tops = filter_clothes(category="상의", season=season) or filter_clothes(category="상의")
    if not bottoms:
        bottoms = filter_clothes(category="하의", season=season) or filter_clothes(category="하의")
    if not outers:
        outers = filter_clothes(category="아우터", season=season) or filter_clothes(category="아우터")

    outfit = {}
    top = pick_best(tops, liked_colors, liked_moods)
    bottom = pick_best(bottoms, liked_colors, liked_moods)

    if top:
        outfit["top"] = top
    if bottom:
        outfit["bottom"] = bottom
    if outers and (weather in ["비", "눈", "추움", "흐림"] or season in ["가을", "겨울"]):
        outer = pick_best(outers, liked_colors, liked_moods)
        if outer:
            outfit["outer"] = outer

    # 유사 무드 추가 추천
    similar_recommendations = []
    if also_recommend_similar and mood and similar:
        for sim_mood in similar[:2]:
            sim_tops = filter_clothes(category="상의", mood=sim_mood, season=season)
            sim_bottoms = filter_clothes(category="하의", mood=sim_mood, season=season)
            if sim_tops and sim_bottoms:
                sim_outfit = {}
                t = pick_best(sim_tops, liked_colors, liked_moods)
                b = pick_best(sim_bottoms, liked_colors, liked_moods)
                if t:
                    sim_outfit["top"] = t
                if b:
                    sim_outfit["bottom"] = b
                if sim_outfit:
                    similar_recommendations.append({
                        "mood": sim_mood,
                        "outfit": sim_outfit
                    })

    weather_msg = WEATHER_MESSAGES.get(weather or "", "오늘도 멋진 코디 해보세요 💕")

    return {
        "outfit": outfit,
        "style": mood or "캐주얼",
        "explanation": weather_msg,
        "mood": mood,
        "weather": weather,
        "season": season,
        "similar_recommendations": similar_recommendations,
        "ai_message": weather_msg,
    }


def recommend_outfit_with_openai(weather=None, temperature=None, location=None, mood=None, date=None):
    """OpenAI GPT를 활용한 AI 코디 추천"""
    global client

    # client 없으면 초기화 시도
    if not client:
        init_openai()

    if not client:
        # GPT 불가 → 간단 추천으로 fallback
        result = recommend_outfit_simple(weather=weather, mood=mood, date=date)
        result["explanation"] = "AI 연결 없이 학습된 취향으로 추천했어요 💕"
        return result

    season = _get_season(date)
    all_clothes = load_clothes()
    available = [c for c in all_clothes if not c.get("excluded", False)]

    if not available:
        return {
            "error": "옷장이 비어있어요! 옷을 먼저 등록해주세요 👗",
            "outfit": {},
            "style": "",
            "explanation": "",
            "similar_recommendations": [],
            "ai_message": "옷장이 비어있어요! 옷을 먼저 등록해주세요 👗",
        }

    prefs = analyze_user_preference()
    profile = prefs.get("profile", {})
    body_type = profile.get("body_type", "보통")

    clothes_by_cat = {}
    for item in available:
        cat = item.get("category", "기타")
        clothes_by_cat.setdefault(cat, []).append({
            "name": item["name"],
            "type": item.get("type", ""),
            "color": item.get("color", ""),
            "mood": item.get("mood", []),
            "season": item.get("season", []),
        })

    prompt = (
        "당신은 전문 패션 스타일리스트입니다. 아래 정보를 바탕으로 최적의 코디를 추천해주세요.\n\n"
        f"날씨: {weather or '정보 없음'}\n"
        f"기온: {temperature}°C\n"
        f"계절: {season or '정보 없음'}\n"
        f"원하는 무드: {mood or '자유'}\n"
        f"체형: {body_type}\n\n"
        f"옷장 목록:\n{json.dumps(clothes_by_cat, ensure_ascii=False, indent=2)}\n\n"
        f"좋아하는 스타일: {list(prefs['liked_styles'].keys())[:3]}\n"
        f"좋아하는 색상: {list(prefs['liked_colors'].keys())[:3]}\n"
        f"피하는 스타일: {list(prefs['disliked_styles'].keys())[:2]}\n\n"
        "요구사항:\n"
        "1. 날씨·계절에 맞게 선택하세요.\n"
        "2. 상의·하의는 필수, 아우터는 날씨에 따라 선택하세요.\n"
        "3. 색상 조합이 조화로워야 합니다.\n"
        "4. 체형을 고려해서 추천하세요.\n\n"
        "JSON만 반환하세요 (설명 없이):\n"
        '{"top":{"name":"상의이름"},"bottom":{"name":"하의이름"},'
        '"outer":{"name":"아우터이름 또는 null"},'
        '"style":"스타일명","explanation":"코디 설명 2문장"}'
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 패션 스타일리스트입니다. JSON만 반환하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=600,
        )
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```")[0]
        recommendation = json.loads(text.strip())

        final_outfit = {}
        cat_map = {"top": "상의", "bottom": "하의", "outer": "아우터"}
        for part, category in cat_map.items():
            rec = recommendation.get(part, {})
            if not rec:
                continue
            rec_name = rec.get("name", "") if isinstance(rec, dict) else str(rec)
            if not rec_name or rec_name.lower() == "null":
                continue
            for item in available:
                if item.get("category") == category and rec_name in item["name"]:
                    final_outfit[part] = item
                    break

        # GPT 결과가 비어있으면 fallback
        if not final_outfit:
            return recommend_outfit_simple(weather=weather, mood=mood, date=date)

        explanation = recommendation.get("explanation", "")
        weather_msg = WEATHER_MESSAGES.get(weather or "", explanation or "오늘도 멋진 코디 해보세요 💕")

        return {
            "outfit": final_outfit,
            "style": recommendation.get("style", mood or "캐주얼"),
            "explanation": explanation,
            "mood": mood,
            "weather": weather,
            "temperature": temperature,
            "season": season,
            "similar_recommendations": [],
            "ai_message": weather_msg,
        }

    except Exception as e:
        # 오류 시 간단 추천으로 fallback
        result = recommend_outfit_simple(weather=weather, mood=mood, date=date)
        result["explanation"] = f"AI 오류로 취향 기반 추천을 드려요 💕 ({str(e)[:30]})"
        return result
