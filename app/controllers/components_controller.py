from typing import Dict, List

from flask import Blueprint, Response, current_app, request

from ..helpers.docs import convert_user_additions_to_spans, merge_spans
from ..helpers.render import render_entities_html

components_controller = Blueprint(
    "components_controller",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
    url_prefix="/components",
)


@components_controller.route("/analyze/", methods=["POST"])
def components() -> Response:
    data = request.get_json(silent=True) or {}
    text: str = (
        data.get("text")
        or """"
        Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal,
        thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious,
        because they just didn't hold with such nonsense.
        Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly
        any neck, although he did have a very large mustache. Mrs. Dursley was thin and blonde and had nearly twice
        the usual amount of neck, which came in very useful as she spent so much of her time craning over garden fences,
        spying on the neighbors.
        The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere.
        """
    )
    user_ents_in: List[Dict] = data.get("user_ents") or []  # type: ignore[type-arg]

    # Run spaCy
    nlp = current_app.nlp  # type: ignore[attr-defined]
    doc = nlp(text)

    # From spaCy model
    doc_spans = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]

    user_spans = convert_user_additions_to_spans(user_ents_in, doc)

    # Merge, render
    merged = merge_spans(text, doc_spans, user_spans)
    html_out = render_entities_html(text, merged)

    return Response(html_out, mimetype="text/html")
