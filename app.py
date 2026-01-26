import sys
from types import ModuleType

# --- 【究極版】Python 3.12/3.13用 エラー回避コード ---
if 'distutils' not in sys.modules:
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
# --- ここまで ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from collections import Counter
import io
import os

# --- 日本語フォントの設定 ---
font_path = None
possible_paths = [
    '/home/adminuser/venv/lib/python3.13/site-packages/japanize_matplotlib/fonts/ipaexg.ttf',
    '/home/adminuser/venv/lib/python3.12/site-packages/japanize_matplotlib/fonts/ipaexg.ttf',
    '/home/adminuser/venv/lib/python3.11/site-packages/japanize_matplotlib/fonts/ipaexg.ttf'
]
for p in possible_paths:
    if os.path.exists(p):
        font_path = p
        break

if font_path:
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
else:
    plt.rcParams['font.family'] = 'sans-serif'

sns.set(font=plt.rcParams['font.family'], style="whitegrid")

# --- アプリ設定 ---
st.set_page_config(page_title="AIセミナー詳細分析 - シビルカレッジ", layout="wide")
st.title("🏗️ シビルカレッジ：AIセミナー詳細分析アプリ")
st.info("CSVのL列からR列（年代、満足度、職種、動機、活用状況、課題、AIニーズ）を集計します。")

uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    try:
        lines = bytes_data.decode("utf-8-sig").splitlines()
        header_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('#,'):
                header_idx = i
                break
        df = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')
    except Exception as e:
        st.error(f"データの読み込みエラー: {e}")
        st.stop()

    # L列(11)からR列(17)の列名取得
    cols = {
        'age': df.columns[11],          # L: 年代
        'satisfaction': df.columns[12], # M: 満足度
        'job': df.columns[13],          # N: 職域
        'motivation': df.columns[14],   # O: きっかけ(複数)
        'usage': df.columns[15],        # P: AI活用状況
        'challenges': df.columns[16],   # Q: 課題(複数)
        'ai_needs': df.columns[17]      # R: AIニーズ(複数)
    }

    def split_and_count(column_name):
        items = []
        for row in df[column_name].dropna():
            parts = str(row).replace('\r', '').split(';')
            items.extend([p.strip() for p in parts if p.strip()])
        return pd.Series(Counter(items)).sort_values()

    # --- 分析レポート表示 ---
    st.header("📊 アンケート分析レポート (L列～R列)")

    # 1段目：基本属性
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"🎂 {cols['age']}")
        fig, ax = plt.subplots()
        df[cols['age']].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, counterclock=False)
        ax.set_ylabel("")
        st.pyplot(fig)
    with col2:
        st.subheader(f"😊 {cols['satisfaction']}")
        fig, ax = plt.subplots()
        df[cols['satisfaction']].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, counterclock=False)
        ax.set_ylabel("")
        st.pyplot(fig)

    st.divider()

    # 2段目：仕事と動機
    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f"👷 {cols['job']}")
        fig, ax = plt.subplots()
        df[cols['job']].value_counts().sort_values().plot(kind='barh', ax=ax, color='skyblue')
        st.pyplot(fig)
    with col4:
        st.subheader(f"🚀 {cols['motivation']}")
        fig, ax = plt.subplots()
        split_and_count(cols['motivation']).plot(kind='barh', ax=ax, color='orange')
        st.pyplot(fig)

    st.divider()

    # 3段目：現状と課題
    col5, col6 = st.columns(2)
    with col5:
        st.subheader(f"💻 {cols['usage']}")
        fig, ax = plt.subplots()
        df[cols['usage']].value_counts().sort_values().plot(kind='barh', ax=ax, color='lightgreen')
        st.pyplot(fig)
    with col6:
        st.subheader(f"📉 {cols['challenges']}")
        fig, ax = plt.subplots()
        split_and_count(cols['challenges']).plot(kind='barh', ax=ax, color='coral')
        st.pyplot(fig)

    st.divider()

    # 4段目：AIへの期待
    st.subheader(f"💡 {cols['ai_needs']}")
    fig, ax = plt.subplots(figsize=(10, 6))
    split_and_count(cols['ai_needs']).plot(kind='barh', ax=ax, color='plum')
    st.pyplot(fig)

    st.success("全ての設問の可視化が完了しました。")
