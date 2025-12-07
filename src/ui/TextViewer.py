# src/ui/TextViewer.py (改修後)
import streamlit as st
from typing import List

from logic.util.filter_text_lines import filter_text_lines


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
        # ... (変更なし)
        regex_patterns = []
        for i in range(st.session_state["regex_count"]):
            key = f"regex_pattern_{i}"
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
                st.rerun()

            st.markdown("---")
            regex_patterns = self._get_regex_patterns()

        # ★ ページ単位 / 全ページ一括 の切り替えラジオボタン
        display_mode = st.radio(
            "表示方法の選択",
            ("ページ単位", "全ページ一括"),
            index=0,
            horizontal=True,
        )

        # ページ内の改行除去
        omit_newline = st.checkbox(
            "ページ内改行除去",
            value=False,
            help="`True`時、ページ内テキストの改行を抑止します",
        )

        text_tabs = st.tabs(["整形済みテキスト", "コード形式"])
        section_title = f"### {display_mode} のテキスト"

        # フィルタリング適用
        # 全ページ一括表示のために、すべてのフィルタ済みテキストを取得しておく
        # filtered_texts = [
        #     filter_text_lines(text, regex_patterns) for text in self.page_texts
        # ]
        filtered_texts = []
        for text in self.page_texts:
            filterd_text = filter_text_lines(text, regex_patterns)
            if omit_newline:
                filterd_text = filterd_text.replace("\n"," ")
            filtered_texts.append(filterd_text)

        # 全ページ一括テキストの作成
        # all_pages_text = "\n\n--- ページ区切り ---\n\n".join(filtered_texts)
        all_pages_text = ""
        for i, page_text in enumerate(filtered_texts):
            all_pages_text += f"\n\n<!-- Page {i} -->\n\n" + page_text


        with text_tabs[0]:  # 整形済みテキスト表示 (F-7-1)
            st.markdown(section_title)

            if display_mode == "ページ単位":
                # ページ単位表示 (既存ロジック)
                for i, filtered_text in enumerate(filtered_texts):
                    st.markdown(f"#### ページ {i + 1}")
                    st.text(filtered_text)
            else:  # 全ページ一括
                # st.markdown("#### 全ページテキスト")
                st.text(all_pages_text)  # st.text で表示

        with text_tabs[1]:  # コード形式表示 (F-7-2)
            st.markdown(section_title)

            if display_mode == "ページ単位":
                # ページ単位表示 (既存ロジック)
                for i, filtered_text in enumerate(filtered_texts):
                    st.markdown(f"#### ページ {i + 1}")
                    st.code(filtered_text, language="plaintext")
            else:  # 全ページ一括
                # st.markdown("#### 全ページテキスト")
                st.code(all_pages_text, language="plaintext")
