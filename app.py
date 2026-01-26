import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from collections import Counter
import io
import os
import sys

# --- 【究極の回避策】エラーの元になるライブラリを一切使わない ---
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

sns.set(font=plt.rcParams['font.family'], style="whitegrid")

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIセミナー全項目分析", layout="wide")
st.title("🏗️ シビルカレッジ：AIセミナー詳細分析")

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

        # 複数回答用（割合％のみを表示）
        def plot_multi(col_name, title, color):
            if not col_name: return
            items = []
            for row in df[col_name].dropna():
                parts = str(row).replace('\r', '').split(';')
                items.extend([p.strip() for p in parts if p.strip()])
            counts = pd.Series(Counter(items)).sort_values()
            total_respondents = len(df[col_name].dropna())
            
            fig, ax = plt.subplots()
            counts.plot(kind='barh', ax=ax, color=color)
            
            # 棒の横に割合(%)のみを表示
            for i, v in enumerate(counts):
                pct = (v / total_respondents) * 100
                ax.text(v + 0.1, i, f'{pct:.1f}%', va='center', fontsize=10, fontweight='bold')
            
            ax.set_xlim(0, max(counts) * 1.2) #
