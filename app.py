import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from collections import Counter
import io
import os
import sys

# --- 1. Python 3.12/3.13用 エラー回避コード ---
if 'distutils' not in sys.modules:
    from types import ModuleType
    class LooseVersion(str):
        def __repr__(self): return f"LooseVersion('{self}')"
        def __lt__(self, other): return False
        def __le__(self, other): return False
        def __gt__(self, other): return True
        def __ge__(self, other): return True
        def __eq__(self, other): return False
    distutils = ModuleType("distutils")
    version = ModuleType("distutils.version")
    version.LooseVersion = LooseVersion
    distutils.version = version
    sys.modules["distutils"] = distutils
    sys.modules["distutils.version"] = version

# --- 2. 日本語フォントの設定 ---
try:
    font_path = None
    for v in ["3.13", "3.12", "3.11"]:
        p = f'/home/adminuser/venv/lib/python{v}/site-packages/japanize_matplotlib/fonts/ipaexg.ttf'
        if os.path.exists(p):
            font_path = p
            break
    if font_path:
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'
except:
    plt.rcParams['font.family'] = 'sans-serif'

sns.set(font=plt.rcParams['font.family'], style="white")

# --- 3. アプリ設定 ---
st.set_page_config(page_title="AIセミナー総合分析", layout="wide")
st.title("🏗️ シビルウェブ：AIセミナー詳細分析アプリ")

uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        lines = bytes_data.decode("utf-8-sig").splitlines()
        header_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#,'):
                header_idx = i
                break
        
        # 全データの読み込み
        df_raw = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')

        # 列名のマッピング（L列〜T列）
        # 列番号で指定することで確実に取得します
        target_cols = {
            '年代': df_raw.columns[11],          # L
            '満足度': df_raw.columns[12],        # M
            '職域': df_raw.columns[13],          # N
            '動機': df_raw.columns[14],          # O (複数)
            '活用状況': df_raw.columns[15],      # P
            '課題': df_raw.columns[16],          # Q (複数)
            'AIニーズ': df_raw.columns[17],      # R (複数)
            '導入の障壁': df_raw.columns[18],    # S (複数)
            '今後の支援': df_raw.columns[19]     # T (複数)
        }

        # --- 4. サイドバーでのフィルタリング（クロス分析） ---
        st.sidebar.header("🔍 データを絞り込む")
        
        # 年代フィルター
        age_list = ["すべて"] + sorted(df_raw[target_cols['年代']].dropna().unique().tolist())
        selected_age = st.sidebar.selectbox(f"🎂 {target_cols['年代']}", age_list)

        # 職域フィルター
        job_list = ["すべて"] + sorted(df_raw[target_cols['職域']].dropna().unique().tolist())
        selected_job = st.sidebar.selectbox(f"👷 {target_cols['職域']}", job_list)

        # 活用状況フィルター
        usage_list = ["すべて"] + sorted(df_raw[target_cols['活用状況']].dropna().unique().tolist())
        selected_usage = st.sidebar.selectbox(f"💻 {target_cols['活用状況']}", usage_list)

        # データの絞り込み実行
        df = df_raw.copy()
        if selected_age != "すべて":
            df = df[df[target_cols['年代']] == selected_age]
        if selected_job != "すべて":
            df = df[df[target_cols['職域']] == selected_job]
        if selected_usage != "すべて":
            df = df[df[target_cols['活用状況']] == selected_usage]

        # --- 5. 母数表示 ---
        total_n = len(df)
        st.metric(label="分析対象の回答者数（母数）", value=f"{total_n} 名")
        if total_n < len(df_raw):
            st.info(f"全 {len(df_raw)} 名から絞り込み中")
        st.divider()

        # --- 6. グラフ描画関数 ---

        def plot_multi_with_pct(col_name, title, color):
            if not col_name or df[col_name].dropna().empty:
                st.info(f"「{title}」のデータはありません。")
                return
            items = []
            for row in df[col_name].dropna():
                parts = str(row).replace('\r', '').split(';')
                items.extend([p.strip() for p in parts if p.strip()])
            if not items: return
            counts = pd.Series(Counter(items)).sort_values()
            total_respondents = len(df[col_name].dropna())
            
            fig, ax = plt.subplots()
            counts.plot(kind='barh', ax=ax, color=color)
            for i, v in enumerate(counts):
                pct = (v / total_respondents) * 100
                ax.text(v + 0.1, i, f'{pct:.1f}%', va='center', fontsize=10, fontweight='bold')
            ax.set_ylabel("") # 左の設問テキストを消す
            ax.xaxis.grid(True, linestyle='--', alpha=0.6) # 縦線あり
            ax.yaxis.grid(False) # 横線なし
            ax.set_xlim(0, max(counts) * 1.3 if not counts.empty else 1)
            st.subheader(f"📊 {title}")
            st.pyplot(fig)

        def plot_single_bar_with_pct(col_name, title, color):
            if not col_name or df[col_name].dropna().empty:
                st.info(f"「{title}」のデータはありません。")
                return
            counts = df[col_name].value_counts().sort_values()
            total = counts.sum()
            fig, ax = plt.subplots()
            counts.plot(kind='barh', ax=ax, color=color)
            for i, v in enumerate(counts):
                pct = (v / total) * 100
                ax.text(v + 0.1, i, f'{pct:.1f}%', va='center', fontsize=10, fontweight='bold')
            ax.set_ylabel("") # 左の設問テキストを消す
            ax.xaxis.grid(True, linestyle='--', alpha=0.6) # 縦線あり
            ax.yaxis.grid(False) # 横線なし
            ax.set_xlim(0, max(counts) * 1.3 if not counts.empty else 1)
            st.subheader(f"👷 {title}")
            st.pyplot(fig)

        def plot_single_pie(col_name, title):
            if not col_name or df[col_name].dropna().empty: return
            fig, ax = plt.subplots()
            df[col_name].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, counterclock=False)
            ax.set_ylabel("")
            st.subheader(f"✅ {title}")
            st.pyplot(fig)

        # --- 7. 画面レイアウト（3つのタブで整理） ---
        tab1, tab2, tab3 = st.tabs(["基本属性・状況", "動機・課題・ニーズ", "障壁・支援ニーズ"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1: plot_single_pie(target_cols['年代'], "年代 (L列)")
            with c2: plot_single_pie(target_cols['満足度'], "満足度 (M列)")
            st.divider()
            c3, c4 = st.columns(2)
            with c3: plot_single_bar_with_pct(target_cols['職域'], "主な職域 (N列)", "skyblue")
            with c4: plot_single_bar_with_pct(target_cols['活用状況'], "現在のAI活用状況 (P列)", "lightgreen")

        with tab2:
            c5, c6 = st.columns(2)
            with c5: plot_multi_with_pct(target_cols['動機'], "参加の動機 (O列)", "orange")
            with c6: plot_multi_with_pct(target_cols['課題'], "業界の課題 (Q列)", "coral")
            st.divider()
            plot_multi_with_pct(target_cols['AIニーズ'], "AIで解決・時短したい内容 (R列)", "plum")

        with tab3:
            c7, c8 = st.columns(2)
            with c7: plot_multi_with_pct(target_cols['導入の障壁'], "実業務導入への障壁 (S列)", "indianred")
            with c8: plot_multi_with_pct(target_cols['今後の支援'], "今後必要な支援 (T列)", "gold")

        st.success("全ての分析が完了しました。左のメニューで自由に絞り込んでください。")

    except Exception as e:
        st.error(f"実行中にエラーが発生しました: {e}")
