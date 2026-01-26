import sys
from types import ModuleType

# --- 【最強版】Python 3.12/3.13用 エラー回避コード ---
if 'distutils' not in sys.modules:
    # 文字列としても振る舞い、かつ比較計算もできる「スーパー身代わり」を作成
    class LooseVersion(str):
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
import japanize_matplotlib # これで今度こそ通過します！
from collections import Counter
import io

# アプリのタイトル・設定
st.set_page_config(page_title="AIセミナーアンケート分析 - シビルカレッジ", layout="wide")
st.title("🏗️ シビルカレッジ：AIセミナーアンケート分析アプリ")
st.caption("CSVファイルをアップロードするだけで、日本語の分析グラフを自動生成します。")

# 1. ファイルアップローダー
uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    # データの読み込み
    bytes_data = uploaded_file.getvalue()
    lines = bytes_data.decode("utf-8-sig").splitlines()
    
    header_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('#,'):
            header_idx = i
            break
            
    df = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')

    # 列名設定（あなたのスプレッドシートの項目名に合わせています）
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
    st.header("📊 分析レポート")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ セミナー満足度")
        fig, ax = plt.subplots(figsize=(8, 8))
        df[cols['satisfaction']].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, counterclock=False)
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.subheader("👷 参加者の職域")
        fig, ax = plt.subplots()
        df[cols['job']].value_counts().sort_values().plot(kind='barh', ax=ax, color='skyblue')
        ax.set_xlabel("回答数")
        st.pyplot(fig)

    st.divider()

    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📉 業界が抱える課題")
        fig, ax = plt.subplots()
        split_and_count(cols['challenges']).plot(kind='barh', ax=ax, color='coral')
        ax.set_xlabel("回答数")
        st.pyplot(fig)

    with col4:
        st.subheader("💡 AIに期待する解決内容")
        fig, ax = plt.subplots()
        split_and_count(cols['ai_needs']).plot(kind='barh', ax=ax, color='lightgreen')
        ax.set_xlabel("回答数")
        st.pyplot(fig)

    st.success("全ての分析が完了しました。")
