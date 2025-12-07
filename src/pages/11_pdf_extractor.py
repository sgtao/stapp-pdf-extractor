# pdf_extractor.py
import streamlit as st
import os
import re
import json
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO

# --- 外部ライブラリに関するコメント ---
# PDF解析と画像生成のため、PyMuPDF (fitz) を使用します。
# Streamlitを使用するため、streamlitライブラリも使用します。
# ------------------------------------

# --- クラス設計 ---
# PDFの処理とデータの保持を一元管理するクラスを設計します。


class PDFExtractor:
    """
    PDFファイルからテキスト、セクション情報、ページ画像を抽出し、保持するクラス
    """

    def __init__(self, pdf_file_path: str):
        """
        コンストラクタ。PDFファイルのパスを初期化する。

        Args:
            pdf_file_path: 解析対象のPDFファイルのパス。
        """
        self.pdf_file_path = pdf_file_path
        self.doc: Optional[fitz.Document] = None
        self.page_texts: List[str] = []
        self.sections: List[Dict[str, Any]] = []

    def load_pdf(self) -> None:
        """
        PDFファイルをPyMuPDF (fitz) で開く。
        """
        try:
            self.doc = fitz.open(self.pdf_file_path)
        except Exception as e:
            st.error(f"PDFファイルの読み込み中にエラーが発生しました: {e}")
            raise

    def extract_text(self) -> None:
        """
        PDFの全ページからテキストを抽出し、page_textsに格納する。
        """
        if not self.doc:
            raise ValueError("PDFがロードされていません。")

        self.page_texts = [page.get_text("text") for page in self.doc]

    def extract_sections(self) -> None:
        """
        PDFの目次/アウトライン情報およびテキスト解析に基づきセクション情報を抽出する。
        F-3: 見出しレベル（アウトライン）と特定のキーワード（テキスト解析）を使用。
        ここではPyMuPDFのアウトライン (目次) 情報を主なセクション情報として抽出する。
        """
        if not self.doc:
            raise ValueError("PDFがロードされていません。")

        # fitzの目次 (アウトライン) 情報を抽出
        toc: List[Tuple[int, str, int]] = self.doc.get_toc()

        # 特定のキーワードに基づいたセクション抽出 (シンプルな実装)
        keyword_sections: List[Dict[str, Any]] = []
        keywords = [
            "概要",
            "結論",
            "はじめに",
            "序論",
            "結果",
            "考察",
            "謝辞",
            "付録",
        ]

        for i, text in enumerate(self.page_texts):
            lines = text.split("\n")
            for line in lines[:5]:  # 各ページ先頭5行程度をチェック
                # ページの先頭行にキーワードが含まれるかチェック
                if any(kw in line for kw in keywords) and len(line) < 80:
                    # 短い行をタイトルと見なす
                    # 同じページに既にアウトライン情報があればスキップ
                    #  (簡略化のため)
                    if not any(t[2] == i + 1 for t in toc):
                        keyword_sections.append(
                            {
                                "level": 1,
                                "title": line.strip(),
                                "page": i + 1,
                            }
                        )
                        break

        # アウトライン情報とキーワード情報を結合
        self.sections = []
        for level, title, page in toc:
            # fitzのページ番号は1から始まる
            if page > 0:
                self.sections.append(
                    {"level": level, "title": title, "page": page}
                )

        # キーワードセクションを追加 (アウトラインと重複しないように)
        for kw_sec in keyword_sections:
            if not any(
                s["title"] == kw_sec["title"] and s["page"] == kw_sec["page"]
                for s in self.sections
            ):
                self.sections.append(kw_sec)

        # ページ番号順にソート
        self.sections.sort(key=lambda x: x["page"])

    def generate_page_snapshot(self, page_number: int) -> Optional[BytesIO]:
        """
        指定されたページ番号（1始まり）のPNGスナップショットを生成する。
        F-10: PDFの全ページについて、PNG形式のスナップショットを生成する。

        Args:
            page_number: 抽出対象のページ番号（1始まり）。

        Returns:
            PNGデータのBytesIOオブジェクト。エラーの場合はNone。
        """
        if not self.doc:
            raise ValueError("PDFがロードされていません。")
        if page_number < 1 or page_number > len(self.doc):
            return None

        try:
            # PyMuPDFのページインデックスは0始まり
            page = self.doc[page_number - 1]

            # ズーム設定 (高解像度画像)
            zoom = 2.0  # 2倍の解像度
            mat = fitz.Matrix(zoom, zoom)

            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")

            return BytesIO(img_data)
        except Exception as e:
            st.warning(
                f"ページ {page_number} の画像生成中にエラーが発生しました: {e}"
            )
            return None

    def close_pdf(self) -> None:
        """
        開いているPDFファイルを閉じる。
        """
        if self.doc:
            self.doc.close()
            self.doc = None

    def get_page_count(self) -> int:
        """
        PDFの総ページ数を取得する。
        """
        return len(self.doc) if self.doc else 0

    def get_sections(self) -> List[Dict[str, Any]]:
        """
        抽出されたセクション情報を取得する。
        """
        return self.sections

    def get_page_texts(self) -> List[str]:
        """
        抽出されたページごとのテキストを取得する。
        """
        return self.page_texts


# --- Streamlit アプリケーション ---


def format_section_output(
    sections: List[Dict[str, Any]], format_type: str
) -> str:
    """
    セクション情報を指定された形式に整形する。
    F-4: テキスト、st.code (JSON/コード形式)、JSON形式をサポート。
    F-5: 「<Chapter/Section番号>： <タイトル> ... <ページ番号>」の形式で表示。
    """
    if not sections:
        return "セクション情報はありませんでした。"

    if format_type == "JSON":
        return json.dumps(sections, ensure_ascii=False, indent=2)

    # テキスト/コード表示形式
    output_lines = []

    for sec in sections:
        level = sec.get("level", 1)
        title = sec.get("title", "不明なセクション")
        page = sec.get("page", 0)

        # 簡易的なセクション番号表示 (levelを使用)
        prefix = "  " * (level - 1)
        section_number = f"[{level}]" if level > 0 else "[?] "

        # F-5 の形式: <Chapter/Section番号>： <タイトル> ... <ページ番号>
        formatted_line = f"{prefix}{section_number}： {title} ... (P.{page})"
        output_lines.append(formatted_line)

    return "\n".join(output_lines)


def filter_text_lines(text: str, regex_patterns: List[str]) -> str:
    """
    テキストから正規表現パターンにマッチする行を除外する。
    F-8, F-9: 除外行設定を適用する。

    Args:
        text: 処理対象のテキスト。
        regex_patterns: 除外する行にマッチする正規表現パターンのリスト。

    Returns:
        除外処理後のテキスト。
    """
    if not regex_patterns:
        return text

    lines = text.split("\n")
    filtered_lines = []

    # パターンをコンパイル
    compiled_patterns = []
    for pattern in regex_patterns:
        try:
            if pattern.strip():
                compiled_patterns.append(re.compile(pattern.strip()))
        except re.error as e:
            st.error(f"正規表現エラー: パターン '{pattern}' が無効です ({e})")
            return text  # エラー時はフィルタリングを中止

    if not compiled_patterns:
        return text

    for line in lines:
        is_excluded = False
        for pattern in compiled_patterns:
            if pattern.search(line):
                is_excluded = True
                break

        if not is_excluded:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)


def main():
    """
    Streamlitアプリケーションのメイン関数。
    """
    st.set_page_config(page_title="PDF情報抽出・解析ツール", layout="wide")

    st.title("📄 PDF情報抽出・解析ツール")
    st.markdown("研究用途における情報収集と解析の初期プロセスを加速します。")

    # --- 状態管理 ---
    if "pdf_path" not in st.session_state:
        st.session_state["pdf_path"] = None
    if "pdf_extractor" not in st.session_state:
        st.session_state["pdf_extractor"] = None
    if "regex_count" not in st.session_state:
        # F-9: 除外行入力の初期値 (1つ)
        st.session_state["regex_count"] = 1
    if "processing_done" not in st.session_state:
        st.session_state["processing_done"] = False

    # --- F-1: PDFアップロード ---
    uploaded_file = st.sidebar.file_uploader(
        "PDFファイルをアップロード", type="pdf"
    )

    if uploaded_file is not None:
        # ファイルの保存
        if st.session_state[
            "pdf_path"
        ] is None or uploaded_file.name != os.path.basename(
            st.session_state["pdf_path"]
        ):
            # 新しいファイルがアップロードされた場合
            temp_path = os.path.join(
                "/tmp", uploaded_file.name
            )  # 環境に依存しない一時パス
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            # メモリ内のファイルを一時的に書き出す
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 古いインスタンスがあれば閉じる
            if st.session_state["pdf_extractor"]:
                st.session_state["pdf_extractor"].close_pdf()

            st.session_state["pdf_path"] = temp_path
            st.session_state["pdf_extractor"] = PDFExtractor(temp_path)
            st.session_state["processing_done"] = False
            st.sidebar.success(
                f"ファイル: **{uploaded_file.name}** をアップロードしました。"
            )
        else:
            st.sidebar.info(
                f"ファイル: **{uploaded_file.name}** が既にロードされています。"
            )

        # --- F-2: 情報抽出開始ボタン ---
        if st.sidebar.button(
            "🚀 情報抽出を開始",
            type="primary",
            disabled=st.session_state["processing_done"],
        ):
            with st.spinner("PDFを解析中... (最大10秒程度)"):
                try:
                    extractor = st.session_state["pdf_extractor"]
                    extractor.load_pdf()
                    extractor.extract_text()
                    extractor.extract_sections()
                    st.session_state["processing_done"] = True
                    st.success("🎉 情報抽出が完了しました！")
                    # 結果表示のために再実行
                    st.rerun()
                except Exception as e:
                    st.error(f"情報抽出中に致命的なエラーが発生しました: {e}")
                    st.session_state["processing_done"] = False

    elif st.session_state["pdf_path"] is not None:
        # アップロードエリアが空になったが、
        # セッションに情報が残っている場合 (リロード時など)
        st.session_state["pdf_path"] = None
        if st.session_state["pdf_extractor"]:
            st.session_state["pdf_extractor"].close_pdf()
        st.session_state["pdf_extractor"] = None
        st.session_state["processing_done"] = False
        st.sidebar.warning("PDFファイルがクリアされました。")

    # --- 結果表示エリア ---
    if (
        st.session_state["processing_done"]
        and st.session_state["pdf_extractor"]
    ):
        extractor = st.session_state["pdf_extractor"]

        st.header("🔍 抽出結果")
        _pdf_basename = os.path.basename(st.session_state["pdf_path"])
        _page_count = extractor.get_page_count()
        st.info(
            f"処理済みファイル: **{_pdf_basename}** ({_page_count} ページ)"
        )

        # --- タブ切り替え ---
        tab_sections, tab_text, tab_images = st.tabs(
            ["📑 セクション情報", "📜 テキスト情報", "🖼️ ページ画像"]
        )

        with tab_sections:
            # --- F-3, F-4, F-5: セクション情報 ---
            st.subheader("セクション (目次) 情報")
            sections = extractor.get_sections()

            section_tabs = st.tabs(
                ["整形済みテキスト", "コード形式", "JSON形式"]
            )

            with section_tabs[0]:  # テキスト表示
                st.markdown("### 整形済みテキスト")
                st.text(format_section_output(sections, "TEXT"))

            with section_tabs[1]:  # st.code表示 (コピー容易性のため)
                st.markdown("### コード形式")
                st.code(
                    format_section_output(sections, "TEXT"),
                    language="plaintext",
                )

            with section_tabs[2]:  # JSON形式
                st.markdown("### 構造化 JSON データ")
                st.json(sections)

        with tab_text:
            # --- F-7, F-8, F-9: テキスト情報と除外行設定 ---
            st.subheader("抽出テキスト")

            # F-9: 除外行入力（正規表現パターン）
            with st.expander(
                "⚙️ 除外行 正規表現パターンの設定", expanded=False
            ):
                col_ctrl, col_patterns = st.columns([1, 4])

                # パターン数の増減
                current_count = st.session_state["regex_count"]
                new_count = col_ctrl.number_input(
                    "パターン数", min_value=1, value=current_count, step=1
                )
                if new_count != current_count:
                    st.session_state["regex_count"] = new_count
                    st.rerun()

                # パターン入力
                regex_patterns = []
                st.markdown("---")
                for i in range(st.session_state["regex_count"]):
                    # セッションステートで永続化
                    key = f"regex_pattern_{i}"
                    default_value = (
                        st.session_state.get(key, r"^\s*Page\s+\d+\s*$")
                        if i == 0
                        else ""
                    )  # F-9: 初期は1つ
                    st.session_state[key] = st.text_input(
                        f"除外パターン {i+1} (正規表現)",
                        value=default_value,
                        key=f"input_{key}",
                        placeholder=r"例: フッターのページ番号 (^\s*\d+\s*$)",
                    )
                    regex_patterns.append(st.session_state[key])

            # テキストの取得とフィルタリング
            page_texts = extractor.get_page_texts()

            text_tabs = st.tabs(["整形済みテキスト", "コード形式"])

            with text_tabs[0]:  # テキスト表示 (F-7-1)
                st.markdown("### ページごとのテキスト (フィルタリング適用)")
                for i, text in enumerate(page_texts):
                    # F-6: ページ単位で「## ページ xx」と見出しを表示
                    st.markdown(f"#### ページ {i + 1}")
                    filtered_text = filter_text_lines(text, regex_patterns)
                    st.text(filtered_text)

            with text_tabs[1]:  # st.code表示 (F-7-2)
                st.markdown(
                    "### ページごとのテキスト (コード形式・フィルタリング適用)"
                )
                for i, text in enumerate(page_texts):
                    # F-6: ページ単位で「## ページ xx」と見出しを表示
                    st.markdown(f"#### ページ {i + 1}")
                    filtered_text = filter_text_lines(text, regex_patterns)
                    st.code(filtered_text, language="plaintext")

        with tab_images:
            # --- F-10, F-11, F-12: ページ画像 ---
            st.subheader("ページスナップショット (PNG)")

            page_count = extractor.get_page_count()

            for i in range(1, page_count + 1):
                # F-11: 各ページをst.expanderで折り畳み表示
                with st.expander(f"🖼️ ページ {i} を表示 (PNG)", expanded=False):
                    snapshot_bytes = extractor.generate_page_snapshot(i)

                    if snapshot_bytes:
                        # 画像の表示
                        st.image(
                            snapshot_bytes,
                            caption=f"ページ {i} スナップショット",
                            use_container_width=True,
                        )

                        # F-12: 各ページのPNG画像について、個別にダウンロードボタン
                        _pdf_basename = os.path.basename(
                            st.session_state["pdf_path"]
                        )
                        _png_file = (
                            f"{_pdf_basename.replace('.pdf', '')}_page_{i}.png"
                        )
                        st.download_button(
                            label=f"⬇️ ページ {i} 画像をダウンロード",
                            data=snapshot_bytes.getvalue(),
                            file_name=_png_file,
                            mime="image/png",
                        )
                    else:
                        st.warning(f"ページ {i} の画像生成に失敗しました。")

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
            # ここでは何もしない
            # 理由：F-10 画像生成処理が完了した後も doc は開いている可能性があるため


if __name__ == "__main__":
    main()
