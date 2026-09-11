import warnings
from app.core.config import settings


def get_llm():
    """Return an Ollama LLM instance, or raise RuntimeError if unavailable."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            from langchain_ollama import OllamaLLM
            return OllamaLLM(base_url=settings.OLLAMA_HOST, model=settings.DEFAULT_MODEL)
        except ImportError:
            pass
        try:
            from langchain_community.llms import Ollama
            return Ollama(base_url=settings.OLLAMA_HOST, model=settings.DEFAULT_MODEL)
        except ImportError:
            raise RuntimeError("No Ollama LLM backend available. Install langchain-ollama or langchain-community.")
