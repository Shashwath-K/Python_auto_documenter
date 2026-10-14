import re
import string
from collections import Counter
from typing import List, Dict, Any, Optional

# Lazy loading / resilient import of NLTK
_NLTK_READY = False
_stopwords_set = set()
_stemmer = None
_lemmatizer = None

def _initialize_nltk():
    global _NLTK_READY, _stopwords_set, _stemmer, _lemmatizer
    if _NLTK_READY:
        return
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.stem import PorterStemmer, WordNetLemmatizer

        # Attempt to access resources; download if not present
        try:
            _stopwords_set = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            _stopwords_set = set(stopwords.words('english'))

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)

        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)

        _stemmer = PorterStemmer()
        _lemmatizer = WordNetLemmatizer()
        _NLTK_READY = True
    except Exception as e:
        # Fallback to robust regex-based tokens & basic stopwords
        _stopwords_set = {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
            "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
            "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
            "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", 
            "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
            "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
            "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", 
            "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", 
            "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
            "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
            "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
            "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
            "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
            "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
            "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", 
            "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours"
        }
        _NLTK_READY = True


class TextPreprocessor:
    """
    NLP Text Preprocessing Engine leveraging NLTK with fallback resilience.
    Supports tokenization, stopword removal, stemming, lemmatization, and lexical statistics.
    """

    def __init__(self):
        _initialize_nltk()

    @staticmethod
    def clean_text(text: str, remove_urls: bool = True, remove_special: bool = False, to_lower: bool = False) -> str:
        """
        Cleans and normalizes raw text.
        """
        if not text:
            return ""
        
        result = text
        if remove_urls:
            result = re.sub(r'https?://\S+|www\.\S+', '', result)
        
        if to_lower:
            result = result.lower()
            
        if remove_special:
            result = re.sub(r'[^\w\s]', ' ', result)
            
        # Normalize whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        return result

    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Splits text into sentences using NLTK sent_tokenize or regex fallback.
        """
        if not text:
            return []
        try:
            import nltk
            return nltk.sent_tokenize(text)
        except Exception:
            return [s.strip() for s in re.split(r'[.!?]+(?:\s+|$)', text) if s.strip()]

    def tokenize_words(self, text: str, remove_punctuation: bool = True) -> List[str]:
        """
        Splits text into word tokens using NLTK word_tokenize or regex fallback.
        """
        if not text:
            return []
        
        try:
            import nltk
            tokens = nltk.word_tokenize(text)
        except Exception:
            tokens = re.findall(r'\b\w+\b', text)
            
        if remove_punctuation:
            tokens = [t for t in tokens if t not in string.punctuation and re.search(r'\w', t)]
            
        return tokens

    def remove_stopwords(self, tokens: List[str], custom_stopwords: Optional[set] = None) -> List[str]:
        """
        Removes stopwords from a list of tokens.
        """
        stops = _stopwords_set
        if custom_stopwords:
            stops = stops.union(custom_stopwords)
            
        return [t for t in tokens if t.lower() not in stops]

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Applies Porter Stemmer to tokens.
        """
        global _stemmer
        if not _stemmer:
            try:
                from nltk.stem import PorterStemmer
                _stemmer = PorterStemmer()
            except Exception:
                return tokens
        return [_stemmer.stem(t) for t in tokens]

    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Applies WordNet Lemmatizer to tokens.
        """
        global _lemmatizer
        if not _lemmatizer:
            try:
                from nltk.stem import WordNetLemmatizer
                _lemmatizer = WordNetLemmatizer()
            except Exception:
                return tokens
        return [_lemmatizer.lemmatize(t.lower()) for t in tokens]

    def extract_keywords(self, tokens: List[str], top_n: int = 10, min_len: int = 3) -> List[Dict[str, Any]]:
        """
        Extracts high-frequency non-stopword keywords from tokens.
        """
        filtered = [t.lower() for t in tokens if len(t) >= min_len and t.lower() not in _stopwords_set]
        counter = Counter(filtered)
        return [{"word": word, "count": count} for word, count in counter.most_common(top_n)]

    def process(
        self,
        text: str,
        to_lower: bool = True,
        remove_punctuation: bool = True,
        remove_stopwords: bool = True,
        stemming: bool = False,
        lemmatization: bool = True,
        extract_keywords_count: int = 8
    ) -> Dict[str, Any]:
        """
        End-to-end NLTK preprocessing pipeline returning rich analytics and processed text.
        """
        if not text or not text.strip():
            return {
                "original_text": "",
                "processed_text": "",
                "token_count": 0,
                "processed_token_count": 0,
                "unique_token_count": 0,
                "stopwords_removed": 0,
                "lexical_diversity": 0.0,
                "tokens": [],
                "keywords": []
            }

        # Sentence tokenization
        sentences = self.tokenize_sentences(text)
        
        # Word tokenization
        raw_tokens = self.tokenize_words(text, remove_punctuation=remove_punctuation)
        original_token_count = len(raw_tokens)
        
        tokens = [t.lower() if to_lower else t for t in raw_tokens]
        
        # Stopword removal
        stopwords_removed_count = 0
        if remove_stopwords:
            before_count = len(tokens)
            tokens = self.remove_stopwords(tokens)
            stopwords_removed_count = before_count - len(tokens)

        # Morphological normalization: Lemmatization takes precedence over Stemming if both enabled
        if lemmatization:
            tokens = self.lemmatize_tokens(tokens)
        elif stemming:
            tokens = self.stem_tokens(tokens)

        # Analytics
        unique_tokens = set(t.lower() for t in tokens)
        lexical_diversity = round(len(unique_tokens) / max(len(tokens), 1), 3)
        keywords = self.extract_keywords(tokens, top_n=extract_keywords_count)
        processed_text = " ".join(tokens)

        return {
            "original_text": text,
            "processed_text": processed_text,
            "sentence_count": len(sentences),
            "original_token_count": original_token_count,
            "processed_token_count": len(tokens),
            "unique_token_count": len(unique_tokens),
            "stopwords_removed": stopwords_removed_count,
            "lexical_diversity": lexical_diversity,
            "tokens": tokens[:100],  # cap sample preview
            "keywords": keywords
        }

    def preprocess_code_comments(self, code: str) -> Dict[str, Any]:
        """
        Extracts docstrings and comments from Python/source code and runs NLP preprocessing.
        """
        # Extract triple-quoted docstrings and single-line # comments
        docstrings = re.findall(r'\"\"\"(.*?)\"\"\"', code, flags=re.DOTALL)
        single_comments = re.findall(r'#\s*(.*?)$', code, flags=re.MULTILINE)
        
        combined_text = "\n".join(docstrings + single_comments).strip()
        if not combined_text:
            # Fallback to identifier extraction from code
            identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', code)
            combined_text = " ".join(identifiers)

        return self.process(combined_text)


# Singleton instance
preprocessor = TextPreprocessor()
