"""
Construction du graphe LangGraph
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    noeud_superviseur,
    noeud_agent_crm,
    noeud_agent_ventes,
    noeud_agent_communication,
    noeud_agent_decision,
    noeud_memoire,
    noeud_synthese,
    router_superviseur
)
from core.models import Utilisateur


def creer_graphe() -> StateGraph:
    """
    Crée et configure le graphe LangGraph.
    """
    print("[Graph] Création du graphe...")
    
    # Créer le graphe avec l'état partagé
    graph = StateGraph(AgentState)
    
    # Ajouter les nœuds
    graph.add_node("memoire", noeud_memoire)
    graph.add_node("superviseur", noeud_superviseur)
    graph.add_node("agent_crm", noeud_agent_crm)
    graph.add_node("agent_ventes", noeud_agent_ventes)
    graph.add_node("agent_communication", noeud_agent_communication)
    graph.add_node("agent_decision", noeud_agent_decision)
    graph.add_node("synthese", noeud_synthese)
    
    # Définir le point d'entrée
    graph.set_entry_point("memoire")
    
    # Transition de memoire vers superviseur
    graph.add_edge("memoire", "superviseur")
    
    # Ajouter les transitions conditionnelles du superviseur
    graph.add_conditional_edges(
        "superviseur",
        router_superviseur,
        {
            "agent_crm": "agent_crm",
            "agent_ventes": "agent_ventes",
            "agent_communication": "agent_communication",
            "agent_decision": "agent_decision"
        }
    )
    
    # Transitions des agents vers la synthèse
    graph.add_edge("agent_crm", "synthese")
    graph.add_edge("agent_ventes", "synthese")
    graph.add_edge("agent_communication", "synthese")
    graph.add_edge("agent_decision", "synthese")
    
    # Fin du graphe
    graph.add_edge("synthese", END)
    
    print("[Graph] Graphe créé avec succès")
    return graph


# ... (le reste du fichier reste identique)


# Instance unique du graphe
GLOBAL_GRAPH = None

def get_graph():
    """
    Récupère l'instance du graphe (singleton).
    """
    global GLOBAL_GRAPH
    if GLOBAL_GRAPH is None:
        GLOBAL_GRAPH = creer_graphe()
    return GLOBAL_GRAPH


def executer_agent(requete: str, utilisateur_id: int, historique: list = None) -> Dict[str, Any]:
    """
    Point d'entrée principal pour exécuter le graphe.
    
    Args:
        requete: La question de l'utilisateur
        utilisateur_id: ID de l'utilisateur
        historique: Historique des conversations
        
    Returns:
        Dictionnaire avec la réponse et les métadonnées
    """
    print(f"\n[Executer] Nouvelle requête: '{requete}'")
    print(f"[Executer] Utilisateur ID: {utilisateur_id}")
    
    try:
        # Récupérer l'utilisateur et son entreprise
        utilisateur = Utilisateur.objects.get(id=utilisateur_id)
        entreprise_id = utilisateur.entreprise.id if utilisateur.entreprise else None
        
        if not entreprise_id:
            return {
                'reponse': "⚠️ Vous devez être rattaché à une entreprise pour utiliser l'assistant.",
                'erreur': 'Entreprise non trouvée'
            }
        
        # Préparer l'état initial
        state = AgentState(
            requete=requete,
            utilisateur_id=utilisateur_id,
            entreprise_id=entreprise_id,
            historique_conversation=historique or [],
            notification_necessaire=False
        )
        
        # Compiler et exécuter le graphe
        graph = get_graph()
        compiled = graph.compile()
        
        # Exécuter
        resultat = compiled.invoke(state)
        
        # Extraire la réponse
        reponse = resultat.get('reponse_finale', 'Je n\'ai pas pu traiter votre demande.')
        
        return {
            'reponse': reponse,
            'notification_necessaire': resultat.get('notification_necessaire', False),
            'notification_message': resultat.get('notification_message', ''),
            'agent_utilise': resultat.get('agent_selectionne', 'inconnu'),
            'temps_execution': resultat.get('temps_execution', 0)
        }
        
    except Utilisateur.DoesNotExist:
        return {
            'reponse': "⚠️ Utilisateur non trouvé. Veuillez vous reconnecter.",
            'erreur': 'Utilisateur non trouvé'
        }
    except Exception as e:
        print(f"[Executer] Erreur: {str(e)}")
        return {
            'reponse': f"❌ Une erreur technique est survenue. Veuillez réessayer.",
            'erreur': str(e)
        }