import html
from typing import List, Tuple


def render_entities_html(text: str, spans: List[Tuple[int, int, str]]) -> str:
    """
    Convert raw text + [(start, end, label)] into HTML with custom span wrappers.
    We preserve the rest of the text as plain, escaped text. The output text
    content remains identical to the input (no extra characters), so selection
    offsets computed in the browser match original char positions.
    """
    pieces = []
    cursor = 0
    for start, end, label in spans:
        if start > cursor:
            pieces.append(html.escape(text[cursor:start]))
        ent_txt = html.escape(text[start:end])
        # Custom tag + data attributes for downstream actions
        pieces.append(
            f'<span class="ent" '
            f'data-label="{html.escape(label)}" '
            f'data-start="{start}" '
            f'data-end="{end}" '
            f'data-text="{ent_txt}">{ent_txt}</span>'
        )
        cursor = end
    if cursor < len(text):
        pieces.append(html.escape(text[cursor:]))
    return "".join(pieces)
