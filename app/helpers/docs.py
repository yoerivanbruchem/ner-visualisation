from typing import List, Tuple

from spacy.tokens import Doc, Span


def merge_spans(
    text: str,
    doc_spans: List[Tuple[int, int, str]],
    user_spans: List[Tuple[int, int, str]],
) -> List[Tuple[int, int, str]]:
    """
    Merge doc spans and user spans, remove invalid/empty, drop overlaps naively
    (keep first), and return sorted by start index.
    """
    spans = []
    for span, entity, label in doc_spans + user_spans:
        if span is None or entity is None:
            continue
        if not (0 <= span < entity <= len(text)):
            continue
        spans.append((int(span), int(entity), str(label)))

    # sort by (start, -length) so larger entities at same start are kept first
    spans.sort(key=lambda t: (t[0], -(t[1] - t[0])))

    merged = []
    last_end = -1
    for span, entity, label in spans:
        if span >= last_end:  # no overlap with previous kept span
            merged.append((span, entity, label))
            last_end = entity
        # If overlapping, skip; simpler than nesting for demo purposes
    return merged


def convert_user_additions_to_spans(
    user_ents_in: List[dict], doc: Doc  # type: ignore[type-arg]
) -> List[Tuple[int, int, str]]:
    """
    Convert user additions to spans; validate through char_span to respect tokenization
    Use alignment_mode='contract' so slightly misaligned boundaries still create a Span.
    """
    user_spans: List[Tuple[int, int, str]] = []
    for it in user_ents_in:
        s, e, label = it.get("start"), it.get("end"), it.get("label") or "MISC"
        try:
            span: Span | None = doc.char_span(
                int(s), int(e), label=str(label), alignment_mode="contract"  # type: ignore[arg-type]
            )
        except Exception:
            span = None
        if span is not None and (span.end_char - span.start_char) > 0:
            user_spans.append((span.start_char, span.end_char, span.label_))
        # If span is None (totally incompatible), we silently drop it in this demo
    return user_spans
