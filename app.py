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

# グラフのデザイン設定（白背景）
sns.set(font=plt.rcParams['font.family'], style="white")

# --- 3. アプリの基本設定 ---
st.set_page_config(page_title="AIセミナー全項目分析", layout="wide")
st.title("🏗️ シビルウェブ：AIセミナー詳細分析")

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
        
        df = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')

        # --- 4. 母数（回答者数）の表示 ---
        total_n = len(df)
        st.metric(label="アンケート回答者数（母数）", value=f"{total_n} 名")
        st.divider()

        # 列名の特定
        def find_col(keywords):
            for col in df.columns:
                if any(k in col for k in keywords):
                    return col
            return None

        target_cols = {
            '年代': find_col(['年代']),
            '満足度': find_col(['満足度', 'いかがでしたか']),
            '職域': find_col(['職域', '職種']),
            '動機': find_col(['動機', 'きっかけ']),
            '活用状況': find_col(['活用', 'AIを活用']),
            '課題': find_col(['課題']),
            'AIニーズ': find_col(['AIで解決', '時短したい']),
            '今後の支援': find_col(['支援', '本格導入'])
        }

        # --- 5. グラフ描画関数 ---

        # 複数回答用
        def plot_multi_with_pct(col_name, title, color):
            if not col_name or df[col_name].dropna().empty: return
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
            
            # --- ここで「縦の設問文字」を消し、線を設定 ---
            ax.set_ylabel("")                   # 左側の設問テキストを消去
            ax.xaxis.grid(True, linestyle='--', alpha=0.6) # 縦線（目安）を出す
            ax.yaxis.grid(False)                # 横線を消す
            
            ax.set_xlim(0, max(counts) * 1.3)
            st.subheader(f"📊 {title}")
            st.pyplot(fig)

        # 単一回答・棒グラフ用
        def plot_single_bar_with_pct(col_name, title, color):
            if not col_name or df[col_name].dropna().empty: return
            counts = df[col_name].value_counts().sort_values()
            total = counts.sum()
            fig, ax = plt.subplots()
            counts.plot(kind='barh', ax=ax, color=color)
            for i, v in enumerate(counts):
                pct = (v / total) * 100
                ax.text(v + 0.1, i, f'{pct:.1f}%', va='center', fontsize=10, fontweight='bold')
            
            # --- ここで「縦の設問文字」を消し、線を設定 ---
            ax.set_ylabel("")                   # 左側の設問テキストを消去
            ax.xaxis.grid(True, linestyle='--', alpha=0.6) # 縦線（目安）を出す
            ax.yaxis.grid(False)                # 横線を消す
            
            ax.set_xlim(0, max(counts) * 1.3)
            st.subheader(f"👷 {title}")
            st.pyplot(fig)

        # 円グラフ
        def plot_single_pie(col_name, title):
            if not col_name or df[col_name].dropna().empty: return
            fig, ax = plt.subplots()
            df[col_name].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, counterclock=False)
            ax.set_ylabel("")
            st.subheader(f"✅ {title}")
            st.pyplot(fig)

        # --- 6. 画面レイアウト ---
        tab1, tab2 = st.tabs(["基本属性・満足度", "課題・ニーズ・支援"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1: plot_single_pie(target_cols['年代'], "年代 (L列)")
            with c2: plot_single_pie(target_cols['満足度'], "セミナー満足度 (M列)")
            
            st.divider()
            
            c3, c4 = st.columns(2)
            with c3: plot_single_bar_with_pct(target_cols['職域'], "参加者の職域 (N列)", "skyblue")
            with c4: plot_single_bar_with_pct(target_cols['活用状況'], "現在のAI活用状況 (P列)", "lightgreen")

        with tab2:
            c5, c6 = st.columns(2)
            with c5: plot_multi_with_pct(target_cols['動機'], "参加の動機 (O列)", "orange")
            with c6: plot_multi_with_pct(target_cols['課題'], "業界の課題 (Q列)", "coral")
            
            st.divider()
            
            c7, c8 = st.columns(2)
            with c7: plot_multi_with_pct(target_cols['AIニーズ'], "AIで解決したい内容 (R列)", "plum")
            with c8: plot_multi_with_pct(target_cols['今後の支援'], "今後必要な支援 (S列)", "gold")

        st.success("全ての分析が完了しました！")

    except Exception as e:
        st.error(f"実行中にエラーが発生しました。: {e}")
