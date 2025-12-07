# utils/filter_text_lines.py
import re
from typing import List


def filter_text_lines(text: str, regex_patterns: List[str]) -> str:
    """
    テキストから正規表現パターンにマッチする行を除外する。

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
        except re.error:
            # Streamlitに依存するエラー表示はここでは行わない
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
