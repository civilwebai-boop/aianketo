import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from collections import Counter
import io
import os

# --- 【解決策】ライブラリを直接使わず、フォントファイルだけ読み込む ---
# japanize_matplotlibをimportするとエラーが出るため、インストールされたフォントファイルを直接指定します
font_path = None
# Streamlit Cloudの標準的なインストール先を探す
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
    # フォントが見つからない場合の予備（文字化けする可能性がありますがアプリは動きます）
    plt.rcParams['font.family'] = 'sans-serif'

# グラフの見た目を整える
sns.set(font=plt.rcParams['font.family'], style="whitegrid")
# -------------------------------------------------------------------

# アプリの基本設定
st.set_page_config(page_title="AIセミナー分析 - シビルカレッジ", layout="wide")
st.title("🏗️ シビルカレッジ：AIセミナーアンケート分析")
st.caption("CSVをアップロードするだけで、日本語のグラフを自動生成します。")

# --- ファイルアップロード ---
uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    try:
        # スプレッドシート形式のCSV読み込み（#で始まる行を飛ばす）
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

    # アンケートの列名
    cols = {
        'satisfaction': '本日のセミナーの内容はいかがでしたか？',
        'job': '現在の主な職域を教えてください。',
        'challenges': '御社が抱える課題を教えてください。（複数回答可）',
        'ai_needs': 'セミナーを聴いて、特に「AIで解決したい・時短したい」と感じた内容はどれですか？（複数回答可）',
        'usage': '現在、業務でどの程度AIを活用していますか？',
        'support': '今後、どのような支援があればAI本格導入・実務活用に移せそうですか？'
    }

    # 複数回答を分解して集計する関数
    def split_and_count(column_name):
        items = []
        for row in df[column_name].dropna():
            parts = str(row).replace('\r', '').split(';')
            items.extend([p.strip() for p in parts if p.strip()])
        return pd.Series(Counter(items)).sort_values()

    # --- グラフ表示 ---
    st.header("📊 分析レポート")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ セミナー満足度")
        fig, ax = plt.subplots(figsize=(7, 7))
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
