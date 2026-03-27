import streamlit as st
import pandas as pd
import io

# --- 1. アプリ設定 ---
st.set_page_config(page_title="要望抽出ダッシュボード", layout="wide")
st.title("🏗️ シビルウェブ：生の声・要望抽出（重複排除版）")

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
        
        # 読み込み時に最初から重複を排除する（ユーザーIDなどでユニークにする）
        df_raw = pd.read_csv(io.BytesIO(bytes_data), skiprows=header_idx, encoding='utf-8-sig')
        
        # 重要：同じ回答者が複数行にまたがっている場合、最初の1行だけを採用する
        # （複数回答の分解による重複を防ぐため、元の「ユーザー ID」や「送信日時」で一意にします）
        df_raw = df_raw.drop_duplicates(subset=[df_raw.columns[1], df_raw.columns[4]])

        col_age = df_raw.columns[11]   # L: 年代
        col_job = df_raw.columns[13]   # N: 職域
        col_text = df_raw.columns[20]  # U: 自由記述

        # --- 2. 分類ロジック ---
        def analyze_comment(c):
            c = str(c)
            # 要望・懸念キーワード
            req_keys = ["もっと", "事例", "具体例", "セキュリティ", "不安", "懸念", "難しい", "少ない", "価格", "コスト", "踏み込ん", "実例", "導入方法", "正確性"]
            # 良い意見キーワード
            pos_keys = ["参考", "分かりやす", "良かっ", "楽しみ", "期待", "有意義", "感謝", "助かり"]
            
            sentiment = "その他"
            if any(k in c for k in req_keys): sentiment = "⚠️ 改善要望・懸念"
            elif any(k in c for k in pos_keys): sentiment = "✅ いい意見・期待"
            
            cats = []
            if any(k in c for k in ["セキュリティ", "不安", "正確性"]): cats.append("🔒 セキュリティ・信頼性")
            if any(k in c for k in ["事例", "具体例", "実例", "デモ"]): cats.append("💡 事例・デモ要望")
            if any(k in c for k in ["もっと", "難しい", "深い", "踏み込ん"]): cats.append("📚 内容の深掘り希望")
            if any(k in c for k in ["コスト", "価格", "予算", "有料"]): cats.append("💰 コスト・導入費用")
            if not cats: cats.append("💬 その他一般")
            
            return sentiment, cats

        # 自由記述がある行だけを抽出（「特になし」等は除外）
        df_text = df_raw.dropna(subset=[col_text]).copy()
        df_text = df_text[~df_text[col_text].str.contains("特になし|なし|ありません|特にありません", na=False)]
        
        results = []
        for _, row in df_text.iterrows():
            sent, cats = analyze_comment(row[col_text])
            results.append({
                "年代": row[col_age],
                "職域": row[col_job],
                "回答内容": row[col_text],
                "タイプ": sent,
                "カテゴリー": cats
            })
        df_final = pd.DataFrame(results)

        # --- 3. サイドバー・フィルター ---
        st.sidebar.header("🔍 絞り込み条件")
        
        sel_type = st.sidebar.radio("1. 意見のタイプを選択", ["すべて表示", "⚠️ 改善要望・懸念のみ", "✅ いい意見のみ"])
        
        flat_cats = sorted(list(set([c for sub in df_final["カテゴリー"] for c in sub])))
        sel_cats = st.sidebar.multiselect("2. 気になるテーマ（複数選択可）", options=flat_cats, default=flat_cats)

        st.sidebar.divider()
        sel_job = st.sidebar.multiselect("3. 職域で絞り込む", options=sorted(df_final["職域"].unique()), default=sorted(df_final["職域"].unique()))

        # フィルター適用
        mask = (df_final["職域"].isin(sel_job)) & \
               (df_final["カテゴリー"].apply(lambda x: any(c in sel_cats for c in x)))
        
        if sel_type == "⚠️ 改善要望・懸念のみ":
            mask = mask & (df_final["タイプ"] == "⚠️ 改善要望・懸念")
        elif sel_type == "✅ いい意見のみ":
            mask = mask & (df_final["タイプ"] == "✅ いい意見・期待")
            
        df_filtered = df_final[mask]

        # --- 4. 表示 ---
        st.metric(label="抽出された声の件数", value=f"{len(df_filtered)} 件")
        
        if len(df_filtered) == 0:
            st.warning("条件に合うコメントが見つかりませんでした。")
        else:
            for _, row in df_filtered.iterrows():
                # カード形式で表示
                with st.chat_message("user", avatar="💬"):
                    st.write(f"**{row['年代']} | {row['職域']}**")
                    st.write(f"タイプ: {row['タイプ']}")
                    st.write(f"テーマ: {', '.join(row['カテゴリー'])}")
                    st.info(row["回答内容"])

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
