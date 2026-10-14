import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.text_preprocessing import preprocessor

def test_clean_text():
    raw = "Check out https://github.com for   nlp pre-processing!  "
    cleaned = preprocessor.clean_text(raw, remove_urls=True, to_lower=True)
    assert "https://" not in cleaned
    assert "check out for nlp pre-processing!" in cleaned

def test_tokenization_and_stopwords():
    text = "Natural Language Processing with NLTK is powerful and exciting for documentation."
    res = preprocessor.process(text, to_lower=True, remove_stopwords=True, lemmatization=True)
    
    assert res["original_token_count"] > 0
    assert res["stopwords_removed"] > 0
    assert "processing" in res["tokens"] or "process" in res["tokens"]
    assert "natural" in res["tokens"]
    assert len(res["keywords"]) > 0

def test_stemming_and_lemmatization():
    tokens = ["running", "cats", "corpora", "better"]
    stems = preprocessor.stem_tokens(tokens)
    assert stems[0] == "run"
    assert stems[1] == "cat"

    lemmas = preprocessor.lemmatize_tokens(tokens)
    assert lemmas[1] == "cat"

def test_code_comments_preprocessing():
    code = '''
    def calculate_metrics(data):
        """
        Calculates lexical metrics and statistical summaries for documents.
        """
        # Remove noisy tokens and punctuation
        x = 10
        return x
    '''
    res = preprocessor.preprocess_code_comments(code)
    assert res["original_token_count"] > 0
    assert any("metric" in k["word"] or "calcul" in k["word"] or "document" in k["word"] for k in res["keywords"])

if __name__ == "__main__":
    test_clean_text()
    test_tokenization_and_stopwords()
    test_stemming_and_lemmatization()
    test_code_comments_preprocessing()
    print("All tests passed successfully!")
