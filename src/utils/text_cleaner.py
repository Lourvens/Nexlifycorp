"""Text cleaning utilities for SEC filings and documents."""
import re
from typing import Set


REMOVE_CHARS: Set[int] = {
    # Box-drawing characters (U+2500-U+257F)
    0x2500, 0x2501, 0x2502, 0x2503,  # ─│┌┐
    0x2504, 0x2505, 0x2506, 0x2507,  # ┍┑┎┏
    0x2508, 0x2509, 0x250A, 0x250B,  # ┒┓┖┗
    0x250C, 0x250D, 0x250E, 0x250F,  # ┌┍┎┏
    0x2510, 0x2511, 0x2512, 0x2513,  # ┐┑┒┓
    0x2514, 0x2515, 0x2516, 0x2517,  # └┘┙┚
    0x2518, 0x2519, 0x251A, 0x251B,  # ┛├┝┞
    0x251C, 0x251D, 0x251E, 0x251F,  # ├┑┒┓
    0x2520, 0x2521, 0x2522, 0x2523,  # ┠┡┢┣
    0x2524, 0x2525, 0x2526, 0x2527,  # ┤┥┦┧
    0x2528, 0x2529, 0x252A, 0x252B,  # ┨┩┪┫
    0x252C, 0x252D, 0x252E, 0x252F,  # ┬┭┮┯
    0x2530, 0x2531, 0x2532, 0x2533,  # ┰┱┲┳
    0x2534, 0x2535, 0x2536, 0x2537,  # ┴┵┶┷
    0x2538, 0x2539, 0x253A, 0x253B,  # ┸┹┺┻
    0x253C, 0x253D, 0x253E, 0x253F,  # ┼┽┾┿
    0x2540, 0x2541, 0x2542, 0x2543,  # ╀╁╂╃
    0x2544, 0x2545, 0x2546, 0x2547,  # ╄╅╆╇
    0x2548, 0x2549, 0x254A, 0x254B,  # ╈╉╊╋
    0x254C, 0x254D, 0x254E, 0x254F,  # ╌╍═
    0x2550, 0x2551, 0x2552, 0x2553,  # ═║╒╓
    0x2554, 0x2555, 0x2556, 0x2557,  # ╔╕╖╗
    0x2558, 0x2559, 0x255A, 0x255B,  # ╘╙╚╛
    0x255C, 0x255D, 0x255E, 0x255F,  # ╜╝╞╟
    0x2560, 0x2561, 0x2562, 0x2563,  # ╠╡╢╣
    0x2564, 0x2565, 0x2566, 0x2567,  # ╤╥╦╧
    0x2568, 0x2569, 0x256A, 0x256B,  # ╨╩╪╫
    0x256C, 0x256D, 0x256E, 0x256F,  # ╬╭╮╯
    0x2570, 0x2571, 0x2572, 0x2573,  # ╰╱╲╳
    0x2574, 0x2575, 0x2576, 0x2577,  # ╴╵╶╷
    0x2578, 0x2579, 0x257A, 0x257B,  # ╸╹╺╻
    0x257C, 0x257D, 0x257E, 0x257F,  # ╼╽╾╿
}


def clean_text(text: str) -> str:
    """
    Clean extracted text from SEC filings.

    Removes:
    - Non-breaking spaces (\xa0)
    - Box-drawing characters (U+2500-U+257F)
    - Multiple consecutive spaces
    - Trailing/leading whitespace from lines
    - Lines that are only box-drawing characters
    - Consecutive empty lines
    - Page footers (e.g., "Apple Inc. | 2024 Form 10-K | 21")
    - Section separators

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return text

    # 1. Replace non-breaking spaces with regular spaces
    text = text.replace('\xa0', ' ')

    # 2. Remove box-drawing characters
    text = ''.join(
        c if ord(c) not in REMOVE_CHARS else ''
        for c in text
    )

    # 3. Remove page footers pattern: "Company | Form | Page"
    # Pattern: "[Company Name] | [Year] Form [Type] | [Page Number]"
    # Example: "Apple Inc. | 2024 Form 10-K | 5"
    text = re.sub(
        r'[A-Z][a-z]+(?:\.[a-z]+)?(?: Inc\.?| Corp\.?| Company)?\s*\|\s*\d{4}\s+Form\s+\d+-[A-Z]\s*\|\s*\d+',
        '',
        text,
        flags=re.IGNORECASE
    )

    # 4. Remove standalone page numbers (lines with just numbers)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # 5. Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # 6. Replace tabs with spaces
    text = text.replace('\t', ' ')

    # 7. Strip trailing/leading whitespace from each line
    lines = [line.strip() for line in text.split('\n')]

    # 8. Remove lines that are only box-drawing characters, spaces, or numbers
    lines = [
        line for line in lines
        if line and not re.match(r'^[\s\u2500-\u257F\-=_0-9]+$', line)
    ]

    # 9. Remove consecutive empty lines
    lines = [line for line in lines if line]

    # 10. Join with single newlines
    text = '\n'.join(lines)

    return text.strip()


def clean_section_header(header: str) -> str:
    """
    Clean a section header (e.g., "Item 1.       Business").

    Args:
        header: Raw header text

    Returns:
        Cleaned header (e.g., "Item 1. Business")
    """
    if not header:
        return header

    # Remove non-breaking spaces
    header = header.replace('\xa0', ' ')

    # Normalize multiple spaces to single
    header = re.sub(r' {2,}', ' ', header)

    # Remove leading/trailing whitespace
    header = header.strip()

    return header


def extract_section_title(item_line: str) -> str | None:
    """
    Extract clean section title from an item line.

    Example:
        "Item 1.       Business" -> "Business"
        "Item 1A. Risk Factors" -> "Risk Factors"
        "Item 7. Management's Discussion..." -> "Management's Discussion..."

    Args:
        item_line: Line containing Item number and title

    Returns:
        Clean section title or None if not an item line
    """
    if not item_line:
        return None

    # Match patterns like "Item X. Title" or "Item XA. Title"
    match = re.match(r'Item\s+\d+[A-Z]?\.\s*(.+)', item_line)
    if match:
        title = match.group(1).strip()
        # Normalize internal spacing
        title = re.sub(r' {2,}', ' ', title)
        return title

    return None