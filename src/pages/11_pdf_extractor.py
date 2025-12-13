# pdf_extractor_app.py
import streamlit as st
import os
from logic.PDFExtractor import PDFExtractor
from ui.ImageViewer import ImageViewer
from ui.SectionViewer import SectionViewer
from ui.SideMenu import SideMenu
from ui.TextViewer import TextViewer

# --- 外部ライブラリに関するコメント ---
# PDF解析と画像生成のため、PyMuPDF (fitz) を使用します。
# Streamlitを使用するため、streamlitライブラリも使用します。
# ------------------------------------
APP_TITLE = "PDF情報抽出・解析ツール"


def main():
    """
    Streamlitアプリケーションのメイン関数 (エントリポイント)。
    """
    st.set_page_config(page_title="PDF 情報抽出ツール", layout="wide")

    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.subheader(f"📄 {APP_TITLE}")
    st.markdown("研究用途における情報収集と解析の初期プロセスを加速します。")

    # --- 状態管理 ---
    # 状態の初期化
    if "pdf_path" not in st.session_state:
        st.session_state["pdf_path"] = None
    if "pdf_extractor" not in st.session_state:
        st.session_state["pdf_extractor"] = None
    if "processing_done" not in st.session_state:
        st.session_state["processing_done"] = False

    # --- F-1: PDFアップロード ---
    uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf")

    if uploaded_file is not None:
        if st.session_state[
            "pdf_path"
        ] is None or uploaded_file.name != os.path.basename(
            st.session_state["pdf_path"]
        ):
            # 新しいファイルがアップロードされた場合の処理
            temp_path = os.path.join("/tmp", uploaded_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ロジック層のインスタンス化
            if st.session_state["pdf_extractor"]:
                st.session_state["pdf_extractor"].close_pdf()

            st.session_state["pdf_path"] = temp_path
            st.session_state["pdf_extractor"] = PDFExtractor(temp_path)
            st.session_state["processing_done"] = False
            st.success(
                f"ファイル: **{uploaded_file.name}** をアップロードしました。"
            )
        else:
            st.info(
                f"ファイル: **{uploaded_file.name}** が既にロードされています。"
            )

        # --- F-2: 情報抽出開始ボタン ---
        if st.button(
            "🚀 情報抽出を開始",
            type="primary",
            disabled=st.session_state["processing_done"],
        ):
            with st.spinner("PDFを解析中..."):
                try:
                    extractor = st.session_state["pdf_extractor"]
                    extractor.load_pdf()
                    extractor.extract_metadata()
                    extractor.extract_text()
                    extractor.extract_sections()
                    st.session_state["processing_done"] = True
                    st.success("🎉 情報抽出が完了しました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"情報抽出中に致命的なエラーが発生しました: {e}")
                    st.session_state["processing_done"] = False
                    # エラーが発生したらPDFファイルをクローズ
                    if extractor:
                        extractor.close_pdf()

    elif st.session_state["pdf_path"] is not None:
        # PDFファイルが削除/クリアされた場合のセッションリセット
        st.session_state["pdf_path"] = None
        if st.session_state["pdf_extractor"]:
            st.session_state["pdf_extractor"].close_pdf()
        st.session_state["pdf_extractor"] = None
        st.session_state["processing_done"] = False
        st.warning("PDFファイルがクリアされました。")

    # --- 結果表示エリア ---
    if (
        st.session_state["processing_done"]
        and st.session_state["pdf_extractor"]
    ):
        extractor: PDFExtractor = st.session_state["pdf_extractor"]
        pdf_basename = os.path.basename(st.session_state["pdf_path"])

        st.header("🔍 抽出結果")
        st.info(
            f"処理済みファイル: **{pdf_basename}** ({extractor.get_page_count()} ページ)"
        )

        # UIコンポーネントのインスタンス化と描画
        tab_sections, tab_text, tab_images = st.tabs(
            ["📑 セクション情報", "📜 テキスト情報", "🖼️ ページ画像"]
        )

        with tab_sections:
            SectionViewer(extractor.get_full_structure()).render()

        with tab_text:
            # TextViewerは内部でStreamlitの状態管理に依存するため、
            # ロジック層のテキストデータを渡す
            TextViewer(extractor.get_page_texts()).render()

        with tab_images:
            # ImageViewerは内部でロジック層 (PDFExtractor) を呼び出す
            ImageViewer(extractor, pdf_basename).render()

    else:
        st.info(
            """左側のサイドバーからPDFファイルをアップロードし、
            「情報抽出を開始」ボタンを押してください。
            """
        )

        # 処理完了時にpdf_extractorを確実に閉じる処理 (メモリリーク防止)
        if (
            "pdf_extractor" in st.session_state
            and st.session_state["pdf_extractor"]
        ):
            st.session_state["pdf_extractor"].close_pdf()


if __name__ == "__main__":
    # --- サイドメニュー ---
    side_menu = SideMenu()
    side_menu.render_menu()

    # --- Main画面 ---
    main()
