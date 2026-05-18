class FashionAnalyticsManager:
    def __init__(self, user_data):
        """
        :param user_data: 세영님이 JSON에서 로드하여 전달해 줄 유저 데이터 딕셔너리
        """
        self.user_data = user_data

    # ========================================================
    # 1. 즐겨찾기 저장 (add_favorite)
    # ========================================================
    def add_favorite(self, outfit_data):
        
        if "favorites" not in self.user_data:
            self.user_data["favorites"] = []
            
        # 중복 저장 방지 검사
        for fav in self.user_data["favorites"]:
            if (fav.get("top_id") == outfit_data.get("top_id") and 
                fav.get("bottom_id") == outfit_data.get("bottom_id") and 
                fav.get("outer_id") == outfit_data.get("outer_id")):
                return False, "이미 즐겨찾기에 등록된 코디입니다."
                
        self.user_data["favorites"].append(outfit_data)
        return True, "즐겨찾기에 성공적으로 저장되었습니다!"

    # ========================================================
    # 2. 즐겨찾기 불러오기 (load_favorite)
    # ========================================================
    def load_favorite(self):
        
        return self.user_data.get("favorites", [])

    # ========================================================
    # 3. 스타일 및 색상 통계 분석 (analyze_style)
    # ========================================================
    def analyze_style(self):
        
        # --- [파트 A] 스타일 빈도 계산 ---
        styles = []
        
        # 즐겨찾기에서 스타일 태그 수집
        for fav in self.user_data.get("favorites", []):
            if fav.get("style"):
                styles.append(fav["style"])
                
        # 캘린더 히스토리(현주님 담당)에서 스타일 태그 수집
        for date, record in self.user_data.get("history", {}).items():
            if record.get("style"):
                styles.append(record["style"])
        
        # 스타일 빈도 계산 (pandas Series 활용)
        if styles:
            style_counts = pd.Series(styles).value_counts().to_dict()
        else:
            style_counts = {}

        # --- [파트 B] 색상 빈도 계산 ---
        color_counts = {}
        wardrobe_list = self.user_data.get("wardrobe", [])
        
        if wardrobe_list:
            # 옷장 데이터를 검색용 DataFrame으로 변환
            df_wardrobe = pd.DataFrame(wardrobe_list)
            used_clothing_ids = []
            
            # 즐겨찾기에서 의류 ID 추출
            for fav in self.user_data.get("favorites", []):
                for role in ["top_id", "bottom_id", "outer_id"]:
                    if fav.get(role):
                        used_clothing_ids.append(fav.get(role))
                        
            # 히스토리에서 의류 ID 추출
            for date, record in self.user_data.get("history", {}).items():
                outfit = record.get("outfit", {})
                for role in ["top", "bottom", "outer"]:
                    if outfit.get(role):
                        used_clothing_ids.append(outfit.get(role))
            
            # 사용된 옷 ID 리스트가 존재할 때만 색상 매핑 작업 진행
            if used_clothing_ids:
                df_used_ids = pd.DataFrame(used_clothing_ids, columns=["id"])
                # 옷장 데이터와 ID를 기준으로 병합(Merge)하여 색상 정보 획득
                df_merged = pd.merge(df_used_ids, df_wardrobe, on="id", how="inner")
                # 색상별 빈도수 계산 후 딕셔너리로 변환
                color_counts = df_merged["color"].value_counts().to_dict()

        # 두 가지 분석 결과를 하나의 결과물로 묶어서 리턴
        return {
            "style_frequency": style_counts,
            "color_frequency": color_counts
        }