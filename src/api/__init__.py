"""FastAPI Backend - simple functions"""

from .rag import search_glossary, load_glossary

__all__ = ['search_glossary', 'load_glossary']
