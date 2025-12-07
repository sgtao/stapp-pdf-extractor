# SectionViewer.py
import streamlit as st
from typing import List, Dict, Any

from logic.util.format_section_output import format_section_output


# --- UIコンポーネント (関数) ---
class SectionViewer:
    """
    セクション情報のタブ表示を管理するUIクラス。
    """

    def __init__(self, sections: List[Dict[str, Any]]):
        self.sections = sections

    def render(self) -> None:
        """セクション情報をStreamlitのタブで表示する。"""
        st.subheader("セクション (目次) 情報")
        section_tabs = st.tabs(["整形済みテキスト", "コード形式", "JSON形式"])

        with section_tabs[0]:  # テキスト表示
            st.markdown("### 整形済みテキスト")
            st.text(format_section_output(self.sections, "TEXT"))

        with section_tabs[1]:  # st.code表示 (コピー容易性のため)
            st.markdown("### コード形式")
            st.code(
                format_section_output(self.sections, "TEXT"),
                language="plaintext",
            )

        with section_tabs[2]:  # JSON形式
            st.markdown("### 構造化 JSON データ")
            st.json(self.sections)
