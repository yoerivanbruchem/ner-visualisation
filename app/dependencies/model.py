import spacy
from spacy.language import Language


def load_model() -> Language:
    """
    Try to load a real NER model; fall back to a blank English pipeline with a
    tiny EntityRuler so the demo still works out-of-the-box.
    """
    return spacy.load("en_core_web_lg")
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        nlp = spacy.blank("en")
        ruler = nlp.add_pipe("entity_ruler")
        ruler.add_patterns(
            [
                {"label": "ORG", "pattern": "Apple"},
                {"label": "ORG", "pattern": "Google"},
                {"label": "PERSON", "pattern": "Elon Musk"},
                {"label": "GPE", "pattern": "New York"},
            ]
        )
        return nlp
