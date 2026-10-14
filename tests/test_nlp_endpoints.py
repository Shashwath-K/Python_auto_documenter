import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api.endpoints import (
    api_nlp_options, 
    api_nlp_preprocess, 
    NLPPreprocessRequest,
    AISummaryRequest
)

async def test_nlp_options():
    res = await api_nlp_options()
    assert res["status"] == "online"
    assert res["library"] == "NLTK"
    assert "tokenizers" in res
    print("[OK] test_nlp_options passed")

async def test_nlp_preprocess_text():
    req = NLPPreprocessRequest(
        text="Natural language processing with NLTK helps optimize automated documentation workflows.",
        to_lower=True,
        remove_stopwords=True,
        lemmatization=True
    )
    res = await api_nlp_preprocess(req)
    assert res.original_token_count > 0
    assert res.stopwords_removed > 0
    assert len(res.keywords) > 0
    print("[OK] test_nlp_preprocess_text passed")

async def test_nlp_preprocess_code():
    code_text = """
    # Helper to calculate token frequency distributions
    def get_token_stats(tokens):
        \"\"\"Extract vocabulary size and lexical diversity.\"\"\"
        return len(tokens)
    """
    req = NLPPreprocessRequest(
        text=code_text,
        is_code=True
    )
    res = await api_nlp_preprocess(req)
    assert res.original_token_count > 0
    assert res.lexical_diversity > 0
    print("[OK] test_nlp_preprocess_code passed")

def main():
    asyncio.run(test_nlp_options())
    asyncio.run(test_nlp_preprocess_text())
    asyncio.run(test_nlp_preprocess_code())
    print("All endpoint unit tests passed successfully!")

if __name__ == "__main__":
    main()
