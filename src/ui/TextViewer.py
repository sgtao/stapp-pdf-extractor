# TextViewer.py
import streamlit as st
from typing import List

from logic.utils.filter_text_lines import filter_text_lines


# --- UIコンポーネント (関数) ---
class TextViewer:
    """
    テキスト情報の表示とフィルタリング設定を管理するUIクラス。
    """

    def __init__(self, page_texts: List[str]):
        self.page_texts = page_texts
        # セッションステートからパターン数を取得
        if "regex_count" not in st.session_state:
            st.session_state["regex_count"] = 1
        self.regex_count = st.session_state["regex_count"]

    def _get_regex_patterns(self) -> List[str]:
        """UIから正規表現パターンを取得する。"""
        regex_patterns = []
        for i in range(st.session_state["regex_count"]):
            key = f"regex_pattern_{i}"
            # セッションステートで永続化
            default_value = (
                st.session_state.get(key, r"^\s*Page\s+\d+\s*$")
                if i == 0
                else ""
            )
            st.session_state[key] = st.text_input(
                f"除外パターン {i+1} (正規表現)",
                value=default_value,
                key=f"input_{key}",
                placeholder=r"例: フッターのページ番号 (^\s*\d+\s*$)",
            )
            regex_patterns.append(st.session_state[key])
        return regex_patterns

    def render(self) -> None:
        """テキスト情報をStreamlitのタブで表示する。"""
        st.subheader("抽出テキスト")

        # F-9: 除外行入力（正規表現パターン）
        with st.expander("⚙️ 除外行 正規表現パターンの設定", expanded=False):
            col_ctrl, _ = st.columns([1, 4])

            # パターン数の増減
            new_count = col_ctrl.number_input(
                "パターン数", min_value=1, value=self.regex_count, step=1
            )
            if new_count != self.regex_count:
                st.session_state["regex_count"] = new_count
                st.rerun()  # パターン数を変更したら再実行して新しい入力欄を出す

            st.markdown("---")
            regex_patterns = self._get_regex_patterns()

        # フィルタリング適用
        filtered_texts = [
            filter_text_lines(text, regex_patterns) for text in self.page_texts
        ]

        text_tabs = st.tabs(["整形済みテキスト", "コード形式"])

        with text_tabs[0]:  # テキスト表示 (F-7-1)
            st.markdown("### ページごとのテキスト (フィルタリング適用)")
            for i, filtered_text in enumerate(filtered_texts):
                st.markdown(f"#### ページ {i + 1}")
                st.text(filtered_text)

        with text_tabs[1]:  # st.code表示 (F-7-2)
            st.markdown(
                "### ページごとのテキスト (コード形式・フィルタリング適用)"
            )
            for i, filtered_text in enumerate(filtered_texts):
                st.markdown(f"#### ページ {i + 1}")
                st.code(filtered_text, language="plaintext")
