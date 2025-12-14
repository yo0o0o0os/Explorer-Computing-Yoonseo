import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import os

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="20대 초반 여성 슈트·블레이저 자켓의 사이즈 구조 분석",
    layout="wide"
)

# =========================
# Global Styles (Apple-like Font)
# =========================
st.sidebar.markdown(
    """
    <div style="
        font-size:20px;
        font-weight:800;
        line-height:1.2;
    ">
        20대 초반 여성 슈트·블레이저 자켓의 사이즈 구조 분석 🧥
    </div>
    <div style="
        font-size:15px;
        opacity:0.75;
        margin-top:6px;
    ">
        Musinsa와 Size Korea 데이터 기반
    </div>
    """,
    unsafe_allow_html=True
)


st.sidebar.divider()

nav = st.sidebar.radio(
    "Menu",
    [
        "Home",
        "무신사 사이즈 데이터",
        "사이즈 코리아 데이터",
        "의류 실측과 인체 치수 간 대응 관계 분석"
    ],
    label_visibility="visible"
)

# =========================
# Helpers (placeholders)
# =========================
AGE_GROUPS = ["20–24세", "25–29세", "30–34세", "35–39세"]


# =========================
# Page: Research Overview (Home)
# =========================
if nav == "Home":
    st.title("🏠 Home")

    st.markdown(
        """
        본 대시보드는 **무신사(Musinsa) 연령대별 랭킹 데이터**와 **사이즈코리아(Size Korea) 인체치수 데이터**를 결합하여,  
        20-24세 연령층의 여성 슈트·블레이저 자켓의 ‘치수 구조’와 ‘인체 대비 격차'를 정량적으로 분석한다.

        ### **☑️ 데이터 구성**
        **1) 무신사 랭킹 데이터**
        - 20-24세 연령층의 여성 상위 **200위** 슈트·블레이저 자켓  
        - 비교적 소재의 다양성이 적고 핏이 정형화되어있는 항목(슈트·블레이저 자켓)을 선정함
        - 사이즈표 실측 항목(무신사 웹 크롤링 통해서 얻을 수 있었음):
          - **총장**, **어깨너비**, **가슴단면**, **소매길이**
        - 제품별 여러 사이즈가 존재할 경우, 분석용 대표값은 **사이즈표 실측의 평균값**으로 정의함""")

    st.image("/Users/yoonseokim/Desktop/25-2 컴탐/기말 프로젝트/OG.png", width=400)
    st.markdown(" ")
    st.markdown("""
        **2) 사이즈코리아 인체치수 데이터**
        - 동일한 연령대 구간(20-24세)을 사용
        - 의복 설계와 대응 가능한 치수(가슴둘레-가슴단면, 어깨사이길이-어깨너비, 팔길이-소매길이)를 선별하여 사용 
        - 조금 더 정확한 3D 측정 데이터를 추후 분석할 때 사용 
        - 사이즈코리아 웹사이트 자료실에 공개된 자료를 활용했으며, Raw 데이터 없이 최종 통계량만 제공되었음""")

    st.image("/Users/yoonseokim/Desktop/25-2 컴탐/기말 프로젝트/logo.png", width=400)
    st.divider()
    st.markdown("""
        ### **☑️ 분석 내용**
        - 무신사 사이즈 데이터 통해 20-24세 연령층의 슈트·블레이저 자켓 사이즈 선호도 분석  
        - 사이즈 코리아 데이터 내에 직접 측정과 3D 측정 데이터 비교  
        - 두 데이터를 결합하여 여성 평균 인체 치수와 의복 치수의 여유분을 계산 후 선호하는 핏의 형태를 분석
        """
    )

# =========================
# Page: 무신사 사이즈 데이터
# =========================
elif nav == "무신사 사이즈 데이터":
    st.title("🛍️ 무신사 사이즈 데이터")
    st.caption("분석 대상: 20–24세 여성 / 무신사 랭킹 Top 100")

    MUSINSA_FILE = "/Users/yoonseokim/Desktop/25-2 컴탐/기말 프로젝트/musinsa_top100_age20_24.pkl"

    @st.cache_data
    def load_pickle(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    if not os.path.exists(MUSINSA_FILE):
        st.error(f"데이터 파일이 없습니다:\n{MUSINSA_FILE}")
        st.stop()

    data = load_pickle(MUSINSA_FILE)
    items = data.get("items", {})
    if not items:
        st.error("data['items']가 비어 있습니다.")
        st.stop()


    # -----------------------------
    # Transform to DataFrames
    # -----------------------------
    rows_avg, rows_long = [], []

    for rank, obj in items.items():
        meta = obj.get("rank_meta", {})
        avg = obj.get("avg", {})
        per_row = obj.get("per_row", {})

        rows_avg.append({
            "rank": int(rank),
            "brand": meta.get("brand"),
            "item_id": meta.get("item_id"),
            "title": meta.get("title", ""),
            "url": meta.get("url"),
            "original_price": meta.get("original_price"),
            "row_count": len(per_row),
            "총장_avg": avg.get("총장"),
            "어깨너비_avg": avg.get("어깨너비"),
            "가슴단면_avg": avg.get("가슴단면"),
            "소매길이_avg": avg.get("소매길이"),
        })

        for row_k, vals in per_row.items():
            rows_long.append({
                "rank": int(rank),
                "brand": meta.get("brand"),
                "item_id": meta.get("item_id"),
                "row_key": row_k,
                "original_price": meta.get("original_price"),
                "총장": vals.get("총장"),
                "어깨너비": vals.get("어깨너비"),
                "가슴단면": vals.get("가슴단면"),
                "소매길이": vals.get("소매길이"),
            })

    df_avg = pd.DataFrame(rows_avg).sort_values("rank")
    df_long = pd.DataFrame(rows_long).sort_values("rank")

    df_avg["original_price"] = pd.to_numeric(df_avg["original_price"], errors="coerce")
    df_long["original_price"] = pd.to_numeric(df_long["original_price"], errors="coerce")

    # rank 진하기(1이 가장 진함)
    df_long["rank_intensity"] = 1 - (df_long["rank"] - df_long["rank"].min()) / (df_long["rank"].max() - df_long["rank"].min() + 1e-9)
    df_avg["rank_intensity"] = 1 - (df_avg["rank"] - df_avg["rank"].min()) / (df_avg["rank"].max() - df_avg["rank"].min() + 1e-9)

    # -----------------------------
    # KPI
    # -----------------------------
    target_rank = 100
    valid_n = len(df_avg)
    unique_brands = df_avg["brand"].nunique(dropna=True)
    skipped = int(data.get("size_skipped_count", 0))
    failed = int(data.get("size_fail_count", 0))
    nonconform = skipped + failed

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("수집 대상", f"Top {target_rank}")
    c2.metric("유효 상품(사이즈표 존재)", f"{valid_n}")
    c3.metric("스킵 상품(사이즈표 존재X)", f"{nonconform}")
    c4.metric("독립적인 브랜드 개수", f"{unique_brands}")

    # -----------------------------
    # Plotly 시각화
    # -----------------------------
    # 1) 전체 테이블(=CSV 형태로 화면에 보여주기)
    st.subheader("1) 전체 데이터 테이블 (CSV 형태로 확인)")
    st.info("df_avg 테이블은 각 상품의 실측 평균값입니다. 사이즈의 개수가 상품별로 다른 것을 고려하여 다음과 같이 대푯값을 설정했습니다. row_count는 사이즈의 개수를 의미합니다.")

    # 화면 표시용 DataFrame (rank_intensity 제거)
    display_df = df_avg.drop(columns=["rank_intensity"], errors="ignore")
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    st.divider()


    # 2) 브랜드 빈도 + 브랜드 랭킹(등장횟수 기준)
    st.subheader("2) 브랜드별 등장 빈도 및 순위 정리")
    brand_count = (
        df_avg.groupby("brand", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    brand_count["brand_rank_by_count"] = np.arange(1, len(brand_count) + 1)

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            brand_count.head(20),
            x="brand",
            y="count",
            title="브랜드별 등장 횟수 (Top 20)",
        )
        fig.update_layout(xaxis_title="brand", yaxis_title="count")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.dataframe(
            brand_count.rename(columns={
                "brand": "브랜드",
                "count": "등장횟수",
                "brand_rank_by_count": "브랜드순위(등장횟수기준)"
            }).head(30),
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # 3) 사이즈 항목별 시각화 (분포 + 랭킹 경향)
    st.subheader("3) 실측 사이즈 4개 항목 분포 및 랭킹 경향")
    st.info(
        """
        ※ 색: rank가 높을수록(=1등에 가까울수록) 더 진하게 표시
        """
    )

    # rank intensity
    df_long["rank_intensity"] = 1 - (df_long["rank"] - df_long["rank"].min()) / (df_long["rank"].max() - df_long["rank"].min() + 1e-9)

    def rank_scatter(df, y_col, title):
        fig = px.scatter(
            df,
            x="rank",
            y=y_col,
            color="rank_intensity",
            color_continuous_scale="Greys",
            hover_data=["rank", "brand"],
            title=title,
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_title="rank (1=최상위)")
        return fig

    measures = ["총장", "어깨너비", "가슴단면", "소매길이"]

    for m in measures:
        st.markdown(f"#### ▪ {m}")

        c1, c2 = st.columns([1, 1])

        with c1:
            fig = px.violin(
                df_long,
                y=m,
                points="all",
                box=True,
                title=f"{m} 분포 (사이즈 행 전체)",
            )
            fig.update_layout(yaxis_title=m)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = rank_scatter(df_long, m, f"{m}: rank에 따른 분포 (점=사이즈 행)")
            st.plotly_chart(fig, use_container_width=True)

                # ✅ 총장 전용: 해석 강화 블록
        if m == "총장":
            st.markdown("##### ① 총장 분포 자체에서 보이는 명확한 특징 (왼쪽 그래프)")
            st.markdown(
                """
                총장 분포가 단일 피크가 아니라 **두 개의 뚜렷한 밀집 구간**을 가집니다. 대략적으로:  
                  - **약 48–55cm 구간**  
                  - **약 70–75cm 구간**

                ➡️ 20대 초반 재킷/블레이저 시장에서는 '숏 기장(크롭/세미크롭)'과 '정석 롱 기장(힙 덮는 길이)이  
                **명확히 분화된 두 가지 주류 실루엣**으로 공존하는 것으로 해석할 수 있습니다.  
                이는 우연이라기보다 **디자인/스타일 전략의 분화**로 볼 수 있습니다.
                """
            )

            # --- 20-24세에서 사용자가 관찰한 "중간(60~70) 공백 + 크롭 쏠림"을 수치로 보강 ---
            crop_thr = 60
            mid_low, mid_high = 60, 70
            s = df_long["총장"].dropna()

            crop_n = (s < crop_thr).sum()
            mid_n  = ((s >= mid_low) & (s <= mid_high)).sum()
            long_n = (s > mid_high).sum()
            total_n = len(s)

            crop_pct = crop_n / total_n * 100 if total_n else 0
            mid_pct  = mid_n  / total_n * 100 if total_n else 0
            long_pct = long_n / total_n * 100 if total_n else 0

            # 상위 랭킹에서 허용구간이 더 좁아지는지(극단값 감소) 간단 체크
            top_k = 20
            s_top = df_long.loc[df_long["rank"] <= top_k, "총장"].dropna()
            top_total = len(s_top)
            top_crop_pct = (s_top < crop_thr).mean() * 100 if top_total else 0
            top_mid_pct  = ((s_top >= mid_low) & (s_top <= mid_high)).mean() * 100 if top_total else 0
            top_long_pct = (s_top > mid_high).mean() * 100 if top_total else 0

            st.markdown("##### ② 20–24세에서 관찰되는 ‘중간 기장 공백’과 ‘크롭 쏠림’(수치 확인)")
            st.markdown(
                f"""
                **[전체 사이즈 행 기준 비중]**  
                - 크롭(<{crop_thr}cm): **{crop_pct:.1f}%** ({crop_n}/{total_n})  
                - 중간({mid_low}–{mid_high}cm): **{mid_pct:.1f}%** ({mid_n}/{total_n})  
                - 롱(>{mid_high}cm): **{long_pct:.1f}%** ({long_n}/{total_n})

                **[상위 랭킹 Top {top_k} 기준 비중]**  
                - 크롭(<{crop_thr}cm): **{top_crop_pct:.1f}%**  
                - 중간({mid_low}–{mid_high}cm): **{top_mid_pct:.1f}%**  
                - 롱(>{mid_high}cm): **{top_long_pct:.1f}%**

                ➡️ 20대 초반에서는 특히 **크롭 쪽 선호가 더 강한 경향성**이 있습니다.  
                    상위 랭킹 구간에서 특정 범위로 수렴한다면, 이는 **상위권 상품의 기장 ‘표준화’** 가능성을 시사합니다.
                """
            )
        if m=="어깨너비":
            st.markdown(
            """
            ##### ① 분포 특징  
            ➡️ 어깨너비는 약 **42–46cm 구간에 강한 중심 밀집**을 가지며, 상단(48cm 이상)으로만 확장되는 **비대칭 분포**를 보입니다.  

            ##### ② 랭킹과의 관계
            ➡️ 상위 랭킹 상품일수록 어깨너비가 **중앙값 근처로 수렴**하며, 과도하게 넓은 어깨는 하위 랭킹에서 더 자주 나타납니다.  
           """)

        if m=="가슴단면":
            st.markdown(
            """
            ##### ① 분포 특징  
            가슴단면은 약 **50–56cm 구간에 가장 강한 중심 밀집**을 보이며,  
            45cm대부터 60cm 이상까지 비교적 **넓은 분산**을 가집니다.  

            ➡️ 가슴단면이 단일 표준값으로 수렴하기보다는,실루엣 전략에 따라 **여유 폭이 조절되는 핵심 치수**임을 의미합니다.

            ##### ② 랭킹과의 관계  
            상위 랭킹 상품일수록 45cm 이하의 과도하게 타이트한 값이나  
            62cm 이상의 과도한 박시 핏은 드물게 나타납니다.  
            대신 **중간 이상의 안정적인 여유 폭**으로 수렴하는 경향이 확인됩니다.  

            ➡️ 20–24세 연령층에서 ‘편안하지만 과하지 않은 핏’이 선호됨을 시사합니다.
            """
            )

        std_low, std_high = 60, 62

        sleeve = df_long["소매길이"].dropna()
        total_n = len(sleeve)
        std_n = ((sleeve >= std_low) & (sleeve <= std_high)).sum()
        out_n = total_n - std_n

        std_pct = std_n / total_n * 100 if total_n else 0
        out_pct = out_n / total_n * 100 if total_n else 0

        top_k = 20
        sleeve_top = df_long.loc[df_long["rank"] <= top_k, "소매길이"].dropna()
        top_total = len(sleeve_top)

        top_std_pct = ((sleeve_top >= std_low) & (sleeve_top <= std_high)).mean() * 100 if top_total else 0
        top_out_pct = 100 - top_std_pct if top_total else 0

        if m == "소매길이":
            st.markdown(
                """
                ##### ① 분포 특징  
                소매길이는 약 **59–62cm 구간에 매우 강한 중심 밀집**을 보입니다.  
                총장이나 가슴단면에 비해 분산 폭이 작으며, 극단적으로 짧거나 긴 값은 상대적으로 드뭅니다.  

                ➡️ 소매길이가 트렌드 실험의 대상이기보다는, **착용 안정성을 유지해야 하는 보수적 치수**임을 시사합니다.
                """
            )

            st.markdown("##### ② 소매길이의 ‘표준 수렴’ 경향 (수치 확인)")
            st.markdown(
                f"""
                **[전체 사이즈 행 기준]**  
                - 표준 구간({std_low}–{std_high}cm): **{std_pct:.1f}%** ({std_n}/{total_n})  
                - 비표준 구간: **{out_pct:.1f}%** ({out_n}/{total_n})

                **[상위 랭킹 Top {top_k} 기준]**  
                - 표준 구간({std_low}–{std_high}cm): **{top_std_pct:.1f}%**  
                - 비표준 구간: **{top_out_pct:.1f}%**

                ➡️ 상위 랭킹 상품일수록 소매길이가 **60–62cm 표준 범위로 더 강하게 수렴**하며,  
                짧거나 긴 소매는 **랭킹 상승에 직접적인 이점으로 작용하지 않는 치수**임을 수치적으로 확인할 수 있습니다.
                """
            )
        st.divider()

# =========================
# Page: 사이즈 코리아 데이터
# =========================
elif nav == "사이즈 코리아 데이터":
    st.title("📏 사이즈 코리아 데이터")
    st.subheader("사이즈코리아 인체치수 요약 통계 (20–24세 여성, 단위: cm)")
    st.caption("※ 원자료는 mm이며, 본 표에서는 cm로 변환(÷10)하여 제시합니다.")

    st.info(
        """사이즈코리아 인체치수 데이터에서 제시되는 통계 지표들은 특정 연령·성별 집단의 체형 분포를 요약하기 위한 값들이다. 
        먼저 N은 해당 항목의 측정에 실제로 포함된 표본 수를 의미하며, 데이터의 신뢰도와 대표성을 판단하는 기준이 된다. 
        표본 수가 충분히 클수록 해당 통계값은 집단의 일반적인 특성을 안정적으로 반영한다고 볼 수 있다. 
        1th, 5th, 10th 등은 하위 백분위 수를 의미한다.""")

    def to_cm(mm):
        return round(mm / 10.0, 1)

    # =========================
    # 1) 가슴둘레
    # =========================
    df_chest = pd.DataFrame([
        {
            "측정방식": "직접측정",
            "N": 271,
            "Mean(cm)": to_cm(865),
            "SD(cm)": round(62.72 / 10.0, 2),
            "Min(cm)": to_cm(720),
            "Max(cm)": to_cm(1093),
            "1th": to_cm(742),
            "5th": to_cm(779),
            "10th": to_cm(794),
            "25th": to_cm(820),
            "50th": to_cm(858),
            "75th": to_cm(902),
            "90th": to_cm(948),
            "95th": to_cm(981),
            "99th": to_cm(1045),
        },
        {
            "측정방식": "3차원 자동측정",
            "N": 445,
            "Mean(cm)": to_cm(873),
            "SD(cm)": round(58.78 / 10.0, 2),
            "Min(cm)": to_cm(740),
            "Max(cm)": to_cm(1093),
            "1th": to_cm(765),
            "5th": to_cm(790),
            "10th": to_cm(804),
            "25th": to_cm(830),
            "50th": to_cm(865),
            "75th": to_cm(905),
            "90th": to_cm(956),
            "95th": to_cm(981),
            "99th": to_cm(1047),
        }
    ])

    st.markdown("### 1) 가슴둘레 (Chest Circumference)")
    st.dataframe(df_chest, hide_index=True, use_container_width=True)
    st.divider()

    # =========================
    # 2) 어깨사이길이
    # =========================
    df_shoulder = pd.DataFrame([
        {
            "측정방식": "직접측정",
            "N": 271,
            "Mean(cm)": to_cm(404),
            "SD(cm)": round(21.37 / 10.0, 2),
            "Min(cm)": to_cm(350),
            "Max(cm)": to_cm(459),
            "1th": to_cm(354),
            "5th": to_cm(370),
            "10th": to_cm(374),
            "25th": to_cm(389),
            "50th": to_cm(406),
            "75th": to_cm(418),
            "90th": to_cm(433),
            "95th": to_cm(439),
            "99th": to_cm(449),
        },
        {
            "측정방식": "3차원 자동측정",
            "N": 443,
            "Mean(cm)": to_cm(402),
            "SD(cm)": round(22.98 / 10.0, 2),
            "Min(cm)": to_cm(352),
            "Max(cm)": to_cm(484),
            "1th": to_cm(358),
            "5th": to_cm(369),
            "10th": to_cm(374),
            "25th": to_cm(385),
            "50th": to_cm(401),
            "75th": to_cm(418),
            "90th": to_cm(433),
            "95th": to_cm(441),
            "99th": to_cm(466),
        }
    ])

    st.markdown("### 2) 어깨사이길이 (Shoulder Breadth)")
    st.dataframe(df_shoulder, hide_index=True, use_container_width=True)
    st.divider()

    # =========================
    # 3) 팔길이 
    # =========================
    df_arm = pd.DataFrame([
        {
            "측정방식": "직접측정",
            "N": 271,
            "Mean(cm)": to_cm(538),
            "SD(cm)": round(22.54 / 10.0, 2),
            "Min(cm)": to_cm(465),
            "Max(cm)": to_cm(614),
            "1th": to_cm(481),
            "5th": to_cm(502),
            "10th": to_cm(509),
            "25th": to_cm(521),
            "50th": to_cm(538),
            "75th": to_cm(554),
            "90th": to_cm(567),
            "95th": to_cm(576),
            "99th": to_cm(595),
        },
        {
            "측정방식": "3차원 자동측정",
            "N": 443,
            "Mean(cm)": to_cm(543),
            "SD(cm)": round(22.31 / 10.0, 2),
            "Min(cm)": to_cm(465),
            "Max(cm)": to_cm(614),
            "1th": to_cm(494),
            "5th": to_cm(509),
            "10th": to_cm(515),
            "25th": to_cm(527),
            "50th": to_cm(542),
            "75th": to_cm(558),
            "90th": to_cm(571),
            "95th": to_cm(582),
            "99th": to_cm(604),
        }
    ])

    st.markdown("### 3) 팔길이 (Arm Length)")
    st.dataframe(df_arm, hide_index=True, use_container_width=True)
    st.divider()

    # =========================
    # (선택) 항목별로 한 번에 비교 요약표 (Mean/SD 중심)
    # =========================
    st.subheader("요약 비교 (Mean/SD 중심, 단위: cm)")

    summary = pd.DataFrame([
        {"항목": "가슴둘레", "직접 Mean": df_chest.loc[0, "Mean(cm)"], "3D Mean": df_chest.loc[1, "Mean(cm)"],
        "차이(3D-직접)": round(df_chest.loc[1, "Mean(cm)"] - df_chest.loc[0, "Mean(cm)"], 1),
        "직접 SD": df_chest.loc[0, "SD(cm)"], "3D SD": df_chest.loc[1, "SD(cm)"]},

        {"항목": "어깨사이길이", "직접 Mean": df_shoulder.loc[0, "Mean(cm)"], "3D Mean": df_shoulder.loc[1, "Mean(cm)"],
        "차이(3D-직접)": round(df_shoulder.loc[1, "Mean(cm)"] - df_shoulder.loc[0, "Mean(cm)"], 1),
        "직접 SD": df_shoulder.loc[0, "SD(cm)"], "3D SD": df_shoulder.loc[1, "SD(cm)"]},

        {"항목": "팔길이", "직접 Mean": df_arm.loc[0, "Mean(cm)"], "3D Mean": df_arm.loc[1, "Mean(cm)"],
        "차이(3D-직접)": round(df_arm.loc[1, "Mean(cm)"] - df_arm.loc[0, "Mean(cm)"], 1),
        "직접 SD": df_arm.loc[0, "SD(cm)"], "3D SD": df_arm.loc[1, "SD(cm)"]},
    ])

    st.dataframe(summary, hide_index=True, use_container_width=True)

# =========================
# Page: 의류 실측과 인체 치수 간 대응 관계 분석
# =========================
elif nav == "의류 실측과 인체 치수 간 대응 관계 분석":
    st.title("🔍 의류 실측과 인체 치수 간 대응 관계 분석")
    st.caption("분석 대상: 20–24세 여성 / 무신사 Top 100 슈트·블레이저 (상품 단위 분석: 가슴단면_avg)")

    # =========================================================
    # 0) 분석 범위 명시
    # =========================================================
    st.info(
        """
        **본 페이지는 ‘가슴단면’ 항목만을 사용하여 인체 치수와의 대응 관계(ease)를 분석합니다.**  
        무신사 실측값 중 가슴단면은 사이즈코리아의 **가슴둘레**와 직접적으로 대응시켜 해석 가능하며,  
        어깨/팔 항목은 측정 정의 차이(의류 기준 vs 인체 기준)가 커서 본 페이지에서는 제외합니다.

        또한 **상품에 사이즈가 여러 개 존재하는 경우**, 분석 대표값은 **가슴단면의 평균값(가슴단면_avg)** 으로 정의합니다.
        """
    )

    # =========================================================
    # A) 무신사 데이터 로드 + df_avg(상품 단위) 생성
    # =========================================================
    MUSINSA_FILE = "/Users/yoonseokim/Desktop/25-2 컴탐/기말 프로젝트/musinsa_top100_age20_24.pkl"

    @st.cache_data
    def load_pickle(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    if not os.path.exists(MUSINSA_FILE):
        st.error(f"무신사 데이터 파일이 없습니다:\n{MUSINSA_FILE}")
        st.stop()

    data = load_pickle(MUSINSA_FILE)
    items = data.get("items", {})
    if not items:
        st.error("data['items']가 비어 있습니다. pkl 구조를 확인하세요.")
        st.stop()

    rows_avg = []
    for rank, obj in items.items():
        meta = obj.get("rank_meta", {})
        avg = obj.get("avg", {})
        per_row = obj.get("per_row", {})

        rows_avg.append({
            "rank": int(rank),
            "brand": meta.get("brand"),
            "item_id": meta.get("item_id"),
            "title": meta.get("title", ""),
            "row_count": len(per_row),
            "가슴단면_avg": avg.get("가슴단면"),
        })

    df_avg = pd.DataFrame(rows_avg).sort_values("rank")

    # 숫자형 변환
    df_avg["가슴단면_avg"] = pd.to_numeric(df_avg["가슴단면_avg"], errors="coerce")

    # rank_intensity
    df_avg["rank_intensity"] = 1 - (df_avg["rank"] - df_avg["rank"].min()) / (
        (df_avg["rank"].max() - df_avg["rank"].min()) + 1e-9
    )

    # 결측 제거
    missing = int(df_avg["가슴단면_avg"].isna().sum())
    if missing > 0:
        st.warning(f"가슴단면_avg 결측치가 {missing}개 있어 ease 계산에서 제외됩니다.")

    df_avg_valid = df_avg.dropna(subset=["가슴단면_avg"]).copy()

    st.divider()

    # =========================================================
    # 1) 여유량(Ease) 기준 정의 (가슴둘레 기준)
    # =========================================================
    st.subheader("① 여유량(Ease) 기준 정의")
    st.caption("패턴메이킹 교재·봉제 가이드에서 제시하는 여유량 범위를 참고해 핏 유형을 정의합니다.")

    rule_df = pd.DataFrame([
        {"항목": "가슴둘레", "슬림핏": "0–6 cm", "레귤러/베이직핏": "6-10 cm", "컴포트핏": "10–16 cm", "오버사이즈핏": "16 cm 이상"}
    ])
    st.table(rule_df)

    st.info(
        """
        - 인체 기준값은 **사이즈코리아 20–24세 여성, 3차원 자동측정(mean)** 을 대표값으로 사용합니다.  
        - 무신사 실측은 **가슴단면(cm)** 이므로, 인체의 **가슴둘레를 /2 하여 단면 기준으로 맞춘 뒤** 비교합니다.  
        - 단면 차이를 다시 둘레 차이로 환산해 핏 기준(가슴둘레 ease)에 적용합니다.

        **가슴둘레 Ease(cm) = 2 × (의류 가슴단면_avg − 인체 가슴둘레/2)**
        """
    )

    st.divider()

    BODY_CHEST_CIRC_CM = 873 / 10  # 87.3cm
    BODY_CHEST_HALF_CM = BODY_CHEST_CIRC_CM / 2  # 43.65cm

    # =========================================================
    # 2) Ease 계산 (상품 단위: 가슴단면_avg 기반)
    # =========================================================
    st.subheader("② Ease 계산")

    df_ease = df_avg_valid.copy()
    df_ease["가슴단면_ease(cm)"] = df_ease["가슴단면_avg"] - BODY_CHEST_HALF_CM
    df_ease["가슴둘레_ease(cm)"] = 2 * df_ease["가슴단면_ease(cm)"]

    def classify_fit(ease):
        if pd.isna(ease):
            return np.nan
        if ease < 0:
            return "0 미만(평균 인체 치수보다 작음)"
        if ease < 6:
            return "슬림핏"
        if ease < 10:
            return "레귤러/베이직핏"
        if ease < 16:
            return "컴포트핏"
        return "오버사이즈핏"

    df_ease["핏_분류(가슴둘레)"] = df_ease["가슴둘레_ease(cm)"].apply(classify_fit)

    st.dataframe(
        df_ease[["rank", "brand", "row_count", "가슴단면_avg", "가슴둘레_ease(cm)", "핏_분류(가슴둘레)"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================================================
    # 4) Ease 분포 + Fit 비중 (Top100 전체 상품 기준)
    # =========================================================
    st.subheader("③ 가슴둘레 Ease 분포 및 핏 비중")

    fig = px.violin(
        df_ease.dropna(subset=["가슴둘레_ease(cm)"]),
        y="가슴둘레_ease(cm)",
        box=True,
        points="all",
        title="가슴둘레 Ease 분포 (상품 단위, 가슴단면_avg 기반)",
    )
    fig.update_layout(yaxis_title="Ease (cm)")
    st.plotly_chart(fig, use_container_width=True)

    fit_share = (
        df_ease["핏_분류(가슴둘레)"]
        .dropna()
        .value_counts()
        .rename_axis("핏")
        .reset_index(name="count")
    )

    # count 숫자 보장
    fit_share["count"] = pd.to_numeric(fit_share["count"], errors="coerce").fillna(0).astype(int)
    total_cnt = int(fit_share["count"].sum())
    fit_share["pct(%)"] = (fit_share["count"] / total_cnt * 100) if total_cnt > 0 else 0.0

    c1, c2 = st.columns([1, 1])
    with c1:
        st.dataframe(fit_share, hide_index=True, use_container_width=True)
    with c2:
        fig_bar = px.bar(fit_share, x="핏", y="pct(%)", title="핏 유형 비중(%)")
        st.plotly_chart(fig_bar, use_container_width=True)

    def get_pct(name: str) -> float:
        r = fit_share.loc[fit_share["핏"] == name, "pct(%)"]
        return float(r.iloc[0]) if len(r) else 0.0

    pct_over = get_pct("오버사이즈핏")
    pct_comfort = get_pct("컴포트핏")
    pct_regular = get_pct("레귤러/베이직핏")
    pct_slim = get_pct("슬림핏")
    pct_neg = 0.0

    # 음수 라벨이 다를 수 있어서 포함 검색
    neg_rows = fit_share[fit_share["핏"].astype(str).str.contains("0 미만", na=False)]
    if len(neg_rows):
        pct_neg = float(neg_rows["pct(%)"].sum())

    pct_loose = pct_over + pct_comfort  # 컴포트 이상
    pct_standard = pct_regular + pct_slim

    ease_series = df_ease["가슴둘레_ease(cm)"].dropna()
    q1 = ease_series.quantile(0.25)
    med = ease_series.quantile(0.50)
    q3 = ease_series.quantile(0.75)
    min_e = ease_series.min()
    max_e = ease_series.max()


    st.markdown("#####  ‘① 가슴 여유량(Ease)’이 실루엣 전략의 핵심 변수로 작동")
    st.markdown(
        f"""
        바이올린 그래프(분포)에서 **중앙값이 이미 오버사이즈 영역에 위치**하고,  
        핏 비중에서도 **오버사이즈+컴포트가 {pct_loose:.1f}%로 과반을 크게 상회**한다는 점을 함께 고려하면,  
        20–24세 여성 슈트·블레이저 시장에서 가슴둘레 Ease는 단순한 착용 편의의 문제가 아니라  
        **브랜드/상품이 설정한 ‘기본 실루엣’을 규정하는 설계 변수**로 해석할 수 있습니다.

        ➡️ 이 연령대에서 상위 랭킹 상품은 ‘정장다운 정핏’보다 **여유를 전제로 한 볼륨감(실루엣) 전략**을 표준처럼 채택하고 있습니다.
        """
    )
    st.divider()

    st.markdown("##### ② 분포 폭은 넓지만, 하한선은 명확")

    st.markdown(
        f"""
        가슴둘레 Ease 분포는 상단 방향으로는 폭넓게 확장되어 있으나,  
        **하한선은 매우 명확하게 제한**되어 있습니다.

        - Ease 하한은 **거의 0cm 근처에서 컷(cut)**  
        - **인체 평균보다 작은 음수 Ease 상품은 1개({pct_neg:.1f}%)에 불과**  
        - 즉, 인체 평균보다 타이트한 설계는 Top100 시장에서 **사실상 선택되지 않음**

        ➡️ **‘몸에 딱 맞게 만든 재킷’이 이 연령대·카테고리에서는 비주류 설계**임을 시사합니다.
        """
    )
