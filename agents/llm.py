"""
Configuration du LLM OpenAI pour Co-Gerant
"""
import os
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def get_llm(**kwargs) -> BaseChatModel:
    """
    Retourne le modele LLM OpenAI configure.
    
    Args:
        **kwargs: Arguments supplementaires pour le modele
    
    Returns:
        BaseChatModel: Instance du modele de chat OpenAI
    
    Raises:
        ValueError: Si la cle API OpenAI est manquante
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY non definie dans le fichier .env. "
            "Veuillez ajouter votre cle API OpenAI."
        )
    
    model_name = kwargs.get('model_name', os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
    temperature = kwargs.get('temperature', float(os.getenv('OPENAI_TEMPERATURE', 0.7)))
    max_tokens = kwargs.get('max_tokens', int(os.getenv('OPENAI_MAX_TOKENS', 1000)))
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )


def get_llm_for_intent_analysis() -> BaseChatModel:
    """
    Retourne un LLM specialise pour l'analyse d'intention.
    Utilise un modele rapide et economique.
    """
    return get_llm(
        model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.3,
        max_tokens=200
    )


def get_llm_for_response() -> BaseChatModel:
    """
    Retourne un LLM pour la generation de reponses.
    """
    return get_llm(
        model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.7,
        max_tokens=1000
    )


def get_llm_for_decision() -> BaseChatModel:
    """
    Retourne un LLM pour l'agent Decision (recommandations strategiques).
    Utilise un modele plus puissant pour des analyses approfondies.
    """
    return get_llm(
        model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.5,
        max_tokens=2000
    )


def get_llm_for_communication() -> BaseChatModel:
    """
    Retourne un LLM pour l'agent Communication (messages de relance).
    """
    return get_llm(
        model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.7,
        max_tokens=500
    )


def get_llm_for_crm_analysis() -> BaseChatModel:
    """
    Retourne un LLM pour l'analyse CRM approfondie.
    """
    return get_llm(
        model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.3,
        max_tokens=800
    )


def get_llm_for_sales_analysis() -> BaseChatModel:
    """
    Retourne un LLM pour l'analyse des ventes approfondie.
    """
    return get_llm(
        model_name=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.3,
        max_tokens=800
    )