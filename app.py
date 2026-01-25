import sys

# --- ここから：Python 3.12+ のエラー回避用（おまじない） ---
try:
    import distutils.version
except ImportError:
    # distutilsがない環境（3.12以上）ではダミーを作成してエラーを防ぐ
    from types import ModuleType
    d = ModuleType("distutils")
    dv = ModuleType("distutils.version")
    class LooseVersion:
        def __init__(self, v): self.v = v
    dv.LooseVersion = LooseVersion
    d.version = dv
    sys.modules["distutils"] = d
    sys.modules["distutils.version"] = dv
# --- ここまで ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib  # ← これより上でダミーを準備するのがポイント！
from collections import Counter
import io

# （以下、以前のコードと同じ）

# アプリのタイトル
st.set_page_config(page_title="AIセミナーアンケート分析アプリ", layout="wide")
st.title("🏗️ 建設業界向け：AIセミナーアンケート分析")

# 1. ファイルアップローダー
uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    # データの読み込み
    # Colab同様、ヘッダー位置を特定
    bytes_data = uploaded_file.getvalue()
    lines = bytes_data.decode("utf-8-sig").splitlines()
    
    header_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('#,'):
            header_idx = i
            break
            
    df = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')

    # 列名設定
    cols = {
        'satisfaction': '本日のセミナーの内容はいかがでしたか？',
        'job': '現在の主な職域を教えてください。',
        'challenges': '御社が抱える課題を教えてください。（複数回答可）',
        'ai_needs': 'セミナーを聴いて、特に「AIで解決したい・時短したい」と感じた内容はどれですか？（複数回答可）',
        'usage': '現在、業務でどの程度AIを活用していますか？',
        'support': '今後、どのような支援があればAI本格導入・実務活用に移せそうですか？'
    }

    # 複数回答集計用関数
    def split_and_count(column_name):
        items = []
        for row in df[column_name].dropna():
            parts = str(row).replace('\r', '').split(';')
            items.extend([p.strip() for p in parts if p.strip()])
        return pd.Series(Counter(items)).sort_values()

    # --- 画面表示 ---
    st.header("📊 分析結果")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("満足度")
        fig, ax = plt.subplots()
        df[cols['satisfaction']].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.subheader("参加者の職域")
        fig, ax = plt.subplots()
        df[cols['job']].value_counts().sort_values().plot(kind='barh', ax=ax, color='skyblue')
        st.pyplot(fig)

    st.divider()

    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("業界の課題（複数回答）")
        fig, ax = plt.subplots()
        split_and_count(cols['challenges']).plot(kind='barh', ax=ax, color='coral')
        st.pyplot(fig)

    with col4:
        st.subheader("AIで解決したい内容")
        fig, ax = plt.subplots()
        split_and_count(cols['ai_needs']).plot(kind='barh', ax=ax, color='lightgreen')
        st.pyplot(fig)

    st.success("分析が完了しました！")

