# SectionViewer.py
import streamlit as st
from typing import Dict, Any

from logic.util.format_section_output import format_section_output


# --- UIコンポーネント (関数) ---
class SectionViewer:
    """
    セクション情報のタブ表示を管理するUIクラス。
    """

    def __init__(self, full_structure: Dict[str, Any]):
        # メタデータとセクション情報を含む構造全体を保持
        self.full_structure = full_structure

    def render(self) -> None:
        """セクション情報をStreamlitのタブで表示する。"""
        st.subheader("メタデータ・セクション情報")
        section_tabs = st.tabs(["整形済みテキスト", "コード形式", "JSON形式"])

        with section_tabs[0]:  # テキスト表示
            st.markdown("### 整形済みテキスト")
            # 引数をfull_structureに変更
            st.text(format_section_output(self.full_structure, "TEXT"))

        with section_tabs[1]:  # st.code表示 (コピー容易性のため)
            st.markdown("### コード形式")
            # 引数をfull_structureに変更
            st.code(
                format_section_output(self.full_structure, "TEXT"),
                language="plaintext",
            )

        with section_tabs[2]:  # JSON形式
            st.markdown("### 構造化 JSON データ")
            # JSON表示はそのままfull_structureを渡す
            st.json(self.full_structure)
