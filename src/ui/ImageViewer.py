# ImageViewer.py
import streamlit as st

# import os
import zipfile
from io import BytesIO
from typing import Optional
from logic.PDFExtractor import PDFExtractor


class ImageViewer:
    """
    ページ画像の生成、表示、ダウンロードを管理するUIクラス。
    """

    def __init__(self, extractor: PDFExtractor, pdf_basename: str):
        self.extractor = extractor
        self.pdf_basename = pdf_basename

    @st.dialog(
        title="Screenshots in specified minute",
        # width="medium",
        width="small",
    )
    def _display_image_dialog(
        self, page_number: int, snapshot_bytes: BytesIO, file_name: str
    ):
        """
        st.dialog を使用して画像を拡大表示し、ダウンロードボタンを設ける。
        """
        # st.dialog は st.button() のコールバック内でのみ使用できるため、ここではキーを設定する
        # ストリームリットの制約により、実際のダイアログ表示はメインループ（render内）から
        # st.buttonが呼び出されたときにロジックとして実行されます。

        # NOTE: Streamlitでは、ボタンがクリックされたときに直接st.dialogを呼び出すのが最も簡単です。
        # この関数は、st.dialogのコンテンツを定義するために使用します。

        st.image(
            snapshot_bytes.getvalue(),
            caption=f"ページ {page_number} スナップショット (拡大)",
            # use_column_width=True,
        )

        # 個別ダウンロードボタン
        st.download_button(
            label=f"⬇️ ページ {page_number} 画像をダウンロード",
            data=snapshot_bytes.getvalue(),
            file_name=file_name,
            mime="image/png",
            key=f"dialog_download_{page_number}",
        )
        if st.button("Close"):
            st.rerun()
        # st.markdown(
        #     "画像を閉じるには、ダイアログの外側をクリックしてください。"
        # )

    def _create_zip_of_images(self) -> Optional[BytesIO]:
        """
        全てのページ画像をZIPファイルにまとめて BytesIO オブジェクトとして返す。
        """
        page_count = self.extractor.get_page_count()
        zip_buffer = BytesIO()
        pdf_name_base = self.pdf_basename.replace(".pdf", "")

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i in range(1, page_count + 1):
                snapshot_bytes = self.extractor.generate_page_snapshot(i)
                if snapshot_bytes:
                    png_file_name = f"{pdf_name_base}_page_{i}.png"
                    # ZIPファイルにBytesIOの中身を書き込む
                    zipf.writestr(png_file_name, snapshot_bytes.getvalue())
                # エラーページはスキップ

        # ZIPファイルにコンテンツがあるか確認
        if zipf.namelist():
            return zip_buffer
        else:
            return None

    def render(self) -> None:
        """ページ画像を5列のグリッドで表示し、拡大表示・一括ダウンロード機能を提供する。"""
        st.subheader("ページスナップショット (PNG)")
        page_count = self.extractor.get_page_count()

        COLS_PER_ROW = 5

        # 全ての画像データを事前にリストアップ（メモリ効率のために逐次処理も検討可だが、ここでは単純化）
        images_data = []
        for i in range(1, page_count + 1):
            snapshot_bytes = self.extractor.generate_page_snapshot(i)
            file_name = f"{self.pdf_basename.replace('.pdf', '')}_page_{i}.png"
            images_data.append((i, snapshot_bytes, file_name))

        # --- 1. グリッド表示と拡大ボタン ---
        st.markdown("#### ページプレビュー (クリックで拡大)")

        # Streamlitのcolumnsをループで生成
        cols = st.columns(COLS_PER_ROW)

        for i, (page_num, snapshot_bytes, file_name) in enumerate(images_data):
            col = cols[i % COLS_PER_ROW]

            with col:
                if snapshot_bytes:
                    # 小さく表示
                    st.image(
                        snapshot_bytes,
                        caption=f"P. {page_num}",
                        # use_column_width=True,
                    )

                    # 拡大/ダウンロードボタン (st.dialogを使うためボタンでイベントをトリガー)
                    # キーをセッションに登録して、ボタンクリックを検知
                    button_key = f"expand_btn_{page_num}"
                    if st.button("DL", key=button_key, icon="📥"):
                        # ボタンがクリックされたらダイアログを表示
                        self._display_image_dialog(
                            page_num, snapshot_bytes, file_name
                        )

                else:
                    st.warning(f"P. {page_num} 失敗")

        st.markdown("---")

        # --- 2. 全画像一括ダウンロードボタン ---
        st.markdown("#### 全ページ一括ダウンロード")

        zip_buffer = self._create_zip_of_images()

        if zip_buffer:
            zip_file_name = (
                f"{self.pdf_basename.replace('.pdf', '')}_all_pages.zip"
            )
            st.download_button(
                label="📦 全ページ画像をZIPでダウンロード",
                data=zip_buffer.getvalue(),
                file_name=zip_file_name,
                mime="application/zip",
            )
        else:
            st.error("ダウンロード可能な画像が見つかりませんでした。")
