import sys
from types import ModuleType

# --- 【解決策】Python 3.12/3.13用 エラー回避コード ---
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
st.set_page_config(page_title="AIセミナー全項目分析 - シビルカレッジ", layout="wide")
st.title("🏗️ シビルカレッジ：AIセミナー全項目分析アプリ")
st.info("CSVのL列からS列（属性・満足度・動機・活用状況・課題・ニーズ・支援）をすべて可視化します。")

uploaded_file = st.file_uploader("アンケート結果（CSV）をアップロードしてください", type="csv")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    try:
        lines = bytes_data.decode("utf-8-
