# ImageViewer.py
import streamlit as st
from logic.PDFExtractor import PDFExtractor


class ImageViewer:
    """
    ページ画像の生成、表示、ダウンロードを管理するUIクラス。
    """

    def __init__(self, extractor: PDFExtractor, pdf_basename: str):
        self.extractor = extractor
        self.pdf_basename = pdf_basename

    def render(self) -> None:
        """ページ画像をStreamlitのexpanderで表示し、ダウンロードボタンを設ける。"""
        st.subheader("ページスナップショット (PNG)")
        page_count = self.extractor.get_page_count()

        for i in range(1, page_count + 1):
            # F-11: 各ページをst.expanderで折り畳み表示
            with st.expander(f"🖼️ ページ {i} を表示 (PNG)", expanded=False):
                # ロジック層を呼び出して画像データを取得
                snapshot_bytes = self.extractor.generate_page_snapshot(i)

                if snapshot_bytes:
                    # 画像の表示
                    st.image(
                        snapshot_bytes,
                        caption=f"ページ {i} スナップショット",
                        width="stretch",
                    )

                    # F-12: 個別にダウンロードボタン
                    _png_file = (
                        f"{self.pdf_basename.replace('.pdf', '')}_page_{i}.png"
                    )
                    st.download_button(
                        label=f"⬇️ ページ {i} 画像をダウンロード",
                        data=snapshot_bytes.getvalue(),
                        file_name=_png_file,
                        mime="image/png",
                    )
                else:
                    st.warning(f"ページ {i} の画像生成に失敗しました。")
