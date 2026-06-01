import calendar
import os
import sys

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QLineEdit, QTextEdit, QComboBox,
    QScrollArea, QGridLayout, QMessageBox, QDialog, QFormLayout,
    QCheckBox, QSizePolicy, QButtonGroup, QApplication
)
from PySide6.QtCore import Qt, QDate, QTimer, Signal, QByteArray, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QCursor

try:
    from PySide6.QtSvg import QSvgRenderer
    SVG_OK = True
except ImportError:
    SVG_OK = False

from features.user_manager import (
    set_current_user, get_current_user, load_users,
    save_user_profile, load_user_profile
)
from features.calendar_manager import (
    save_schedule, load_schedule, delete_schedule, get_dates_with_records
)
from features.closet_manager import add_clothes, load_clothes, delete_clothes, filter_clothes
from features.favorite_manager import add_favorite, load_favorite, delete_favorite, analyze_style
from features.ai_recommender import (
    recommend_outfit_simple, recommend_outfit_with_openai,
    save_feedback, load_feedback_data, init_openai
)

# ─────────────────────────────────────────────
#  색상 팔레트
# ─────────────────────────────────────────────
C_BG        = "#FFF0F5"
C_SIDEBAR1  = "#FFB7C5"
C_SIDEBAR2  = "#FF85A1"
C_ACCENT    = "#FF6B8E"
C_ACCENT2   = "#FF4D75"
C_CARD      = "#FFFFFF"
C_BORDER    = "#FFD6E4"
C_TEXT      = "#3C2230"
C_TEXT2     = "#9B6070"
C_BTN       = "#FF85A1"
C_BTN_H     = "#FF6B8E"
C_GREEN     = "#7BC47A"
C_RED       = "#E57373"

# 옷 색상 → HEX
COLOR_HEX = {
    "검정":  "#2C2C2C",
    "흰색":  "#F0F0F0",
    "회색":  "#9E9E9E",
    "빨강":  "#E53935",
    "파랑":  "#1E88E5",
    "초록":  "#43A047",
    "노랑":  "#FDD835",
    "분홍":  "#F48FB1",
    "보라":  "#8E24AA",
    "베이지": "#D7C5A0",
    "브라운": "#795548",
}

# 기분 → 이모지
MOOD_EMOJI = {
    "행복":   "😊",
    "편안함": "😌",
    "우울함": "😢",
    "설레는": "🥰",
    "피곤함": "😴",
    "활기찬": "💪",
}

# ─────────────────────────────────────────────
#  SVG 옷 아이콘 템플릿
# ─────────────────────────────────────────────
SVG_TMPL = {
    "티셔츠": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,15 L7,38 L24,44 L24,70 L56,70 L56,44 L73,38 L58,15 L50,21 C44,26 36,26 30,21 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "맨투맨": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,16 L7,39 L24,45 L24,70 L56,70 L56,45 L73,39 L58,16 L50,22 C44,28 36,28 30,22 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M30,22 C36,30 44,30 50,22" fill="none" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "후드티": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,18 L7,40 L24,46 L24,72 L56,72 L56,46 L73,40 L58,18 L50,24 C44,22 36,22 30,24 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M30,24 C34,17 37,14 40,14 C43,14 46,17 50,24 C46,28 43,30 40,30 C37,30 34,28 30,24 Z"
        fill="FILL" stroke="STROKE" stroke-width="2" stroke-linejoin="round"/>
  <ellipse cx="40" cy="26" rx="5" ry="6" fill="none" stroke="STROKE" stroke-width="1.5"/>
</svg>""",
    "셔츠": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,15 L7,38 L24,44 L24,70 L56,70 L56,44 L73,38 L58,15 L50,21 L44,16 L40,20 L36,16 L30,21 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M36,16 L38,32 L40,34 L42,32 L44,16" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
  <circle cx="40" cy="38" r="1.5" fill="STROKE"/>
  <circle cx="40" cy="46" r="1.5" fill="STROKE"/>
  <circle cx="40" cy="54" r="1.5" fill="STROKE"/>
</svg>""",
    "니트": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,15 L7,38 L24,44 L24,70 L56,70 L56,44 L73,38 L58,15 L50,21 C44,26 36,26 30,21 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="24" y1="50" x2="56" y2="50" stroke="STROKE" stroke-width="1.2" stroke-dasharray="3,2"/>
  <line x1="24" y1="57" x2="56" y2="57" stroke="STROKE" stroke-width="1.2" stroke-dasharray="3,2"/>
  <line x1="24" y1="64" x2="56" y2="64" stroke="STROKE" stroke-width="1.2" stroke-dasharray="3,2"/>
</svg>""",
    "청바지": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M17,14 L14,70 L36,70 L40,47 L44,70 L66,70 L63,14 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="40" y1="18" x2="40" y2="47" stroke="STROKE" stroke-width="2"/>
  <rect x="17" y="11" width="46" height="7" rx="2" fill="FILL" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "슬랙스": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M18,14 L15,70 L37,70 L40,48 L43,70 L65,70 L62,14 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="40" y1="18" x2="40" y2="48" stroke="STROKE" stroke-width="1.8"/>
  <rect x="18" y="11" width="44" height="7" rx="3" fill="FILL" stroke="STROKE" stroke-width="2"/>
  <line x1="18" y1="25" x2="62" y2="25" stroke="STROKE" stroke-width="1"/>
</svg>""",
    "반바지": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M17,14 L14,52 L36,52 L40,38 L44,52 L66,52 L63,14 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="40" y1="18" x2="40" y2="38" stroke="STROKE" stroke-width="2"/>
  <rect x="17" y="11" width="46" height="7" rx="2" fill="FILL" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "치마": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <rect x="23" y="13" width="34" height="10" rx="3" fill="FILL" stroke="STROKE" stroke-width="2"/>
  <path d="M20,23 L8,72 L72,72 L60,23 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "레깅스": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M19,14 L16,75 L37,75 L40,52 L43,75 L64,75 L61,14 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <rect x="19" y="11" width="42" height="7" rx="2" fill="FILL" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "자켓": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,15 L4,40 L22,46 L22,70 L58,70 L58,46 L76,40 L58,15 L50,22 L44,26 L40,28 L36,26 L30,22 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M37,26 L36,70" stroke="STROKE" stroke-width="1.5" fill="none"/>
  <path d="M43,26 L44,70" stroke="STROKE" stroke-width="1.5" fill="none"/>
</svg>""",
    "코트": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,12 L4,38 L22,44 L22,76 L58,76 L58,44 L76,38 L58,12 L50,19 L44,23 L40,25 L36,23 L30,19 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M37,23 L36,76" stroke="STROKE" stroke-width="1.5" fill="none"/>
  <path d="M43,23 L44,76" stroke="STROKE" stroke-width="1.5" fill="none"/>
  <circle cx="40" cy="40" r="2" fill="STROKE"/>
  <circle cx="40" cy="52" r="2" fill="STROKE"/>
  <circle cx="40" cy="64" r="2" fill="STROKE"/>
</svg>""",
    "패딩": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,15 L4,40 L22,46 L22,75 L58,75 L58,46 L76,40 L58,15 L50,22 L40,24 L30,22 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M40,24 L40,75" stroke="STROKE" stroke-width="1.5" fill="none"/>
  <line x1="22" y1="52" x2="58" y2="52" stroke="STROKE" stroke-width="2"/>
  <line x1="22" y1="60" x2="58" y2="60" stroke="STROKE" stroke-width="2"/>
  <line x1="22" y1="68" x2="58" y2="68" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "가디건": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,16 L7,39 L24,45 L24,72 L56,72 L56,45 L73,39 L58,16 L50,22 L44,17 L40,21 L36,17 L30,22 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M40,21 L40,72" stroke="STROKE" stroke-width="1.5" fill="none"/>
  <line x1="24" y1="52" x2="56" y2="52" stroke="STROKE" stroke-width="1.2" stroke-dasharray="3,2"/>
  <line x1="24" y1="60" x2="56" y2="60" stroke="STROKE" stroke-width="1.2" stroke-dasharray="3,2"/>
</svg>""",
    "점퍼": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M22,16 L5,40 L22,46 L22,70 L58,70 L58,46 L75,40 L58,16 L50,23 L40,25 L30,23 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M40,25 L40,70" stroke="STROKE" stroke-width="1.5" fill="none"/>
  <line x1="22" y1="62" x2="58" y2="62" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "운동화": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M8,58 C8,58 22,32 44,32 L64,32 C70,32 72,37 70,42 L60,52 L68,57 C68,62 64,64 58,64 L12,64 C8,64 6,61 8,58 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
  <line x1="30" y1="32" x2="28" y2="43" stroke="STROKE" stroke-width="1.5"/>
  <line x1="38" y1="32" x2="36" y2="43" stroke="STROKE" stroke-width="1.5"/>
  <line x1="46" y1="32" x2="44" y2="43" stroke="STROKE" stroke-width="1.5"/>
</svg>""",
    "구두": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M10,67 L10,52 C10,42 18,34 30,34 L55,34 C62,34 66,40 65,47 L58,57 C58,57 70,60 72,64 C72,68 68,70 62,70 L14,70 C11,70 9,69 10,67 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "부츠": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <rect x="26" y="10" width="22" height="38" rx="5" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
  <path d="M20,48 C20,48 18,56 18,61 C18,66 26,69 40,69 C54,69 64,66 64,63 C64,60 56,56 56,56 L48,48 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "슬리퍼": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <ellipse cx="40" cy="62" rx="30" ry="9" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
  <path d="M20,57 C20,47 26,37 33,34 C39,32 41,32 47,34 C54,37 58,47 55,57"
        fill="none" stroke="STROKE" stroke-width="5" stroke-linecap="round"/>
</svg>""",
    "샌들": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <ellipse cx="40" cy="64" rx="29" ry="8" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
  <path d="M18,60 C18,50 30,38 40,36 C50,38 62,50 62,60"
        fill="none" stroke="STROKE" stroke-width="3" stroke-linecap="round"/>
  <line x1="28" y1="44" x2="52" y2="44" stroke="STROKE" stroke-width="3" stroke-linecap="round"/>
</svg>""",
    "모자": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <ellipse cx="40" cy="56" rx="33" ry="8" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
  <path d="M16,56 C16,56 19,26 40,23 C61,26 64,56 64,56 Z"
        fill="FILL" stroke="STROKE" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "가방": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <rect x="10" y="32" width="60" height="40" rx="8" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
  <path d="M28,32 C28,22 52,22 52,32" fill="none" stroke="STROKE" stroke-width="3"/>
  <rect x="33" y="47" width="14" height="11" rx="3" fill="none" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "목걸이": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <path d="M20,20 C20,50 30,65 40,68 C50,65 60,50 60,20"
        fill="none" stroke="STROKE" stroke-width="3" stroke-linecap="round"/>
  <circle cx="40" cy="68" r="6" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
</svg>""",
    "시계": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <circle cx="40" cy="42" r="22" fill="FILL" stroke="STROKE" stroke-width="3"/>
  <line x1="40" y1="42" x2="40" y2="27" stroke="STROKE" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="40" y1="42" x2="52" y2="42" stroke="STROKE" stroke-width="2.5" stroke-linecap="round"/>
  <rect x="30" y="18" width="20" height="6" rx="3" fill="FILL" stroke="STROKE" stroke-width="2"/>
</svg>""",
    "안경": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <circle cx="25" cy="42" r="14" fill="none" stroke="STROKE" stroke-width="3"/>
  <circle cx="55" cy="42" r="14" fill="none" stroke="STROKE" stroke-width="3"/>
  <line x1="39" y1="42" x2="41" y2="42" stroke="STROKE" stroke-width="3"/>
  <path d="M11,42 C8,36 5,32 3,34" fill="none" stroke="STROKE" stroke-width="2.5"/>
  <path d="M69,42 C72,36 75,32 77,34" fill="none" stroke="STROKE" stroke-width="2.5"/>
</svg>""",
    "기본": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <rect x="15" y="15" width="50" height="55" rx="8" fill="FILL" stroke="STROKE" stroke-width="2.5"/>
  <line x1="15" y1="30" x2="65" y2="30" stroke="STROKE" stroke-width="1.5"/>
</svg>""",
}


def _stroke_for(hex_color):
    """색상에 따른 외곽선 색 반환"""
    light = {"#F0F0F0", "#FDD835", "#D7C5A0", "#F48FB1"}
    if hex_color in light:
        return "#888888"
    return "rgba(0,0,0,0.25)"


def get_svg_pixmap(type_name, color_name, size=64):
    """옷 종류 + 색상으로 채색된 QPixmap 반환"""
    if not SVG_OK:
        return None
    tmpl = SVG_TMPL.get(type_name, SVG_TMPL["기본"])
    hex_c = COLOR_HEX.get(color_name, C_BTN)
    stroke = _stroke_for(hex_c)
    svg = tmpl.replace("FILL", hex_c).replace("STROKE", stroke)
    try:
        data = QByteArray(svg.encode("utf-8"))
        renderer = QSvgRenderer(data)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap
    except Exception:
        return None


# ─────────────────────────────────────────────
#  전체 스타일시트
# ─────────────────────────────────────────────
APP_STYLE = f"""
QWidget {{
    background-color: {C_BG};
    font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
    color: {C_TEXT};
    font-size: 13px;
}}

QFrame#sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {C_SIDEBAR1}, stop:1 {C_SIDEBAR2});
    border-radius: 0px;
}}

QFrame#content_card {{
    background-color: {C_CARD};
    border: 1.5px solid {C_BORDER};
    border-radius: 18px;
}}

QPushButton {{
    background-color: {C_BTN};
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {C_BTN_H};
}}

QPushButton:pressed {{
    background-color: {C_ACCENT2};
}}

QPushButton#sidebar_btn {{
    background-color: transparent;
    color: white;
    text-align: left;
    padding: 12px 18px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: bold;
}}

QPushButton#sidebar_btn:hover {{
    background-color: rgba(255,255,255,0.20);
}}

QPushButton#sidebar_btn:checked {{
    background-color: rgba(255,255,255,0.35);
}}

QPushButton#danger_btn {{
    background-color: {C_RED};
}}

QPushButton#green_btn {{
    background-color: {C_GREEN};
}}

QPushButton#ghost_btn {{
    background-color: transparent;
    color: {C_ACCENT};
    border: 2px solid {C_ACCENT};
}}

QPushButton#ghost_btn:hover {{
    background-color: {C_ACCENT};
    color: white;
}}

QLineEdit, QTextEdit, QComboBox {{
    border: 2px solid {C_BORDER};
    border-radius: 10px;
    padding: 8px 12px;
    background-color: #FFF8FB;
    font-size: 13px;
    color: {C_TEXT};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 2px solid {C_ACCENT};
    background-color: white;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: #FFE8F0;
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {C_BTN};
    border-radius: 4px;
    min-height: 20px;
}}

QCheckBox {{
    spacing: 6px;
    color: {C_TEXT};
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid {C_BORDER};
    background: white;
}}

QCheckBox::indicator:checked {{
    background: {C_ACCENT};
    border: 2px solid {C_ACCENT};
}}

QLabel#section_title {{
    font-size: 20px;
    font-weight: bold;
    color: {C_TEXT};
}}

QLabel#subtitle {{
    font-size: 13px;
    color: {C_TEXT2};
}}
"""


# ─────────────────────────────────────────────
#  헬퍼 위젯
# ─────────────────────────────────────────────
def make_card(parent=None):
    f = QFrame(parent)
    f.setObjectName("content_card")
    return f


def make_sep():
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"color: {C_BORDER};")
    return sep


class BubbleLabel(QLabel):
    """말풍선 스타일 레이블"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet(f"""
            background: white;
            border: 2px solid {C_BORDER};
            border-radius: 16px;
            padding: 14px 16px;
            font-size: 13px;
            color: {C_TEXT};
            line-height: 1.6;
        """)


# ─────────────────────────────────────────────
#  커스텀 캘린더 위젯
# ─────────────────────────────────────────────
class CustomCalendar(QWidget):
    dateClicked = Signal(str)  # "yyyy-MM-dd"

    def __init__(self, parent=None):
        super().__init__(parent)
        today = QDate.currentDate()
        self.year = today.year()
        self.month = today.month()
        self.records = set()
        self.mood_map = {}   # date_str -> mood emoji
        self.selected = None
        self._build_ui()
        self.refresh_records()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(0, 0, 0, 0)

        # 헤더
        hdr = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(36, 36)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{ background: white; color: {C_ACCENT}; border: 2px solid {C_BORDER};
                          border-radius: 10px; font-weight: bold; }}
            QPushButton:hover {{ background: {C_ACCENT}; color: white; }}
        """)
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(36, 36)
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.month_lbl = QLabel()
        self.month_lbl.setAlignment(Qt.AlignCenter)
        self.month_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C_TEXT};")
        hdr.addWidget(self.prev_btn)
        hdr.addWidget(self.month_lbl, 1)
        hdr.addWidget(self.next_btn)
        outer.addLayout(hdr)

        # 요일 헤더
        day_hdr = QGridLayout()
        day_hdr.setSpacing(4)
        days = ["월", "화", "수", "목", "금", "토", "일"]
        colors = [C_TEXT] * 5 + [C_ACCENT2, C_ACCENT]
        for i, (d, c) in enumerate(zip(days, colors)):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {c};")
            day_hdr.addWidget(lbl, 0, i)
        outer.addLayout(day_hdr)

        # 날짜 그리드
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(4)
        outer.addWidget(self.grid_container)

        self.prev_btn.clicked.connect(self._prev_month)
        self.next_btn.clicked.connect(self._next_month)
        self._rebuild()

    def _clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _rebuild(self):
        self._clear_grid()
        self.month_lbl.setText(f"{self.year}년 {self.month}월")

        first_wd, num_days = calendar.monthrange(self.year, self.month)
        # Python: 0=월요일, 6=일요일

        row, col = 0, first_wd
        for day in range(1, num_days + 1):
            date_str = f"{self.year}-{self.month:02d}-{day:02d}"
            has_record = date_str in self.records
            mood_e = self.mood_map.get(date_str, "")

            btn = QPushButton()
            btn.setFixedSize(48, 48)
            btn.setProperty("date_str", date_str)

            # 토(5)=C_ACCENT2, 일(6)=C_ACCENT 색상
            if col == 5:
                fg = C_ACCENT2
            elif col == 6:
                fg = C_ACCENT
            else:
                fg = C_TEXT

            if has_record:
                btn.setText(f"{mood_e}\n{day}" if mood_e else str(day))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {C_BTN};
                        color: white;
                        border-radius: 10px;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px;
                    }}
                    QPushButton:hover {{ background: {C_BTN_H}; }}
                """)
            else:
                btn.setText(str(day))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: white;
                        color: {fg};
                        border: 1.5px solid {C_BORDER};
                        border-radius: 10px;
                        font-size: 13px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{ background: {C_BG}; border-color: {C_ACCENT}; }}
                """)

            btn.clicked.connect(lambda checked=False, ds=date_str: self.dateClicked.emit(ds))
            self.grid.addWidget(btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def refresh_records(self):
        self.records = set(get_dates_with_records())
        self.mood_map = {}
        for s in load_schedule():
            if isinstance(s, dict):
                d = s.get("date", "")
                m = s.get("mood", "")
                if d and m:
                    self.mood_map[d] = MOOD_EMOJI.get(m, "")
        self._rebuild()

    def _prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self._rebuild()

    def _next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self._rebuild()


# ─────────────────────────────────────────────
#  로그인 페이지
# ─────────────────────────────────────────────
class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setSpacing(0)

        # 타이틀
        title = QLabel("💕 StyleMate")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 52px; font-weight: bold; color: {C_ACCENT}; padding: 0;")

        sub = QLabel("나만의 AI 패션 스타일리스트")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size: 16px; color: {C_TEXT2}; margin-bottom: 30px;")

        outer.addWidget(title)
        outer.addWidget(sub)
        outer.addSpacing(20)

        card = make_card()
        card.setMinimumWidth(420)
        card.setMaximumWidth(480)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(30, 30, 30, 30)

        users = load_users()

        if users:
            lbl = QLabel("계속하기")
            lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {C_TEXT};")
            card_layout.addWidget(lbl)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMaximumHeight(180)
            scroll.setStyleSheet("background: transparent; border: none;")
            user_w = QWidget()
            user_v = QVBoxLayout(user_w)
            user_v.setSpacing(8)
            user_v.setContentsMargins(0, 0, 0, 0)
            for name in users:
                btn = QPushButton(f"👤  {name}")
                btn.setMinimumHeight(44)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #FFF0F5;
                        color: {C_TEXT};
                        border: 1.5px solid {C_BORDER};
                        border-radius: 12px;
                        text-align: left;
                        padding-left: 16px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{ background: {C_BTN}; color: white; border-color: {C_BTN}; }}
                """)
                btn.clicked.connect(lambda checked=False, n=name: self._login_existing(n))
                user_v.addWidget(btn)
            user_v.addStretch()
            scroll.setWidget(user_w)
            card_layout.addWidget(scroll)
            card_layout.addWidget(make_sep())

        new_lbl = QLabel("새 사용자" if users else "시작하기")
        new_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {C_TEXT};")
        card_layout.addWidget(new_lbl)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("이름을 입력하세요")
        self.name_input.setMinimumHeight(44)
        self.name_input.returnPressed.connect(self._new_user)
        card_layout.addWidget(self.name_input)

        new_btn = QPushButton("✨ 새로 시작하기")
        new_btn.setMinimumHeight(46)
        new_btn.clicked.connect(self._new_user)
        card_layout.addWidget(new_btn)

        outer.addWidget(card, alignment=Qt.AlignCenter)

    def _login_existing(self, name):
        set_current_user(name)
        self.main_window.show_main_app()

    def _new_user(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "알림", "이름을 입력해주세요!")
            return
        if name in load_users():
            set_current_user(name)
            self.main_window.show_main_app()
            return
        dlg = ProfileSetupDialog(name, self)
        if dlg.exec():
            set_current_user(name)
            self.main_window.show_main_app()


# ─────────────────────────────────────────────
#  프로필 설정 다이얼로그 (신규 사용자)
# ─────────────────────────────────────────────
class ProfileSetupDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("프로필 설정")
        self.setMinimumWidth(460)
        self.setStyleSheet(APP_STYLE)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        hdr = QLabel(f"💕 {self.username}님 환영해요!")
        hdr.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {C_ACCENT};")
        sub = QLabel("취향을 알려주시면 딱 맞는 코디를 추천해드려요!")
        sub.setStyleSheet(f"font-size: 13px; color: {C_TEXT2};")
        layout.addWidget(hdr)
        layout.addWidget(sub)
        layout.addWidget(make_sep())

        # 선호 무드
        m_lbl = QLabel("💭 좋아하는 스타일 (복수 선택)")
        m_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C_TEXT};")
        layout.addWidget(m_lbl)

        mood_w = QWidget()
        mood_g = QGridLayout(mood_w)
        mood_g.setSpacing(8)
        mood_g.setContentsMargins(0, 0, 0, 0)
        moods = ["캐주얼", "포멀", "힙", "스트릿", "페미닌", "심플", "빈티지", "모던"]
        self.mood_checks = {}
        for i, m in enumerate(moods):
            cb = QCheckBox(m)
            self.mood_checks[m] = cb
            mood_g.addWidget(cb, i // 4, i % 4)
        layout.addWidget(mood_w)

        # 체형
        b_lbl = QLabel("👤 체형")
        b_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C_TEXT};")
        self.body_combo = QComboBox()
        self.body_combo.addItems(["보통", "슬림", "볼륨"])
        self.body_combo.setMinimumHeight(40)
        layout.addWidget(b_lbl)
        layout.addWidget(self.body_combo)

        # 선호 색상
        c_lbl = QLabel("🎨 좋아하는 색상 (복수 선택)")
        c_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C_TEXT};")
        layout.addWidget(c_lbl)

        color_w = QWidget()
        color_g = QGridLayout(color_w)
        color_g.setSpacing(8)
        color_g.setContentsMargins(0, 0, 0, 0)
        colors = list(COLOR_HEX.keys())
        self.color_checks = {}
        for i, c in enumerate(colors):
            cb = QCheckBox(c)
            self.color_checks[c] = cb
            color_g.addWidget(cb, i // 4, i % 4)
        layout.addWidget(color_w)

        layout.addWidget(make_sep())

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾 저장하고 시작하기")
        save_btn.setMinimumHeight(46)
        save_btn.clicked.connect(self._save)
        skip_btn = QPushButton("나중에 설정할게요")
        skip_btn.setObjectName("ghost_btn")
        skip_btn.setMinimumHeight(46)
        skip_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(skip_btn)
        layout.addLayout(btn_row)

    def _save(self):
        preferred_moods = [m for m, cb in self.mood_checks.items() if cb.isChecked()]
        favorite_colors = [c for c, cb in self.color_checks.items() if cb.isChecked()]
        profile = {
            "preferred_moods": preferred_moods,
            "body_type": self.body_combo.currentText(),
            "favorite_colors": favorite_colors,
        }
        save_user_profile(self.username, profile)
        self.accept()


# ─────────────────────────────────────────────
#  AI 어시스턴트 패널
# ─────────────────────────────────────────────
class AiPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content_card")
        self.setMinimumWidth(260)
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        avatar = QLabel("🤖")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 56px;")

        ai_name = QLabel("Style AI")
        ai_name.setAlignment(Qt.AlignCenter)
        ai_name.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_ACCENT};")

        self.bubble = BubbleLabel("안녕하세요! 오늘의 코디를 추천해드릴게요 💕\n\n무드를 선택하고 추천받기 버튼을 눌러보세요!")

        # 쇼핑 링크 영역
        self.shop_frame = QFrame()
        self.shop_frame.setVisible(False)
        shop_layout = QVBoxLayout(self.shop_frame)
        shop_layout.setSpacing(6)
        shop_layout.setContentsMargins(0, 0, 0, 0)

        shop_lbl = QLabel("🛍️ 옷장에 없는 옷이 필요하다면?")
        shop_lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {C_TEXT2};")
        shop_lbl.setWordWrap(True)

        self.musinsa_btn = QPushButton("무신사에서 찾기")
        self.musinsa_btn.setObjectName("ghost_btn")
        self.musinsa_btn.setMinimumHeight(36)

        self.ably_btn = QPushButton("에이블리에서 찾기")
        self.ably_btn.setObjectName("ghost_btn")
        self.ably_btn.setMinimumHeight(36)

        shop_layout.addWidget(shop_lbl)
        shop_layout.addWidget(self.musinsa_btn)
        shop_layout.addWidget(self.ably_btn)

        layout.addWidget(avatar)
        layout.addWidget(ai_name)
        layout.addWidget(self.bubble)
        layout.addWidget(self.shop_frame)
        layout.addStretch()

    def set_message(self, msg):
        self.bubble.setText(msg)

    def show_shopping(self, keyword):
        import urllib.parse
        q = urllib.parse.quote(keyword)
        musinsa_url = f"https://www.musinsa.com/search/musinsa/integration?q={q}"
        ably_url = f"https://m.a-bly.com/search?q={q}"

        self.musinsa_btn.clicked.disconnect() if self.musinsa_btn.receivers(self.musinsa_btn.clicked) > 0 else None
        self.ably_btn.clicked.disconnect() if self.ably_btn.receivers(self.ably_btn.clicked) > 0 else None

        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        self.musinsa_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(musinsa_url)))
        self.ably_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(ably_url)))
        self.shop_frame.setVisible(True)

    def hide_shopping(self):
        self.shop_frame.setVisible(False)


# ─────────────────────────────────────────────
#  옷 아이콘 카드 (추천 결과 표시용)
# ─────────────────────────────────────────────
def make_outfit_item_card(label, item):
    """상의/하의/아우터 추천 카드"""
    card = make_card()
    card.setMinimumHeight(110)
    layout = QHBoxLayout(card)
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(12)

    # SVG 아이콘
    icon_lbl = QLabel()
    icon_lbl.setFixedSize(64, 64)
    icon_lbl.setAlignment(Qt.AlignCenter)
    if SVG_OK and isinstance(item, dict):
        pix = get_svg_pixmap(item.get("type", "기본"), item.get("color", "검정"), 60)
        if pix:
            icon_lbl.setPixmap(pix)
        else:
            icon_lbl.setText("👗")
            icon_lbl.setStyleSheet("font-size: 32px;")
    else:
        icon_lbl.setText("👗")
        icon_lbl.setStyleSheet("font-size: 32px;")

    info = QVBoxLayout()
    info.setSpacing(3)

    cat_lbl = QLabel(label)
    cat_lbl.setStyleSheet(f"font-size: 11px; color: {C_TEXT2}; font-weight: bold;")

    name_lbl = QLabel(item.get("name", str(item)) if isinstance(item, dict) else str(item))
    name_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C_TEXT};")

    color_lbl = QLabel(item.get("color", "") if isinstance(item, dict) else "")
    color_lbl.setStyleSheet(f"font-size: 12px; color: {C_TEXT2};")

    moods = item.get("mood", []) if isinstance(item, dict) else []
    if moods:
        mood_lbl = QLabel("  ".join(moods[:3]))
        mood_lbl.setStyleSheet(f"""
            font-size: 11px; color: {C_ACCENT};
            background: #FFF0F5; border-radius: 6px;
            padding: 2px 6px;
        """)
        info.addWidget(mood_lbl)

    info.addWidget(cat_lbl)
    info.addWidget(name_lbl)
    info.addWidget(color_lbl)

    layout.addWidget(icon_lbl)
    layout.addLayout(info, 1)
    return card


# ─────────────────────────────────────────────
#  홈 페이지 (코디 추천 포함)
# ─────────────────────────────────────────────
class HomePage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.current_rec = None
        self.current_weather = None
        self.current_temp = None
        self._build()
        self._load_weather()

    def _build(self):
        root = QHBoxLayout(self)
        root.setSpacing(20)
        root.setContentsMargins(0, 0, 0, 0)

        # ── 왼쪽: 추천 영역
        left = QScrollArea()
        left.setWidgetResizable(True)
        left.setStyleSheet("background: transparent; border: none;")
        left_w = QWidget()
        left_w.setStyleSheet("background: transparent;")
        lv = QVBoxLayout(left_w)
        lv.setSpacing(16)
        lv.setContentsMargins(0, 0, 8, 0)

        # 인사 + 날씨
        greet_card = make_card()
        greet_l = QVBoxLayout(greet_card)
        greet_l.setContentsMargins(20, 16, 20, 16)

        username = get_current_user() or "친구"
        self.greet_lbl = QLabel(f"안녕하세요, {username}님! 💕")
        self.greet_lbl.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {C_TEXT};")

        self.weather_lbl = QLabel("날씨 정보 불러오는 중...")
        self.weather_lbl.setStyleSheet(f"font-size: 13px; color: {C_TEXT2};")

        # 통계
        stat_row = QHBoxLayout()
        stat_row.setSpacing(12)
        self.stat_clothes = self._stat_badge("👗", "등록 옷", str(len(load_clothes())))
        self.stat_fav = self._stat_badge("⭐", "즐겨찾기", str(len(load_favorite())))
        self.stat_cal = self._stat_badge("📅", "기록", str(len(get_dates_with_records())))
        stat_row.addWidget(self.stat_clothes)
        stat_row.addWidget(self.stat_fav)
        stat_row.addWidget(self.stat_cal)
        stat_row.addStretch()

        greet_l.addWidget(self.greet_lbl)
        greet_l.addWidget(self.weather_lbl)
        greet_l.addSpacing(8)
        greet_l.addLayout(stat_row)
        lv.addWidget(greet_card)

        # 코디 추천 컨트롤
        ctrl_card = make_card()
        ctrl_l = QVBoxLayout(ctrl_card)
        ctrl_l.setContentsMargins(20, 16, 20, 16)
        ctrl_l.setSpacing(12)

        ctrl_title = QLabel("✨ 오늘의 코디 추천")
        ctrl_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C_TEXT};")

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        mood_lbl = QLabel("무드:")
        mood_lbl.setStyleSheet(f"font-size: 13px; color: {C_TEXT2};")
        self.mood_combo = QComboBox()
        self.mood_combo.setMinimumHeight(38)
        self.mood_combo.addItems([
            "자동 선택", "캐주얼", "포멀", "힙", "스트릿",
            "페미닌", "심플", "빈티지", "모던"
        ])

        mode_lbl = QLabel("AI:")
        mode_lbl.setStyleSheet(f"font-size: 13px; color: {C_TEXT2};")
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(38)
        self.mode_combo.addItems(["GPT (고급)", "빠른 추천"])

        row1.addWidget(mood_lbl)
        row1.addWidget(self.mood_combo, 2)
        row1.addWidget(mode_lbl)
        row1.addWidget(self.mode_combo, 1)

        rec_btn = QPushButton("🎯 코디 추천받기")
        rec_btn.setMinimumHeight(46)
        rec_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_BTN}, stop:1 {C_ACCENT});
                color: white; border-radius: 14px;
                font-size: 15px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {C_ACCENT2}; }}
        """)
        rec_btn.clicked.connect(self._recommend)

        ctrl_l.addWidget(ctrl_title)
        ctrl_l.addLayout(row1)
        ctrl_l.addWidget(rec_btn)
        lv.addWidget(ctrl_card)

        # 추천 결과 영역
        self.result_area = QFrame()
        self.result_area.setObjectName("content_card")
        self.result_v = QVBoxLayout(self.result_area)
        self.result_v.setContentsMargins(20, 16, 20, 16)
        self.result_v.setSpacing(10)

        self.result_ph = QLabel("코디 추천 결과가 여기에 나타나요 ✨")
        self.result_ph.setAlignment(Qt.AlignCenter)
        self.result_ph.setStyleSheet(f"font-size: 14px; color: {C_TEXT2}; padding: 30px;")
        self.result_v.addWidget(self.result_ph)
        lv.addWidget(self.result_area)

        # 피드백 버튼
        self.fb_frame = QFrame()
        self.fb_frame.setVisible(False)
        fb_l = QHBoxLayout(self.fb_frame)
        fb_l.setSpacing(10)

        self.like_btn = QPushButton("👍 좋아요")
        self.like_btn.setObjectName("green_btn")
        self.like_btn.setMinimumHeight(42)
        self.like_btn.clicked.connect(lambda: self._feedback(True))

        self.dislike_btn = QPushButton("👎 별로예요")
        self.dislike_btn.setObjectName("danger_btn")
        self.dislike_btn.setMinimumHeight(42)
        self.dislike_btn.clicked.connect(lambda: self._feedback(False))

        self.fav_btn = QPushButton("⭐ 즐겨찾기")
        self.fav_btn.setMinimumHeight(42)
        self.fav_btn.clicked.connect(self._add_fav)

        fb_l.addWidget(self.like_btn)
        fb_l.addWidget(self.dislike_btn)
        fb_l.addWidget(self.fav_btn)
        lv.addWidget(self.fb_frame)

        # 유사 무드 추천
        self.sim_area = QFrame()
        self.sim_area.setVisible(False)
        self.sim_v = QVBoxLayout(self.sim_area)
        self.sim_v.setContentsMargins(0, 0, 0, 0)
        self.sim_v.setSpacing(8)
        lv.addWidget(self.sim_area)

        lv.addStretch()
        left.setWidget(left_w)

        # ── 오른쪽: AI 패널
        self.ai_panel = AiPanel()
        self.ai_panel.setMaximumWidth(290)

        root.addWidget(left, 3)
        root.addWidget(self.ai_panel, 1)

    def _stat_badge(self, icon, label, val):
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: #FFF0F5;
                border-radius: 12px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(2)
        ic = QLabel(icon)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet("font-size: 20px;")
        num = QLabel(val)
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {C_ACCENT};")
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"font-size: 11px; color: {C_TEXT2};")
        v.addWidget(ic)
        v.addWidget(num)
        v.addWidget(lbl)
        return f

    def _load_weather(self):
        from features.weather_api import get_weather, get_weather_icon_emoji
        from features.settings_manager import get_weather_key, get_default_city
        key = get_weather_key()
        city = get_default_city()
        if not key:
            self.weather_lbl.setText("⚠️ 날씨 API 키를 config.py에 입력해주세요")
            return
        data = get_weather(city, key)
        if data.get("error"):
            self.weather_lbl.setText("⚠️ 날씨 정보를 불러오지 못했어요")
        else:
            self.current_weather = data["weather"]
            self.current_temp = data["temperature"]
            emoji = get_weather_icon_emoji(data["weather"])
            self.weather_lbl.setText(
                f"{emoji} {data['city']}  {data['weather']}  {data['temperature']}°C  "
                f"💧 습도 {data.get('humidity', '-')}%"
            )

    def _recommend(self):
        from datetime import datetime
        mood = self.mood_combo.currentText()
        if mood == "자동 선택":
            mood = None
        use_gpt = (self.mode_combo.currentIndex() == 0)
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            if use_gpt:
                rec = recommend_outfit_with_openai(
                    weather=self.current_weather,
                    temperature=self.current_temp,
                    mood=mood,
                    date=today
                )
            else:
                rec = recommend_outfit_simple(
                    weather=self.current_weather,
                    mood=mood,
                    date=today
                )
        except Exception as e:
            rec = recommend_outfit_simple(weather=self.current_weather, mood=mood, date=today)

        if rec.get("error"):
            QMessageBox.information(self, "알림", rec["error"])
            self.ai_panel.set_message(rec["error"])
            return

        self.current_rec = rec
        self._show_result(rec)

        # AI 메시지
        ai_msg = rec.get("ai_message", rec.get("explanation", "오늘도 멋진 코디 해보세요 💕"))
        if rec.get("explanation"):
            ai_msg = rec["explanation"] + "\n\n" + ai_msg if rec["explanation"] != ai_msg else ai_msg
        self.ai_panel.set_message(ai_msg)

        # 옷장이 비어있을 때 쇼핑 링크 제안
        outfit = rec.get("outfit", {})
        missing = []
        if not outfit.get("top"):
            missing.append("여성 상의")
        if not outfit.get("bottom"):
            missing.append("여성 하의")

        if missing:
            self.ai_panel.show_shopping(missing[0])
        else:
            self.ai_panel.hide_shopping()

    def _show_result(self, rec):
        # 기존 위젯 제거
        while self.result_v.count():
            item = self.result_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        outfit = rec.get("outfit", {})
        style = rec.get("style", "")

        if not outfit:
            ph = QLabel("옷장에 등록된 옷이 없어요!\n옷장 탭에서 옷을 추가해보세요 👗")
            ph.setAlignment(Qt.AlignCenter)
            ph.setStyleSheet(f"font-size: 14px; color: {C_TEXT2}; padding: 30px;")
            self.result_v.addWidget(ph)
            self.fb_frame.setVisible(False)
            return

        title_row = QHBoxLayout()
        style_lbl = QLabel(f"🎨 {style} 스타일")
        style_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {C_ACCENT};")
        title_row.addWidget(style_lbl)
        title_row.addStretch()
        self.result_v.addLayout(title_row)

        if "top" in outfit:
            self.result_v.addWidget(make_outfit_item_card("상의", outfit["top"]))
        if "bottom" in outfit:
            self.result_v.addWidget(make_outfit_item_card("하의", outfit["bottom"]))
        if "outer" in outfit:
            self.result_v.addWidget(make_outfit_item_card("아우터", outfit["outer"]))

        self.fb_frame.setVisible(True)

        # 유사 무드 추천
        self._show_similar(rec.get("similar_recommendations", []))

    def _show_similar(self, sims):
        while self.sim_v.count():
            item = self.sim_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not sims:
            self.sim_area.setVisible(False)
            return

        sim_title = QLabel("💡 비슷한 무드 코디도 어때요?")
        sim_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C_TEXT};")
        self.sim_v.addWidget(sim_title)

        for s in sims:
            s_mood = s.get("mood", "")
            s_out = s.get("outfit", {})
            if not s_out:
                continue
            card = make_card()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            cl.setSpacing(6)
            ml = QLabel(f"💭 {s_mood} 무드")
            ml.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_ACCENT2};")
            cl.addWidget(ml)
            items_row = QHBoxLayout()
            items_row.setSpacing(8)
            for part, lbl in [("top", "상의"), ("bottom", "하의")]:
                it = s_out.get(part)
                if it:
                    item_lbl = QLabel(f"{lbl}: {it.get('name','')}")
                    item_lbl.setStyleSheet(f"font-size: 12px; color: {C_TEXT2};")
                    items_row.addWidget(item_lbl)
            items_row.addStretch()
            cl.addLayout(items_row)
            self.sim_v.addWidget(card)

        self.sim_area.setVisible(True)

    def _feedback(self, liked):
        if not self.current_rec:
            return
        save_feedback(self.current_rec, liked)
        msg = "취향을 기억해둘게요! 💕" if liked else "알겠어요! 다른 스타일로 추천해드릴게요 🔄"
        self.ai_panel.set_message(msg)

    def _add_fav(self):
        if not self.current_rec:
            return
        data = {
            "style": self.current_rec.get("style", ""),
            "mood": self.current_rec.get("mood", ""),
            "outfit": self.current_rec.get("outfit", {})
        }
        ok, msg = add_favorite(data)
        QMessageBox.information(self, "즐겨찾기", msg)
        if ok:
            self.ai_panel.set_message("즐겨찾기에 저장했어요! ⭐")


# ─────────────────────────────────────────────
#  옷장 관리
# ─────────────────────────────────────────────
class AddClothesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("옷 추가")
        self.setMinimumWidth(440)
        self.setStyleSheet(APP_STYLE)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("👗 새 옷 추가")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {C_ACCENT};")
        layout.addWidget(title)
        layout.addWidget(make_sep())

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 검정 후드티")
        self.name_input.setMinimumHeight(38)

        self.cat_combo = QComboBox()
        self.cat_combo.setMinimumHeight(38)
        self.cat_combo.addItems(["상의", "하의", "아우터", "신발", "악세서리"])
        self.cat_combo.currentTextChanged.connect(self._update_types)

        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(38)
        self._update_types("상의")

        self.color_combo = QComboBox()
        self.color_combo.setMinimumHeight(38)
        self.color_combo.addItems(list(COLOR_HEX.keys()))

        form.addRow("이름:", self.name_input)
        form.addRow("카테고리:", self.cat_combo)
        form.addRow("종류:", self.type_combo)
        form.addRow("색상:", self.color_combo)
        layout.addLayout(form)

        # 계절
        season_lbl = QLabel("계절")
        season_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        season_w = QWidget()
        season_h = QHBoxLayout(season_w)
        season_h.setContentsMargins(0, 0, 0, 0)
        season_h.setSpacing(10)
        self.season_checks = {}
        for s in ["봄", "여름", "가을", "겨울"]:
            cb = QCheckBox(s)
            cb.setChecked(True)
            self.season_checks[s] = cb
            season_h.addWidget(cb)
        season_h.addStretch()
        layout.addWidget(season_lbl)
        layout.addWidget(season_w)

        # 무드
        mood_lbl = QLabel("무드")
        mood_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        mood_w = QWidget()
        mood_g = QGridLayout(mood_w)
        mood_g.setContentsMargins(0, 0, 0, 0)
        mood_g.setSpacing(8)
        self.mood_checks = {}
        for i, m in enumerate(["캐주얼", "포멀", "힙", "스트릿", "페미닌", "심플", "빈티지", "모던"]):
            cb = QCheckBox(m)
            self.mood_checks[m] = cb
            mood_g.addWidget(cb, i // 4, i % 4)
        layout.addWidget(mood_lbl)
        layout.addWidget(mood_w)

        # 아이콘 미리보기
        prev_row = QHBoxLayout()
        prev_lbl = QLabel("미리보기:")
        prev_lbl.setStyleSheet(f"font-size: 13px; color: {C_TEXT2};")
        self.preview_lbl = QLabel()
        self.preview_lbl.setFixedSize(70, 70)
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        prev_row.addWidget(prev_lbl)
        prev_row.addWidget(self.preview_lbl)
        prev_row.addStretch()
        layout.addLayout(prev_row)

        self.type_combo.currentTextChanged.connect(self._update_preview)
        self.color_combo.currentTextChanged.connect(self._update_preview)
        self._update_preview()

        layout.addWidget(make_sep())
        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾 저장")
        save_btn.setMinimumHeight(44)
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("ghost_btn")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _update_types(self, cat):
        self.type_combo.clear()
        types = {
            "상의":    ["티셔츠", "셔츠", "후드티", "맨투맨", "니트"],
            "하의":    ["청바지", "슬랙스", "반바지", "치마", "레깅스"],
            "아우터":  ["자켓", "코트", "패딩", "가디건", "점퍼"],
            "신발":    ["운동화", "구두", "부츠", "슬리퍼", "샌들"],
            "악세서리": ["모자", "가방", "목걸이", "시계", "안경"],
        }
        self.type_combo.addItems(types.get(cat, ["기타"]))
        self._update_preview()

    def _update_preview(self):
        type_name = self.type_combo.currentText()
        color_name = self.color_combo.currentText()
        pix = get_svg_pixmap(type_name, color_name, 64)
        if pix:
            self.preview_lbl.setPixmap(pix)
            self.preview_lbl.setStyleSheet("")
        else:
            self.preview_lbl.setText("👗")
            self.preview_lbl.setStyleSheet("font-size: 36px;")

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "알림", "이름을 입력해주세요!")
            return
        seasons = [s for s, cb in self.season_checks.items() if cb.isChecked()]
        moods = [m for m, cb in self.mood_checks.items() if cb.isChecked()]
        if not moods:
            QMessageBox.warning(self, "알림", "무드를 하나 이상 선택해주세요!")
            return
        data = {
            "name": name,
            "category": self.cat_combo.currentText(),
            "type": self.type_combo.currentText(),
            "color": self.color_combo.currentText(),
            "season": seasons,
            "mood": moods,
            "excluded": False,
        }
        add_clothes(data)
        QMessageBox.information(self, "성공", "옷이 추가됐어요! 👗")
        self.accept()


class ClosetPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        # 헤더
        hdr = QHBoxLayout()
        title = QLabel("👗 옷장 관리")
        title.setObjectName("section_title")
        add_btn = QPushButton("➕ 옷 추가")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self._add_dialog)
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        # 필터
        filter_card = make_card()
        fl = QHBoxLayout(filter_card)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["전체", "상의", "하의", "아우터", "신발", "악세서리"])
        self.cat_filter.setMinimumHeight(36)
        self.cat_filter.currentTextChanged.connect(self.refresh)

        self.color_filter = QComboBox()
        self.color_filter.addItems(["전체 색상"] + list(COLOR_HEX.keys()))
        self.color_filter.setMinimumHeight(36)
        self.color_filter.currentTextChanged.connect(self.refresh)

        fl.addWidget(QLabel("카테고리:"))
        fl.addWidget(self.cat_filter)
        fl.addWidget(QLabel("색상:"))
        fl.addWidget(self.color_filter)
        fl.addStretch()
        layout.addWidget(filter_card)

        # 그리드
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.clothes_w = QWidget()
        self.clothes_w.setStyleSheet("background: transparent;")
        self.clothes_g = QGridLayout(self.clothes_w)
        self.clothes_g.setSpacing(14)
        scroll.setWidget(self.clothes_w)
        layout.addWidget(scroll)

        self.refresh()

    def refresh(self):
        while self.clothes_g.count():
            item = self.clothes_g.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cat = self.cat_filter.currentText()
        color = self.color_filter.currentText()
        clothes = load_clothes()
        if cat != "전체":
            clothes = [c for c in clothes if c.get("category") == cat]
        if color != "전체 색상":
            clothes = [c for c in clothes if c.get("color") == color]

        if not clothes:
            empty = QLabel("등록된 옷이 없어요\n➕ 버튼으로 옷을 추가해보세요!")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"font-size: 15px; color: {C_TEXT2}; padding: 40px;")
            self.clothes_g.addWidget(empty, 0, 0, 1, 3)
            return

        row, col = 0, 0
        for idx, item in enumerate(clothes):
            card = self._make_card(item, idx)
            self.clothes_g.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _make_card(self, item, idx):
        card = make_card()
        card.setMinimumHeight(200)
        card.setMaximumWidth(240)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 16, 14, 12)
        cl.setSpacing(6)
        cl.setAlignment(Qt.AlignCenter)

        # SVG 아이콘
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(70, 70)
        icon_lbl.setAlignment(Qt.AlignCenter)
        pix = get_svg_pixmap(item.get("type", "기본"), item.get("color", "검정"), 64)
        if pix:
            icon_lbl.setPixmap(pix)
        else:
            icon_lbl.setText("👗")
            icon_lbl.setStyleSheet("font-size: 36px;")

        # 색상 원
        color_hex = COLOR_HEX.get(item.get("color", ""), "#E0E0E0")
        color_dot = QLabel("●")
        color_dot.setAlignment(Qt.AlignCenter)
        color_dot.setStyleSheet(f"font-size: 18px; color: {color_hex};")

        name = QLabel(item.get("name", ""))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        name.setWordWrap(True)

        info = QLabel(f"{item.get('category','')} · {item.get('color','')}")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet(f"font-size: 11px; color: {C_TEXT2};")

        moods = item.get("mood", [])
        if moods:
            mood_txt = "  ".join(moods[:2])
            mood_lbl = QLabel(mood_txt)
            mood_lbl.setAlignment(Qt.AlignCenter)
            mood_lbl.setStyleSheet(f"""
                font-size: 11px; color: {C_ACCENT};
                background: #FFF0F5; border-radius: 6px; padding: 2px 6px;
            """)
            cl.addWidget(mood_lbl)

        del_btn = QPushButton("삭제")
        del_btn.setObjectName("danger_btn")
        del_btn.setFixedHeight(30)
        del_btn.setStyleSheet(f"""
            QPushButton {{ background: #FFE8EE; color: {C_RED};
                          border: 1px solid {C_RED}; border-radius: 8px;
                          font-size: 11px; font-weight: bold; }}
            QPushButton:hover {{ background: {C_RED}; color: white; }}
        """)
        del_btn.clicked.connect(lambda checked=False, i=idx: self._delete(i))

        cl.addWidget(icon_lbl, alignment=Qt.AlignCenter)
        cl.addWidget(color_dot)
        cl.addWidget(name)
        cl.addWidget(info)
        cl.addWidget(del_btn, alignment=Qt.AlignCenter)
        return card

    def _delete(self, idx):
        reply = QMessageBox.question(self, "삭제", "정말 삭제할까요?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_clothes(idx)
            self.refresh()

    def _add_dialog(self):
        dlg = AddClothesDialog(self)
        if dlg.exec():
            self.refresh()


# ─────────────────────────────────────────────
#  캘린더 페이지
# ─────────────────────────────────────────────
class SelectOutfitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("코디 선택")
        self.setMinimumSize(480, 380)
        self.setStyleSheet(APP_STYLE)
        self.selected_outfit = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("👗 착용 코디 선택")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C_ACCENT};")
        layout.addWidget(title)

        tab_row = QHBoxLayout()
        manual_btn = QPushButton("직접 선택")
        manual_btn.setObjectName("ghost_btn")
        manual_btn.clicked.connect(self._show_manual)
        fav_btn = QPushButton("즐겨찾기에서")
        fav_btn.setObjectName("ghost_btn")
        fav_btn.clicked.connect(self._show_fav)
        tab_row.addWidget(manual_btn)
        tab_row.addWidget(fav_btn)
        tab_row.addStretch()
        layout.addLayout(tab_row)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.manual_w = QWidget()
        self._build_manual()
        self.fav_w = QWidget()
        self._build_fav()
        self.stack.addWidget(self.manual_w)
        self.stack.addWidget(self.fav_w)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("확인")
        ok_btn.setMinimumHeight(42)
        ok_btn.clicked.connect(self._confirm)
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("ghost_btn")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _build_manual(self):
        form = QFormLayout(self.manual_w)
        form.setSpacing(10)
        self.top_combo = QComboBox()
        self.bottom_combo = QComboBox()
        self.outer_combo = QComboBox()
        for combo in [self.top_combo, self.bottom_combo, self.outer_combo]:
            combo.setMinimumHeight(38)
        self.top_combo.addItem("선택 안함")
        for c in filter_clothes(category="상의"):
            self.top_combo.addItem(f"{c['name']} ({c['color']})", c)
        self.bottom_combo.addItem("선택 안함")
        for c in filter_clothes(category="하의"):
            self.bottom_combo.addItem(f"{c['name']} ({c['color']})", c)
        self.outer_combo.addItem("선택 안함")
        for c in filter_clothes(category="아우터"):
            self.outer_combo.addItem(f"{c['name']} ({c['color']})", c)
        form.addRow("상의:", self.top_combo)
        form.addRow("하의:", self.bottom_combo)
        form.addRow("아우터:", self.outer_combo)

    def _build_fav(self):
        v = QVBoxLayout(self.fav_w)
        favs = load_favorite()
        if not favs:
            v.addWidget(QLabel("즐겨찾기가 비어있어요"))
            return
        self.favs = favs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        w = QWidget()
        wv = QVBoxLayout(w)
        for i, fav in enumerate(favs):
            out = fav.get("outfit", {})
            parts = []
            for p, lbl in [("top","상의"),("bottom","하의"),("outer","아우터")]:
                it = out.get(p)
                if it and isinstance(it, dict):
                    parts.append(f"{lbl}: {it['name']}")
            btn = QPushButton(f"🎨 {fav.get('style','스타일')}  " + "  ".join(parts))
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked=False, idx=i: self._select_fav(idx))
            wv.addWidget(btn)
        wv.addStretch()
        scroll.setWidget(w)
        v.addWidget(scroll)

    def _show_manual(self):
        self.stack.setCurrentIndex(0)

    def _show_fav(self):
        self.stack.setCurrentIndex(1)

    def _select_fav(self, idx):
        self.selected_outfit = self.favs[idx].get("outfit", {})
        self.accept()

    def _confirm(self):
        if self.stack.currentIndex() == 0:
            outfit = {}
            if self.top_combo.currentIndex() > 0:
                outfit["top"] = self.top_combo.currentData()
            if self.bottom_combo.currentIndex() > 0:
                outfit["bottom"] = self.bottom_combo.currentData()
            if self.outer_combo.currentIndex() > 0:
                outfit["outer"] = self.outer_combo.currentData()
            if not outfit:
                QMessageBox.warning(self, "알림", "옷을 하나 이상 선택해주세요!")
                return
            self.selected_outfit = outfit
        self.accept()


class CalendarPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_date = None
        self.selected_outfit = None
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setSpacing(20)
        root.setContentsMargins(0, 0, 0, 0)

        # 왼쪽: 캘린더
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(12)
        lv.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📅 캘린더 & 다이어리")
        title.setObjectName("section_title")
        lv.addWidget(title)

        self.cal = CustomCalendar()
        self.cal.dateClicked.connect(self._date_selected)
        lv.addWidget(self.cal)
        lv.addStretch()

        # 오른쪽: 기록 패널
        right = make_card()
        right.setMinimumWidth(320)
        rv = QVBoxLayout(right)
        rv.setSpacing(12)
        rv.setContentsMargins(20, 20, 20, 20)

        self.date_lbl = QLabel("날짜를 선택하세요")
        self.date_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C_TEXT};")
        rv.addWidget(self.date_lbl)
        rv.addWidget(make_sep())

        # 기분 선택 (이모지 버튼)
        mood_lbl = QLabel("오늘의 기분")
        mood_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        rv.addWidget(mood_lbl)

        mood_row = QHBoxLayout()
        mood_row.setSpacing(6)
        self.mood_btns = {}
        self.mood_btn_group = QButtonGroup(self)
        self.mood_btn_group.setExclusive(True)
        for mood, emoji in MOOD_EMOJI.items():
            btn = QPushButton(emoji)
            btn.setCheckable(True)
            btn.setFixedSize(44, 44)
            btn.setToolTip(mood)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 20px;
                    background: #FFF0F5;
                    border: 2px solid {C_BORDER};
                    border-radius: 10px;
                }}
                QPushButton:checked {{
                    background: {C_BTN};
                    border-color: {C_ACCENT};
                }}
                QPushButton:hover {{ border-color: {C_ACCENT}; }}
            """)
            self.mood_btns[mood] = btn
            self.mood_btn_group.addButton(btn)
            mood_row.addWidget(btn)
        mood_row.addStretch()
        rv.addLayout(mood_row)

        # 날씨
        weather_lbl = QLabel("날씨")
        weather_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        self.weather_combo = QComboBox()
        self.weather_combo.setMinimumHeight(36)
        self.weather_combo.addItems(["맑음", "흐림", "비", "눈", "더움", "추움"])
        rv.addWidget(weather_lbl)
        rv.addWidget(self.weather_combo)

        # 메모
        memo_lbl = QLabel("메모 📝")
        memo_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        self.memo_input = QTextEdit()
        self.memo_input.setPlaceholderText("오늘 기록을 남겨보세요...")
        self.memo_input.setMaximumHeight(90)
        rv.addWidget(memo_lbl)
        rv.addWidget(self.memo_input)

        # 코디
        outfit_lbl = QLabel("착용 코디 👔")
        outfit_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        self.outfit_lbl = QLabel("코디를 선택하세요")
        self.outfit_lbl.setStyleSheet(f"""
            background: #FFF0F5;
            border: 1.5px solid {C_BORDER};
            border-radius: 10px;
            padding: 10px;
            font-size: 12px;
            color: {C_TEXT2};
        """)
        self.outfit_lbl.setWordWrap(True)
        select_btn = QPushButton("코디 선택하기")
        select_btn.setMinimumHeight(38)
        select_btn.setObjectName("ghost_btn")
        select_btn.clicked.connect(self._select_outfit)
        rv.addWidget(outfit_lbl)
        rv.addWidget(self.outfit_lbl)
        rv.addWidget(select_btn)

        rv.addWidget(make_sep())

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾 저장")
        save_btn.setMinimumHeight(42)
        save_btn.clicked.connect(self._save)
        del_btn = QPushButton("🗑️ 삭제")
        del_btn.setObjectName("danger_btn")
        del_btn.setMinimumHeight(42)
        del_btn.setStyleSheet(f"""
            QPushButton {{ background: #FFE8EE; color: {C_RED};
                          border: 1.5px solid {C_RED}; border-radius: 12px;
                          font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background: {C_RED}; color: white; }}
        """)
        del_btn.clicked.connect(self._delete)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(del_btn)
        rv.addLayout(btn_row)
        rv.addStretch()

        root.addWidget(left, 3)
        root.addWidget(right, 2)

    def _date_selected(self, date_str):
        self.selected_date = date_str
        parts = date_str.split("-")
        self.date_lbl.setText(f"📅 {parts[0]}년 {int(parts[1])}월 {int(parts[2])}일")

        record = load_schedule(date_str)
        # reset
        for btn in self.mood_btns.values():
            btn.setChecked(False)
        self.weather_combo.setCurrentIndex(0)
        self.memo_input.clear()
        self.outfit_lbl.setText("코디를 선택하세요")
        self.selected_outfit = None

        if record:
            mood = record.get("mood", "")
            if mood in self.mood_btns:
                self.mood_btns[mood].setChecked(True)
            weather = record.get("weather", "맑음")
            idx = self.weather_combo.findText(weather)
            if idx >= 0:
                self.weather_combo.setCurrentIndex(idx)
            self.memo_input.setText(record.get("memo", ""))
            outfit = record.get("outfit", {})
            if outfit:
                self.selected_outfit = outfit
                self._display_outfit(outfit)

    def _get_selected_mood(self):
        for mood, btn in self.mood_btns.items():
            if btn.isChecked():
                return mood
        return "행복"

    def _select_outfit(self):
        dlg = SelectOutfitDialog(self)
        if dlg.exec() and dlg.selected_outfit:
            self.selected_outfit = dlg.selected_outfit
            self._display_outfit(self.selected_outfit)

    def _display_outfit(self, outfit):
        parts = []
        for p, lbl in [("top","상의"),("bottom","하의"),("outer","아우터")]:
            it = outfit.get(p)
            if it:
                name = it["name"] if isinstance(it, dict) else str(it)
                parts.append(f"{lbl}: {name}")
        self.outfit_lbl.setText("\n".join(parts) if parts else "코디 없음")

    def _save(self):
        if not self.selected_date:
            QMessageBox.warning(self, "알림", "날짜를 먼저 선택해주세요!")
            return
        if not self.selected_outfit:
            QMessageBox.warning(self, "알림", "코디를 선택해주세요!")
            return
        save_schedule(
            self.selected_date,
            self.selected_outfit,
            self._get_selected_mood(),
            self.weather_combo.currentText(),
            self.memo_input.toPlainText()
        )
        self.cal.refresh_records()
        QMessageBox.information(self, "저장", "저장됐어요! 💕")

    def _delete(self):
        if not self.selected_date:
            QMessageBox.warning(self, "알림", "날짜를 먼저 선택해주세요!")
            return
        reply = QMessageBox.question(self, "삭제", "이 날의 기록을 삭제할까요?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_schedule(self.selected_date)
            self.cal.refresh_records()
            self._date_selected(self.selected_date)
            QMessageBox.information(self, "삭제", "삭제됐어요!")


# ─────────────────────────────────────────────
#  즐겨찾기 페이지
# ─────────────────────────────────────────────
class FavoritePage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QHBoxLayout()
        title = QLabel("⭐ 즐겨찾기")
        title.setObjectName("section_title")
        stat_btn = QPushButton("📊 스타일 통계")
        stat_btn.setMinimumHeight(38)
        stat_btn.clicked.connect(self._show_stats)
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(stat_btn)
        layout.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.fav_w = QWidget()
        self.fav_w.setStyleSheet("background: transparent;")
        self.fav_v = QVBoxLayout(self.fav_w)
        self.fav_v.setSpacing(12)
        scroll.setWidget(self.fav_w)
        layout.addWidget(scroll)

        self.refresh()

    def refresh(self):
        while self.fav_v.count():
            item = self.fav_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        favs = load_favorite()
        if not favs:
            empty = QLabel("즐겨찾기가 비어있어요\n코디 추천에서 마음에 드는 스타일을 저장해보세요 ⭐")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"font-size: 15px; color: {C_TEXT2}; padding: 40px;")
            self.fav_v.addWidget(empty)
            self.fav_v.addStretch()
            return

        for idx, fav in enumerate(favs):
            card = self._make_card(fav, idx)
            self.fav_v.addWidget(card)
        self.fav_v.addStretch()

    def _make_card(self, fav, idx):
        card = make_card()
        row = QHBoxLayout(card)
        row.setContentsMargins(18, 14, 18, 14)
        row.setSpacing(14)

        # 아이콘 영역
        icons_v = QHBoxLayout()
        icons_v.setSpacing(6)
        outfit = fav.get("outfit", {})
        for part in ["top", "bottom", "outer"]:
            it = outfit.get(part)
            if it and isinstance(it, dict):
                pix = get_svg_pixmap(it.get("type", "기본"), it.get("color", "검정"), 48)
                il = QLabel()
                il.setFixedSize(52, 52)
                il.setAlignment(Qt.AlignCenter)
                if pix:
                    il.setPixmap(pix)
                else:
                    il.setText("👗")
                    il.setStyleSheet("font-size: 24px;")
                icons_v.addWidget(il)

        info = QVBoxLayout()
        info.setSpacing(4)

        style_lbl = QLabel(f"🎨 {fav.get('style', '스타일')}")
        style_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {C_TEXT};")

        mood_lbl = QLabel(f"💭 {fav.get('mood', '')}" if fav.get("mood") else "")
        mood_lbl.setStyleSheet(f"font-size: 12px; color: {C_TEXT2};")

        parts_strs = []
        for p, lbl in [("top","상의"),("bottom","하의"),("outer","아우터")]:
            it = outfit.get(p)
            if it and isinstance(it, dict):
                parts_strs.append(f"{lbl}: {it['name']}")
        detail = QLabel("  ·  ".join(parts_strs))
        detail.setStyleSheet(f"font-size: 12px; color: {C_TEXT2};")
        detail.setWordWrap(True)

        info.addLayout(icons_v)
        info.addWidget(style_lbl)
        info.addWidget(mood_lbl)
        info.addWidget(detail)

        del_btn = QPushButton("삭제")
        del_btn.setFixedSize(60, 34)
        del_btn.setStyleSheet(f"""
            QPushButton {{ background: #FFE8EE; color: {C_RED};
                          border: 1px solid {C_RED}; border-radius: 8px;
                          font-size: 11px; font-weight: bold; }}
            QPushButton:hover {{ background: {C_RED}; color: white; }}
        """)
        del_btn.clicked.connect(lambda checked=False, i=idx: self._delete(i))

        row.addLayout(info, 1)
        row.addWidget(del_btn, alignment=Qt.AlignTop)
        return card

    def _delete(self, idx):
        reply = QMessageBox.question(self, "삭제", "즐겨찾기에서 삭제할까요?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_favorite(idx)
            self.refresh()

    def _show_stats(self):
        stats = analyze_style()
        dlg = QDialog(self)
        dlg.setWindowTitle("스타일 통계")
        dlg.setMinimumSize(360, 300)
        dlg.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(QLabel(f"<b>📊 총 즐겨찾기: {stats['total_favorites']}개</b>"))

        html = "<b>🎨 선호 스타일</b><br>"
        for s, c in sorted(stats["style_frequency"].items(), key=lambda x: x[1], reverse=True):
            html += f"&nbsp;• {s}: {c}회<br>"

        html += "<br><b>🎨 선호 색상</b><br>"
        for s, c in sorted(stats["color_frequency"].items(), key=lambda x: x[1], reverse=True)[:5]:
            html += f"&nbsp;• {s}: {c}회<br>"

        lbl = QLabel(html)
        lbl.setTextFormat(Qt.RichText)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"font-size: 13px; color: {C_TEXT};")
        layout.addWidget(lbl)

        close_btn = QPushButton("닫기")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec()


# ─────────────────────────────────────────────
#  사이드바 날씨/시간 위젯
# ─────────────────────────────────────────────
class SidebarInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)
        self._update_time()

    def _build(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(4)

        self.weather_lbl = QLabel("날씨 로딩 중...")
        self.weather_lbl.setWordWrap(True)
        self.weather_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px;")

        self.date_lbl = QLabel()
        self.date_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px; font-weight: bold;")

        self.time_lbl = QLabel()
        self.time_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.time_lbl.setAlignment(Qt.AlignCenter)

        v.addWidget(self.time_lbl, alignment=Qt.AlignCenter)
        v.addWidget(self.date_lbl, alignment=Qt.AlignCenter)
        v.addWidget(self.weather_lbl, alignment=Qt.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,0.3);")
        v.insertWidget(0, sep)

    def _update_time(self):
        from datetime import datetime
        now = datetime.now()
        self.time_lbl.setText(now.strftime("%H:%M:%S"))
        self.date_lbl.setText(now.strftime("%Y.%m.%d (%a)").replace(
            "Mon","월").replace("Tue","화").replace("Wed","수").replace(
            "Thu","목").replace("Fri","금").replace("Sat","토").replace("Sun","일"))

    def set_weather(self, text):
        self.weather_lbl.setText(text)


# ─────────────────────────────────────────────
#  메인 윈도우
# ─────────────────────────────────────────────
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💕 StyleMate")
        self.resize(1440, 900)
        self.setStyleSheet(APP_STYLE)

        # OpenAI 초기화
        try:
            init_openai()
        except Exception:
            pass

        current = get_current_user()
        if current:
            self.show_main_app()
        else:
            self.show_login()

    def _clear_layout(self):
        old = self.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)

    def show_login(self):
        self._clear_layout()
        page = LoginPage(self)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(page)

    def show_main_app(self):
        self._clear_layout()

        root = QHBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── 사이드바
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sv = QVBoxLayout(sidebar)
        sv.setSpacing(4)
        sv.setContentsMargins(16, 24, 16, 16)

        # 로고
        logo = QLabel("💕 StyleMate")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")

        username = get_current_user() or ""
        user_lbl = QLabel(f"👤 {username}님")
        user_lbl.setAlignment(Qt.AlignCenter)
        user_lbl.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.85);")

        sv.addWidget(logo)
        sv.addWidget(user_lbl)
        sv.addSpacing(16)

        # 페이지 스택
        self.stack = QStackedWidget()

        self.home_page = HomePage(self)
        self.closet_page = ClosetPage()
        self.calendar_page = CalendarPage()
        self.fav_page = FavoritePage()

        for page in [self.home_page, self.closet_page, self.calendar_page, self.fav_page]:
            self.stack.addWidget(page)

        # 메뉴 버튼
        menu_items = [
            ("🏠  홈 & 코디 추천", self.home_page),
            ("👗  옷장 관리",       self.closet_page),
            ("📅  캘린더",          self.calendar_page),
            ("⭐  즐겨찾기",        self.fav_page),
        ]

        self.sidebar_btns = []
        for label, page in menu_items:
            btn = QPushButton(label)
            btn.setObjectName("sidebar_btn")
            btn.setCheckable(True)
            btn.setMinimumHeight(48)
            btn.clicked.connect(lambda checked=False, p=page: self._switch(p))
            sv.addWidget(btn)
            self.sidebar_btns.append(btn)

        sv.addStretch()

        # 날씨/시간
        self.info_widget = SidebarInfoWidget()
        sv.addWidget(self.info_widget)
        sv.addSpacing(8)

        # 로그아웃
        logout_btn = QPushButton("🚪  로그아웃")
        logout_btn.setObjectName("sidebar_btn")
        logout_btn.setMinimumHeight(44)
        logout_btn.clicked.connect(self._logout)
        sv.addWidget(logout_btn)

        # 컨텐츠 영역
        content = QWidget()
        content.setStyleSheet(f"background: {C_BG};")
        cv = QVBoxLayout(content)
        cv.setContentsMargins(28, 24, 28, 24)
        cv.addWidget(self.stack)

        root.addWidget(sidebar)
        root.addWidget(content, 1)

        # 첫 번째 버튼 활성화
        self.sidebar_btns[0].setChecked(True)
        self.stack.setCurrentWidget(self.home_page)

        # 날씨 정보 사이드바에도 표시
        self._update_sidebar_weather()

    def _switch(self, page):
        self.stack.setCurrentWidget(page)
        for btn in self.sidebar_btns:
            btn.setChecked(False)
        sender = self.sender()
        if sender:
            sender.setChecked(True)

    def _update_sidebar_weather(self):
        from features.weather_api import get_weather, get_weather_icon_emoji
        from features.settings_manager import get_weather_key, get_default_city
        key = get_weather_key()
        city = get_default_city()
        if key:
            data = get_weather(city, key)
            if not data.get("error"):
                emoji = get_weather_icon_emoji(data["weather"])
                text = f"{emoji} {data['city']} {data['weather']} {data['temperature']}°C"
                self.info_widget.set_weather(text)
            else:
                self.info_widget.set_weather("날씨 정보 없음")
        else:
            self.info_widget.set_weather("⚙ config.py에 날씨 키 입력")

    def _logout(self):
        reply = QMessageBox.question(self, "로그아웃", "로그아웃 하시겠어요?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from features.user_manager import CURRENT_USER_FILE
                if os.path.exists(CURRENT_USER_FILE):
                    os.remove(CURRENT_USER_FILE)
            except Exception:
                pass
            self.show_login()
