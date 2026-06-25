"""
State partagé pour l'orchestrateur LangGraph
"""
from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime

class AgentState(TypedDict, total=False):
    """État partagé du graphe LangGraph"""
    
    # Entrée utilisateur
    requete: str
    utilisateur_id: int
    entreprise_id: int
    
    # Contexte
    profil_entreprise: Dict[str, Any]  # Secteur, objectifs, services prioritaires
    historique_conversation: List[Dict[str, str]]  # Historique des échanges
    memoire: Optional[Dict[str, Any]]  # Résumé de la mémoire
    
    # Résultats du routage
    agent_selectionne: Optional[str]  # 'crm', 'ventes', 'communication', 'decision'
    intention: Optional[str]  # Intention détectée
    
    # Résultats des agents
    resultat_crm: Optional[str]
    resultat_ventes: Optional[str]
    resultat_communication: Optional[str]
    resultat_decision: Optional[str]
    
    # Sortie finale
    reponse_finale: Optional[str]
    notification_necessaire: bool
    notification_message: Optional[str]
    
    # Métadonnées
    erreur: Optional[str]
    temps_execution: Optional[float]