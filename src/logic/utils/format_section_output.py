# format_section_output.py
import json
from typing import List, Dict, Any

# --- UIコンポーネント (関数) ---


def format_section_output(
    sections: List[Dict[str, Any]], format_type: str
) -> str:
    """
    セクション情報を指定された形式に整形する。
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

        # F-5 の形式: <Chapter/Section番号>： <タイトル> ... <ページ番号>
        prefix = "  " * (level - 1)
        section_number = f"[{level}]" if level > 0 else "[?] "
        formatted_line = f"{prefix}{section_number}： {title} ... (P.{page})"
        output_lines.append(formatted_line)

    return "\n".join(output_lines)
