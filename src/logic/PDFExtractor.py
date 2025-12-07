# PDFExtractor.py
import fitz

# import json
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO


# --- コアロジック ---
class PDFExtractor:
    """
    PDFファイルからテキスト、セクション情報、ページ画像を抽出し、保持するクラス
    (Streamlit非依存のコアロジック)
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
        self.metadata: Dict[str, Any] = {}

    def load_pdf(self) -> None:
        """
        PDFファイルをPyMuPDF (fitz) で開く。
        """
        try:
            # エラー処理は呼び出し元 (pages/01_pdf_extractor_app.py) で
            # Streamlitのウィジェットを使って行う
            self.doc = fitz.open(self.pdf_file_path)
        except Exception:
            # Streamlitに依存するエラー表示はここでは行わない
            raise

    def extract_text(self) -> None:
        """
        PDFの全ページからテキストを抽出し、page_textsに格納する。
        """
        if not self.doc:
            raise ValueError("PDFがロードされていません。")

        self.page_texts = [page.get_text("text") for page in self.doc]

    def extract_metadata(self) -> None:
        """
        PDFドキュメントのメタデータを抽出し、self.metadataに格納する。
        """
        if not self.doc:
            raise ValueError("PDFがロードされていません。")

        # PyMuPDFのメタデータをそのまま取得
        raw_meta = self.doc.metadata

        # 不要な/扱いにくい情報を除外し、表示用に整形
        cleaned_meta = {}
        if raw_meta:
            for key, value in raw_meta.items():
                # fitzのメタデータキーは大文字・小文字が混ざるため、TitleやAuthorを
                # ユーザーフレンドリーな形式で保持

                # CreateDateとModDateはそのまま保持し、UI層で整形してもよい
                if key in [
                    "title",
                    "author",
                    "subject",
                    "keywords",
                    "creator",
                    "producer",
                    "creationDate",
                    "modDate",
                    "trapped",
                ]:
                    cleaned_meta[key] = value

        self.metadata = cleaned_meta

    def extract_sections(self) -> None:
        """
        PDFの目次/アウトライン情報およびテキスト解析に基づきセクション情報を抽出する。
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
                if any(kw in line for kw in keywords) and len(line) < 80:
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
        """
        if not self.doc:
            raise ValueError("PDFがロードされていません。")
        if page_number < 1 or page_number > len(self.doc):
            return None

        try:
            page = self.doc[page_number - 1]
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")

            return BytesIO(img_data)
        except Exception:
            # Streamlitに依存する警告はここでは行わない
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

    def get_full_structure(self) -> Dict[str, Any]:
        """
        メタデータとセクション情報を含む構造化された辞書を返す。
        """
        return {"metadata": self.metadata, "sections": self.sections}
