import warnings
import logging
from typing import Dict, Optional
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


class BaseAgent:
    """
    Base class for all agents in the AutoTest AI system.
    Provides common functionality like logging and LLM initialization.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """
        Initialize the LLM (Language Model) for AI operations.
        Returns None if LLM is not available or not needed.
        """
        try:
            # Try OpenAI first if API key is available
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                try:
                    from langchain_openai import ChatOpenAI
                    return ChatOpenAI(
                        model="gpt-4",
                        temperature=0.7,
                        api_key=settings.OPENAI_API_KEY
                    )
                except ImportError:
                    self.logger.warning("langchain-openai not installed")
            
            # Fallback to Ollama
            return get_llm()
        except Exception as e:
            self.logger.warning(f"LLM initialization failed: {e}")
            return None
    
    def run(self, input_data: Dict) -> Dict:
        """
        Main execution method for the agent.
        Must be implemented by subclasses.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Dict with execution results
        """
        raise NotImplementedError("Subclasses must implement run() method")

