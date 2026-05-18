import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QFrame,
)
from PySide6.QtCore import Qt


# =========================
# 공통 페이지 스타일
# =========================
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


# =========================
# 홈 화면
# =========================
class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("StyleMate")
        title.setStyleSheet("font-size: 40px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("AI 패션 코디 추천 프로그램")
        subtitle.setStyleSheet("font-size: 18px;")
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(subtitle)

        self.setLayout(layout)


# =========================
# 메인 추천 페이지
# =========================
class RecommendPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("오늘의 코디 추천")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        card = QFrame()
        card_layout = QVBoxLayout()

        weather = QLabel("🌤 오늘 날씨: 맑음")
        mood = QLabel("😊 오늘 기분: 편안함")
        style = QLabel("🧥 추천 스타일: 캐주얼")

        recommend_btn = QPushButton("코디 추천 받기")

        card_layout.addWidget(weather)
        card_layout.addWidget(mood)
        card_layout.addWidget(style)
        card_layout.addSpacing(20)
        card_layout.addWidget(recommend_btn)

        card.setLayout(card_layout)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)

        self.setLayout(layout)


# =========================
# 옷장 관리 페이지
# =========================
class ClosetPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("옷장 관리")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        card = QFrame()
        card_layout = QVBoxLayout()

        info = QLabel("등록된 옷 목록이 표시될 영역")
        add_btn = QPushButton("옷 추가하기")

        card_layout.addWidget(info)
        card_layout.addSpacing(20)
        card_layout.addWidget(add_btn)

        card.setLayout(card_layout)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)

        self.setLayout(layout)


# =========================
# 캘린더 페이지
# =========================
class CalendarPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("캘린더 & 다이어리")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        card = QFrame()
        card_layout = QVBoxLayout()

        info = QLabel("날짜별 코디 및 메모 기록 영역")
        save_btn = QPushButton("오늘 코디 저장")

        card_layout.addWidget(info)
        card_layout.addSpacing(20)
        card_layout.addWidget(save_btn)

        card.setLayout(card_layout)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)

        self.setLayout(layout)


# =========================
# 즐겨찾기 페이지
# =========================
class FavoritePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("즐겨찾기 코디")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        card = QFrame()
        card_layout = QVBoxLayout()

        info = QLabel("즐겨찾기한 코디 목록 영역")
        stats = QLabel("📊 사용자님은 캐주얼 스타일을 자주 선택하시네요!")

        card_layout.addWidget(info)
        card_layout.addSpacing(20)
        card_layout.addWidget(stats)

        card.setLayout(card_layout)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(card)

        self.setLayout(layout)


# =========================
# 메인 윈도우
# =========================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StyleMate")
        self.resize(1200, 800)
        self.setStyleSheet(PAGE_STYLE)

        # 전체 레이아웃
        main_layout = QHBoxLayout()

        # =========================
        # 사이드바
        # =========================
        sidebar = QFrame()
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout()

        logo = QLabel("StyleMate")
        logo.setStyleSheet("font-size: 24px; font-weight: bold;")
        logo.setAlignment(Qt.AlignCenter)

        home_btn = QPushButton("🏠 홈")
        recommend_btn = QPushButton("✨ 코디 추천")
        closet_btn = QPushButton("👕 옷장 관리")
        calendar_btn = QPushButton("📅 캘린더")
        favorite_btn = QPushButton("⭐ 즐겨찾기")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(home_btn)
        sidebar_layout.addWidget(recommend_btn)
        sidebar_layout.addWidget(closet_btn)
        sidebar_layout.addWidget(calendar_btn)
        sidebar_layout.addWidget(favorite_btn)
        sidebar_layout.addStretch()

        sidebar.setLayout(sidebar_layout)

        # =========================
        # 페이지 스택
        # =========================
        self.pages = QStackedWidget()

        self.home_page = HomePage()
        self.recommend_page = RecommendPage()
        self.closet_page = ClosetPage()
        self.calendar_page = CalendarPage()
        self.favorite_page = FavoritePage()

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.recommend_page)
        self.pages.addWidget(self.closet_page)
        self.pages.addWidget(self.calendar_page)
        self.pages.addWidget(self.favorite_page)

        # =========================
        # 버튼 연결
        # =========================
        home_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.home_page))
        recommend_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.recommend_page))
        closet_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.closet_page))
        calendar_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.calendar_page))
        favorite_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.favorite_page))

        # =========================
        # 레이아웃 합치기
        # =========================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

        self.setLayout(main_layout)


# =========================
# 실행
# =========================
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
