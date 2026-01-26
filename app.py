import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from collections import Counter
import io
import os
import sys

# --- 【最強の回避策】エラーの元になるライブラリを一切使わない ---
# japanize_matplotlibを読み込まず、フォントファイルだけを直接使います
try:
    font_path = None
    # 各バージョンのパスを総当たりで探す
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

sns.set(font=plt.rcParams['font.family'], style="whitegrid")

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIセミナー全項目分析", layout="wide")
st.title("🏗️ シビルウェブ：AIセミナーアンケート分析")

# 万が一のエラーを画面に表示する設定
def show_error(e):
    st.error(f"エラーが発生しました: {e}")
    st.info("CSVの形式や、GitHubのファイル名（app.pyになっているか）を確認してください。")

uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        # CSVの読み込み（#で始まる行を探してヘッダーにする）
        lines = bytes_data.decode("utf-8-sig").splitlines()
        header_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#,'):
                header_idx = i
                break
        
        df = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')

        # --- 列の特定（キーワードで探すことで、列がズレても動くようにする） ---
        def find_col(keywords):
            for col in df.columns:
                if any(k in col for k in keywords):
                    return col
            return None

        # L列〜S列に相当する項目を自動特定
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

        # 複数回答を集計する関数
        def plot_multi(col_name, title, color):
            if not col_name: return
            items = []
            for row in df[col_name].dropna():
                parts = str(row).replace('\r', '').split(';')
                items.extend([p.strip() for p in parts if p.strip()])
            counts = pd.Series(Counter(items)).sort_values()
            
            fig, ax = plt.subplots()
            counts.plot(kind='barh', ax=ax, color=color)
            st.subheader(f"📊 {title}")
            st.pyplot(fig)

        # 1種類のみ回答を集計する関数
        def plot_single_pie(col_name, title):
            if not col_name: return
            fig, ax = plt.subplots()
            df[col_name].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, counterclock=False)
            ax.set_ylabel("")
            st.subheader(f"✅ {title}")
            st.pyplot(fig)

        def plot_single_bar(col_name, title, color):
            if not col_name: return
            fig, ax = plt.subplots()
            df[col_name].value_counts().sort_values().plot(kind='barh', ax=ax, color=color)
            st.subheader(f"👷 {title}")
            st.pyplot(fig)

        # --- 画面レイアウト ---
        tab1, tab2 = st.tabs(["基本属性・満足度", "課題・ニーズ・支援"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1: plot_single_pie(target_cols['年代'], "年代")
            with c2: plot_single_pie(target_cols['満足度'], "セミナー満足度")
            
            c3, c4 = st.columns(2)
            with c3: plot_single_bar(target_cols['職域'], "参加者の職域", "skyblue")
            with c4: plot_single_bar(target_cols['活用状況'], "現在のAI活用状況", "lightgreen")

        with tab2:
            st.info("複数回答の項目を集計しています")
            c5, c6 = st.columns(2)
            with c5: plot_multi(target_cols['動機'], "参加の動機", "orange")
            with c6: plot_multi(target_cols['課題'], "業界の課題", "coral")
            
            st.divider()
            
            c7, c8 = st.columns(2)
            with c7: plot_multi(target_cols['AIニーズ'], "AIで解決したいこと", "plum")
            with c8: plot_multi(target_cols['今後の支援'], "今後必要な支援", "gold")

        st.success("全ての分析が完了しました！")

    except Exception as e:
        show_error(e)

