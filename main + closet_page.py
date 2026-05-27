"""
StyleMate - 메인 UI
옷장 관리 페이지와 연동 가능
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QLineEdit, QComboBox, QScrollArea, QGridLayout,
    QDialog, QCheckBox, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from closet_page import (
    load_clothes, add_clothes, delete_clothes, update_clothes, filter_clothes,
    CATEGORIES, COLORS, MOODS, COLOR_HEX, CATEGORY_BADGE_COLOR,
)

# ──────────────────────────────────────────────────────
# 공통 스타일
# ──────────────────────────────────────────────────────
PAGE_STYLE = """
QWidget {
    background-color: #F5F5F5;
    font-family: 'Segoe UI';
}
QFrame {
    background-color: white;
    border-radius: 15px;
}
QPushButton {
    background-color: #CDB4FF;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #B392F0;
}
QLabel {
    color: #333333;
}
"""

# ──────────────────────────────────────────────────────
# 옷 추가 / 수정 다이얼로그
# ──────────────────────────────────────────────────────
class ClothesDialog(QDialog):
    """
    옷 추가 및 수정에 공통으로 사용하는 다이얼로그.
    item=None  → 추가 모드
    item=dict  → 수정 모드 (기존 값 자동 채워짐)
    """
    def __init__(self, parent=None, item: dict = None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("옷 추가하기" if item is None else "옷 수정하기")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog   { background-color: #F5F5F5; font-family: 'Segoe UI'; }
            QLabel    { color: #444; font-size: 13px; }
            QLineEdit, QComboBox {
                border: 1px solid #DDD; border-radius: 8px;
                padding: 8px 10px; background: white; font-size: 13px;
            }
            QScrollArea { border: 1px solid #DDD; border-radius: 8px; background: white; }
            QCheckBox   { font-size: 12px; color: #444; spacing: 6px; }
        """)
        self._build_ui()
        if item:
            self._populate(item)

    # ── UI 구성 ──────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout()
        root.setSpacing(10)
        root.setContentsMargins(28, 24, 28, 24)

        # 제목
        title_lbl = QLabel("✚ 옷 추가하기" if self.item is None else "✎ 옷 수정하기")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        root.addWidget(title_lbl)
        root.addSpacing(4)

        # 이름
        root.addWidget(self._section_label("이름 *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예) 검정 후드티")
        root.addWidget(self.name_input)

        # 카테고리 + 세부유형 (가로 나란히)
        cat_row = QHBoxLayout()
        cat_row.setSpacing(12)

        cat_col = QVBoxLayout()
        cat_col.addWidget(self._section_label("카테고리 *"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(list(CATEGORIES.keys()))
        cat_col.addWidget(self.category_combo)

        sub_col = QVBoxLayout()
        sub_col.addWidget(self._section_label("세부 유형"))
        self.subcategory_combo = QComboBox()
        sub_col.addWidget(self.subcategory_combo)

        cat_row.addLayout(cat_col)
        cat_row.addLayout(sub_col)
        root.addLayout(cat_row)

        # 색상
        root.addWidget(self._section_label("색상 *"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(COLORS)
        root.addWidget(self.color_combo)

        # 무드 (체크박스 멀티셀렉트)
        root.addWidget(self._section_label("무드 * (복수 선택 가능)"))

        mood_scroll = QScrollArea()
        mood_scroll.setFixedHeight(130)
        mood_scroll.setWidgetResizable(True)

        mood_inner = QWidget()
        mood_inner.setStyleSheet("background: white;")
        mood_grid = QGridLayout()
        mood_grid.setSpacing(6)
        mood_grid.setContentsMargins(10, 10, 10, 10)

        self.mood_checks: dict[str, QCheckBox] = {}
        for i, m in enumerate(MOODS):
            cb = QCheckBox(m)
            self.mood_checks[m] = cb
            mood_grid.addWidget(cb, i // 4, i % 4)

        mood_inner.setLayout(mood_grid)
        mood_scroll.setWidget(mood_inner)
        root.addWidget(mood_scroll)

        # 추천 제외 옵션
        self.exclude_check = QCheckBox("이 옷을 코디 추천에서 제외")
        self.exclude_check.setStyleSheet("color: #888; font-size: 12px;")
        root.addWidget(self.exclude_check)

        root.addStretch()

        # 하단 버튼
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("취소")
        cancel_btn.setStyleSheet("""
            QPushButton { background-color: #EEE; color: #555; border:none;
                          border-radius:10px; padding:10px; font-size:14px; font-weight:bold; }
            QPushButton:hover { background-color: #DDD; }
        """)
        save_btn = QPushButton("저장")

        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

        self.setLayout(root)

        # 카테고리 변경 → 세부유형 갱신
        self.category_combo.currentTextChanged.connect(self._update_subcategory)
        self._update_subcategory(self.category_combo.currentText())

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 12px; color: #666; margin-top: 4px;")
        return lbl

    def _update_subcategory(self, category: str):
        self.subcategory_combo.clear()
        self.subcategory_combo.addItems(CATEGORIES.get(category, []))

    # ── 수정 모드: 기존 값 채우기 ────────────────────
    def _populate(self, item: dict):
        self.name_input.setText(item.get("name", ""))

        cat = item.get("category", "")
        if cat in CATEGORIES:
            self.category_combo.setCurrentText(cat)
            self._update_subcategory(cat)
            sub = item.get("subcategory", "")
            idx = self.subcategory_combo.findText(sub)
            if idx >= 0:
                self.subcategory_combo.setCurrentIndex(idx)

        color = item.get("color", "")
        idx = self.color_combo.findText(color)
        if idx >= 0:
            self.color_combo.setCurrentIndex(idx)

        for tag in item.get("mood", []):
            if tag in self.mood_checks:
                self.mood_checks[tag].setChecked(True)

        self.exclude_check.setChecked(item.get("exclude_from_recommendation", False))

    # ── 저장 시 유효성 확인 ──────────────────────────
    def _on_save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "입력 오류", "옷 이름을 입력해주세요.")
            return
        if not any(cb.isChecked() for cb in self.mood_checks.values()):
            QMessageBox.warning(self, "입력 오류", "무드를 최소 1개 선택해주세요.")
            return
        self.accept()

    # ── 외부에서 결과 수집 ───────────────────────────
    def get_data(self) -> dict:
        return {
            "name":        self.name_input.text().strip(),
            "category":    self.category_combo.currentText(),
            "subcategory": self.subcategory_combo.currentText(),
            "color":       self.color_combo.currentText(),
            "mood":        [m for m, cb in self.mood_checks.items() if cb.isChecked()],
            "exclude_from_recommendation": self.exclude_check.isChecked(),
        }


# ──────────────────────────────────────────────────────
# 개별 옷 카드 위젯
# ──────────────────────────────────────────────────────
class ClothesCard(QFrame):
    """옷 한 벌의 정보를 카드 형태로 표시하는 위젯"""
    def __init__(self, username: str, item: dict, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.username = username
        self.item = item
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.setFixedWidth(210)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 14px;
                border: 1px solid #EBEBEB;
            }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(7)

        category = self.item.get("category", "")
        subcategory = self.item.get("subcategory", "")
        color = self.item.get("color", "")
        color_hex = COLOR_HEX.get(color, "#DDD")
        badge_bg = CATEGORY_BADGE_COLOR.get(category, "#EEE")

        # ── 카테고리 배지
        badge_frame = QFrame()
        badge_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {badge_bg};
                border-radius: 8px;
                border: none;
            }}
        """)
        badge_layout = QHBoxLayout()
        badge_layout.setContentsMargins(8, 4, 8, 4)
        badge_lbl = QLabel(f"{category}  ·  {subcategory}" if subcategory else category)
        badge_lbl.setStyleSheet("font-size: 11px; color: #666; background: transparent;")
        badge_layout.addWidget(badge_lbl)
        badge_frame.setLayout(badge_layout)
        layout.addWidget(badge_frame)

        # ── 옷 이름
        name_lbl = QLabel(self.item.get("name", ""))
        name_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #222;")
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl)

        # ── 색상 chip
        color_lbl = QLabel(f"●  {color}")
        # 어두운 색은 테두리 효과
        txt_color = color_hex if color not in ("화이트", "아이보리", "화이트") else "#AAAAAA"
        color_lbl.setStyleSheet(f"font-size: 13px; color: {txt_color};")
        layout.addWidget(color_lbl)

        # ── 무드 태그 (최대 3개)
        mood_row = QHBoxLayout()
        mood_row.setSpacing(4)
        mood_row.setContentsMargins(0, 0, 0, 0)
        for tag in self.item.get("mood", [])[:3]:
            tag_lbl = QLabel(tag)
            tag_lbl.setStyleSheet("""
                background-color: #F0EAFF; color: #7B5EA7;
                border-radius: 8px; padding: 2px 8px;
                font-size: 10px; border: none;
            """)
            mood_row.addWidget(tag_lbl)
        mood_row.addStretch()
        layout.addLayout(mood_row)

        # ── 추천 제외 표시
        if self.item.get("exclude_from_recommendation"):
            excl_lbl = QLabel("추천 제외")
            excl_lbl.setStyleSheet("""
                background-color: #FFF3E0; color: #E65100;
                border-radius: 6px; padding: 2px 8px;
                font-size: 10px; border: none;
            """)
            layout.addWidget(excl_lbl)

        layout.addStretch()

        # ── 수정 / 삭제 버튼
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        edit_btn = QPushButton("수정")
        edit_btn.setFixedHeight(30)
        edit_btn.setStyleSheet("""
            QPushButton { background-color: #CDB4FF; color: white; border: none;
                          border-radius: 8px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #B392F0; }
        """)
        del_btn = QPushButton("삭제")
        del_btn.setFixedHeight(30)
        del_btn.setStyleSheet("""
            QPushButton { background-color: #FFE4E4; color: #C62828; border: none;
                          border-radius: 8px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #FFCDD2; }
        """)

        edit_btn.clicked.connect(lambda: self.on_edit(self.item))
        del_btn.clicked.connect(lambda: self.on_delete(self.item))

        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)


# ──────────────────────────────────────────────────────
# 옷장 관리 페이지 (ClosetPage) — 완전 구현
# ──────────────────────────────────────────────────────
class ClosetPage(QWidget):
    """
    wardrobe_manager의 4개 핵심 함수와 연동된 옷장 관리 화면.
    MainWindow에서 set_username(name)을 호출하면 해당 사용자 데이터를 로드합니다.
    """
    COLS = 4  # 그리드 열 수

    def __init__(self):
        super().__init__()
        self.username = ""
        self._build_ui()

    def set_username(self, username: str):
        """로그인 후 MainWindow에서 호출"""
        self.username = username
        self.refresh()

    # ── UI 구성 ──────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        # ── 타이틀 바
        title_bar = QHBoxLayout()
        title_lbl = QLabel("옷장 관리")
        title_lbl.setStyleSheet("font-size: 28px; font-weight: bold;")
        add_btn = QPushButton("＋  옷 추가")
        add_btn.setFixedWidth(130)
        add_btn.clicked.connect(self._open_add_dialog)
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()
        title_bar.addWidget(add_btn)
        root.addLayout(title_bar)

        # ── 필터 바
        filter_frame = QFrame()
        filter_frame.setStyleSheet("QFrame { background: white; border-radius: 12px; }")
        filter_lay = QHBoxLayout()
        filter_lay.setContentsMargins(16, 10, 16, 10)
        filter_lay.setSpacing(10)

        combo_style = """
            QComboBox { border:1px solid #EEE; border-radius:8px;
                        padding:5px 10px; background:#FAFAFA; font-size:12px; }
            QComboBox::drop-down { border:none; }
        """
        search_style = """
            QLineEdit { border:1px solid #EEE; border-radius:8px;
                        padding:5px 10px; background:#FAFAFA; font-size:12px; }
        """

        self.cat_filter = QComboBox()
        self.cat_filter.addItem("전체 카테고리")
        self.cat_filter.addItems(list(CATEGORIES.keys()))
        self.cat_filter.setStyleSheet(combo_style)
        self.cat_filter.setFixedWidth(130)

        self.color_filter = QComboBox()
        self.color_filter.addItem("전체 색상")
        self.color_filter.addItems(COLORS)
        self.color_filter.setStyleSheet(combo_style)
        self.color_filter.setFixedWidth(110)

        self.mood_filter = QComboBox()
        self.mood_filter.addItem("전체 무드")
        self.mood_filter.addItems(MOODS)
        self.mood_filter.setStyleSheet(combo_style)
        self.mood_filter.setFixedWidth(130)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  이름으로 검색")
        self.search_input.setStyleSheet(search_style)
        self.search_input.setFixedWidth(160)

        filter_lay.addWidget(self.cat_filter)
        filter_lay.addWidget(self.color_filter)
        filter_lay.addWidget(self.mood_filter)
        filter_lay.addWidget(self.search_input)
        filter_lay.addStretch()
        filter_frame.setLayout(filter_lay)
        root.addWidget(filter_frame)

        # ── 통계 레이블
        self.stats_lbl = QLabel("")
        self.stats_lbl.setStyleSheet("color: #999; font-size: 12px; margin-left: 4px;")
        root.addWidget(self.stats_lbl)

        # ── 스크롤 그리드
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_widget.setLayout(self.grid_layout)
        scroll.setWidget(self.grid_widget)
        root.addWidget(scroll)

        self.setLayout(root)

        # 필터 시그널 연결
        self.cat_filter.currentTextChanged.connect(self.refresh)
        self.color_filter.currentTextChanged.connect(self.refresh)
        self.mood_filter.currentTextChanged.connect(self.refresh)
        self.search_input.textChanged.connect(self.refresh)

    # ── 그리드 새로고침 ──────────────────────────────
    def refresh(self):
        """필터 조건에 맞게 옷 목록을 다시 그립니다."""
        if not self.username:
            return

        cat   = self.cat_filter.currentText()
        color = self.color_filter.currentText()
        mood  = self.mood_filter.currentText()
        query = self.search_input.text().strip()

        # wardrobe_manager.filter_clothes() 호출
        clothes = filter_clothes(
            self.username,
            category  = None if cat   == "전체 카테고리" else cat,
            color     = None if color == "전체 색상"    else color,
            mood_tags = None if mood  == "전체 무드"    else [mood],
            exclude_hidden = False,
        )

        # 이름 검색 (로컬 필터)
        if query:
            clothes = [c for c in clothes if query in c.get("name", "")]

        # 기존 카드 전부 제거
        while self.grid_layout.count():
            w = self.grid_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        # 카드 추가
        if not clothes:
            empty = QLabel("등록된 옷이 없습니다.\n'＋ 옷 추가' 버튼으로 첫 번째 옷을 등록해보세요!")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #BBBBBB; font-size: 14px;")
            self.grid_layout.addWidget(empty, 0, 0, 1, self.COLS)
        else:
            for i, item in enumerate(clothes):
                card = ClothesCard(self.username, item, self._open_edit_dialog, self._handle_delete)
                self.grid_layout.addWidget(card, i // self.COLS, i % self.COLS)

        # 통계 업데이트
        total = len(load_clothes(self.username))
        self.stats_lbl.setText(f"총 {total}벌 등록  ·  현재 {len(clothes)}벌 표시")

    # ── 추가 다이얼로그 ──────────────────────────────
    def _open_add_dialog(self):
        if not self.username:
            QMessageBox.warning(self, "알림", "홈 화면에서 이름을 입력하고 시작해주세요.")
            return
        dlg = ClothesDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if add_clothes(self.username, data):
                self.refresh()

    # ── 수정 다이얼로그 ──────────────────────────────
    def _open_edit_dialog(self, item: dict):
        dlg = ClothesDialog(self, item=item)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            fields = {
                "name":        data["name"],
                "category":    data["category"],
                "subcategory": data["subcategory"],
                "color":       data["color"],
                "mood":        data["mood"],
                "exclude_from_recommendation": data["exclude_from_recommendation"],
            }
            if update_clothes(self.username, item["id"], fields):
                self.refresh()

    # ── 삭제 확인 ────────────────────────────────────
    def _handle_delete(self, item: dict):
        reply = QMessageBox.question(
            self, "삭제 확인",
            f"'{item['name']}'을(를) 옷장에서 삭제할까요?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            if delete_clothes(self.username, item["id"]):
                self.refresh()


# ──────────────────────────────────────────────────────
# 홈 화면 (이름 입력 → 시작)
# ──────────────────────────────────────────────────────
class HomePage(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("StyleMate")
        title.setStyleSheet("font-size: 40px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("AI 패션 코디 추천 프로그램")
        subtitle.setStyleSheet("font-size: 18px; color: #888;")
        subtitle.setAlignment(Qt.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("이름을 입력하세요")
        self.name_input.setFixedWidth(280)
        self.name_input.setStyleSheet("""
            QLineEdit { border: 1px solid #DDD; border-radius: 10px;
                        padding: 10px 16px; font-size: 15px; background: white; }
        """)
        self.name_input.returnPressed.connect(self._handle_start)

        start_btn = QPushButton("시작하기")
        start_btn.setFixedWidth(280)
        start_btn.clicked.connect(self._handle_start)

        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(subtitle)
        layout.addSpacing(32)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _handle_start(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "알림", "이름을 입력해주세요.")
            return
        self.on_start(name)


# ──────────────────────────────────────────────────────
# 코디 추천 페이지
# ──────────────────────────────────────────────────────
class RecommendPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("오늘의 코디 추천")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        card = QFrame()
        card_layout = QVBoxLayout()
        for text in ["🌤 오늘 날씨: 맑음", "😊 오늘 기분: 편안함", "🧥 추천 스타일: 캐주얼"]:
            card_layout.addWidget(QLabel(text))
        card_layout.addSpacing(20)
        card_layout.addWidget(QPushButton("코디 추천 받기"))
        card.setLayout(card_layout)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)
        self.setLayout(layout)


# ──────────────────────────────────────────────────────
# 캘린더 페이지
# ──────────────────────────────────────────────────────
class CalendarPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("캘린더 & 다이어리")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        card = QFrame()
        card_layout = QVBoxLayout()
        card_layout.addWidget(QLabel("날짜별 코디 및 메모 기록 영역"))
        card_layout.addSpacing(20)
        card_layout.addWidget(QPushButton("오늘 코디 저장"))
        card.setLayout(card_layout)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)
        self.setLayout(layout)


# ──────────────────────────────────────────────────────
# 즐겨찾기 페이지
# ──────────────────────────────────────────────────────
class FavoritePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("즐겨찾기 코디")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        card = QFrame()
        card_layout = QVBoxLayout()
        card_layout.addWidget(QLabel("즐겨찾기한 코디 목록 영역"))
        card_layout.addSpacing(20)
        card_layout.addWidget(QLabel("📊 사용자님은 캐주얼 스타일을 자주 선택하시네요!"))
        card.setLayout(card_layout)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)
        self.setLayout(layout)


# ──────────────────────────────────────────────────────
# 메인 윈도우
# ──────────────────────────────────────────────────────
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.setWindowTitle("StyleMate")
        self.resize(1200, 800)
        self.setStyleSheet(PAGE_STYLE)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── 사이드바
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("QFrame { background: white; border-radius: 0px; }")

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(6)

        logo = QLabel("StyleMate")
        logo.setStyleSheet("font-size: 22px; font-weight: bold; color: #7B5EA7;")
        logo.setAlignment(Qt.AlignCenter)

        self.user_lbl = QLabel("로그인 전")
        self.user_lbl.setStyleSheet("font-size: 12px; color: #AAA;")
        self.user_lbl.setAlignment(Qt.AlignCenter)

        home_btn      = QPushButton("🏠  홈")
        recommend_btn = QPushButton("✨  코디 추천")
        closet_btn    = QPushButton("👕  옷장 관리")
        calendar_btn  = QPushButton("📅  캘린더")
        favorite_btn  = QPushButton("⭐  즐겨찾기")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(self.user_lbl)
        sidebar_layout.addSpacing(24)
        for btn in [home_btn, recommend_btn, closet_btn, calendar_btn, favorite_btn]:
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)

        # ── 페이지 스택
        self.pages = QStackedWidget()
        self.home_page      = HomePage(self._on_login)
        self.recommend_page = RecommendPage()
        self.closet_page    = ClosetPage()
        self.calendar_page  = CalendarPage()
        self.favorite_page  = FavoritePage()

        for page in [self.home_page, self.recommend_page, self.closet_page,
                     self.calendar_page, self.favorite_page]:
            self.pages.addWidget(page)

        # ── 사이드바 버튼 연결
        home_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.home_page))
        recommend_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.recommend_page))
        closet_btn.clicked.connect(lambda: self._go_closet())
        calendar_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.calendar_page))
        favorite_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.favorite_page))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)
        self.setLayout(main_layout)

    def _on_login(self, name: str):
        """홈 화면에서 이름 입력 후 호출"""
        self.username = name
        self.user_lbl.setText(f"👤 {name}")
        self.closet_page.set_username(name)
        self.pages.setCurrentWidget(self.recommend_page)

    def _go_closet(self):
        if not self.username:
            QMessageBox.information(self, "알림", "홈 화면에서 이름을 입력하고 시작해주세요.")
            self.pages.setCurrentWidget(self.home_page)
            return
        self.pages.setCurrentWidget(self.closet_page)


# ──────────────────────────────────────────────────────
# 실행
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


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