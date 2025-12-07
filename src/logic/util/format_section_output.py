# format_section_output.py
import json
from typing import Dict, Any

# --- メタデータ表示用のマッピング (任意) ---
METADATA_LABELS = {
    "title": "タイトル",
    "author": "作成者",
    "subject": "サブジェクト（主題）",
    "keywords": "キーワード",
    "creator": "オリジナル文書の作成ツール",
    "producer": "変換ツール",
    "creationDate": "作成日時",
    "modDate": "更新日時",
    "trapped": "トラッピング",
}


# --- UIコンポーネント (関数) ---
def format_section_output(
    full_structure: Dict[str, Any], format_type: str
) -> str:
    """
    メタデータとセクション情報を含む構造全体を指定された形式に整形する。
    """
    metadata = full_structure.get("metadata", {})
    sections = full_structure.get("sections", [])

    # 1. JSON形式の処理
    if format_type == "JSON":
        # 構造化された辞書全体をJSONとして出力
        return json.dumps(full_structure, ensure_ascii=False, indent=2)

    # 2. テキスト/コード表示形式の処理
    output_lines = []

    # メタデータの整形 (F-5)
    output_lines.append("### 📄 PDFメタデータ")
    if metadata:
        for key, value in metadata.items():
            label = METADATA_LABELS.get(key.lower(), key.capitalize())
            # 日付文字列を整形するロジックは複雑になるため、ここではそのまま表示
            output_lines.append(f"{label}: {value}")
    else:
        output_lines.append("メタデータ情報はありませんでした。")

    output_lines.append("\n" + "=" * 40 + "\n")
    output_lines.append("### 📑 セクション (目次) リスト")

    # セクション情報の整形 (F-5)
    if not sections:
        output_lines.append("セクション情報はありませんでした。")
        return "\n".join(output_lines)

    for sec in sections:
        level = sec.get("level", 1)
        title = sec.get("title", "不明なセクション")
        page = sec.get("page", 0)

        # F-5 の形式: <Chapter/Section番号>： <タイトル> ... <ページ番号>
        prefix = "  " * (level - 1)
        section_number = f"[{level}]" if level > 0 else "[?] "
        formatted_line = f"{prefix}{section_number}： {title} ... (P.{page})"
        output_lines.append(formatted_line)

    return "\n".join(output_lines)
