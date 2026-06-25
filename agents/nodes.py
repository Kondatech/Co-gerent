"""
Noeuds du graphe LangGraph - Version OpenAI
"""
import time
import json
import re
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from core.models import Utilisateur, ProfilEntreprise
from .state import AgentState
from .tools import AgentTools
from .llm import get_llm_for_intent_analysis, get_llm_for_response, get_llm_for_decision


class LLM:
    """Interface pour les appels LLM avec OpenAI"""
    
    @staticmethod
    def analyze_intent(requete: str) -> str:
        """
        Analyse l'intention de l'utilisateur en utilisant OpenAI.
        """
        try:
            llm = get_llm_for_intent_analysis()
            
            prompt = f"""
Analyse l'intention de l'utilisateur et retourne UNIQUEMENT l'un de ces mots:

IMPORTANT: 
- communication: pour les demandes de publication, messages, relances
- decision: pour les questions strategiques, de conseil, d'amelioration
- crm: pour les questions sur les clients, relances, RFM, segmentation
- ventes: pour les questions sur le chiffre d'affaires, les performances, les previsions

Exemples:
- "Publie une offre" -> communication
- "Genere un message" -> communication
- "comment augmenter mes ventes" -> decision
- "quels sont mes meilleurs clients" -> crm
- "quel est mon chiffre d'affaires" -> ventes

Requete: {requete}

Reponse (UNIQUEMENT le mot):"""
            
            response = llm.invoke(prompt)
            intention = response.content.strip().lower()
            
            # Fallback si le LLM ne renvoie pas un mot valide
            if intention not in ['crm', 'ventes', 'communication', 'decision']:
                return LLM._analyze_intent_fallback(requete)
            
            # Override pour les publications (securite)
            requete_lower = requete.lower()
            if any(kw in requete_lower for kw in ['publie', 'publication', 'post', 'annonce', 'publier']):
                print(f"[LLM] Override: publication detectee -> communication")
                return 'communication'
            
            # Verifier si c'est strategique
            strategie_keywords = ['comment', 'conseil', 'strategie', 'ameliorer', 
                                 'developper', 'augmenter', 'croissance', 'optimiser']
            if any(kw in requete_lower for kw in strategie_keywords):
                print(f"[LLM] Override: question strategique -> decision")
                return 'decision'
            
            return intention
            
        except Exception as e:
            print(f"[LLM] Erreur analyse intention: {e}. Utilisation du fallback.")
            return LLM._analyze_intent_fallback(requete)
    
    @staticmethod
    def _analyze_intent_fallback(requete: str) -> str:
        """Methode de fallback pour l'analyse d'intention"""
        requete_lower = requete.lower()
        
        # PRIORITE 1: Communication (publications)
        if any(kw in requete_lower for kw in ['publie', 'publication', 'post', 'annonce', 'publier', 'poster']):
            return 'communication'
        
        # PRIORITE 2: Questions strategiques
        strategie_keywords = ['comment', 'conseil', 'strategie', 'ameliorer', 
                             'developper', 'augmenter', 'croissance', 'optimiser',
                             'que dois-je', 'que puis-je', 'solution', 'grossir']
        if any(kw in requete_lower for kw in strategie_keywords):
            return 'decision'
        
        # PRIORITE 3: Communication (messages)
        communication_keywords = ['message', 'relance', 'email', 'communication', 'contenu']
        if any(kw in requete_lower for kw in communication_keywords):
            return 'communication'
        
        # PRIORITE 4: CRM
        crm_keywords = ['client', 'rfm', 'segment', 'fideliser', 'prospect', 'relancer']
        if any(kw in requete_lower for kw in crm_keywords):
            return 'crm'
        
        # PRIORITE 5: Ventes
        ventes_keywords = ['vente', 'ca', 'chiffre', 'affaire', 'performance', 'prevision']
        if any(kw in requete_lower for kw in ventes_keywords):
            return 'ventes'
        
        # Par defaut: Decision
        return 'decision'
    
    @staticmethod
    def generate_response(prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Genere une reponse avec OpenAI.
        """
        try:
            llm = get_llm_for_response()
            
            full_prompt = prompt
            if context:
                context_str = json.dumps(context, ensure_ascii=False, indent=2)
                full_prompt = f"""
Contexte:
{context_str}

{prompt}
"""
            
            response = llm.invoke(full_prompt)
            return response.content
            
        except Exception as e:
            print(f"[LLM] Erreur generation reponse: {e}")
            return f"Erreur: {str(e)}"
    
    @staticmethod
    def generate_decision(prompt: str, donnees: Dict[str, Any]) -> str:
        """
        Genere des recommandations strategiques avec OpenAI.
        """
        try:
            llm = get_llm_for_decision()
            
            full_prompt = f"""
Donnees disponibles:
{json.dumps(donnees, ensure_ascii=False, indent=2)}

{prompt}

Genere des recommandations strategiques claires et actionnables pour l'entreprise.

Structure ta reponse avec:
1. Des titres clairs pour chaque section
2. Des actions concretes
3. Des priorites (HAUTE, MOYENNE, BASSE)
4. Des impacts attendus

Reponds en francais, de maniere professionnelle et operationnelle."""
            
            response = llm.invoke(full_prompt)
            return response.content
            
        except Exception as e:
            print(f"[LLM] Erreur generation decision: {e}")
            return f"Erreur: {str(e)}"


# ============ NOEUDS DU GRAPHE ============

def noeud_superviseur(state: AgentState) -> Dict[str, Any]:
    """
    Noeud Superviseur : analyse la requete et decide quel agent activer.
    """
    print(f"[Superviseur] Traitement de la requete: {state.get('requete', '')}")
    
    requete = state.get('requete', '')
    if not requete:
        return {
            'erreur': 'Aucune requete fournie',
            'reponse_finale': "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?"
        }
    
    # Analyser l'intention avec OpenAI
    intention = LLM.analyze_intent(requete)
    
    # Override pour les publications (securite supplementaire)
    requete_lower = requete.lower()
    publication_keywords = ['publie', 'publication', 'post', 'annonce', 'publier', 'poster']
    if any(kw in requete_lower for kw in publication_keywords):
        print(f"[Superviseur] Override: publication detectee -> communication")
        intention = 'communication'
    
    # Override pour les questions strategiques
    strategie_keywords = ['comment', 'conseil', 'strategie', 'ameliorer', 
                         'developper', 'augmenter', 'croissance', 'optimiser',
                         'que dois-je', 'que puis-je', 'solution', 'grossir']
    if any(kw in requete_lower for kw in strategie_keywords) and intention != 'communication':
        print(f"[Superviseur] Override: question strategique -> decision")
        intention = 'decision'
    
    # Recuperer le profil entreprise pour contexte
    entreprise_id = state.get('entreprise_id')
    profil = None
    if entreprise_id:
        try:
            profil_entreprise = ProfilEntreprise.objects.get(entreprise_id=entreprise_id)
            profil = {
                'secteur': profil_entreprise.entreprise.secteur,
                'objectif_court_terme': profil_entreprise.objectif_court_terme,
                'objectif_long_terme': profil_entreprise.objectif_long_terme,
                'services_prioritaires': profil_entreprise.services_prioritaires
            }
        except ProfilEntreprise.DoesNotExist:
            pass
    
    print(f"[Superviseur] Intention detectee: {intention}")
    
    return {
        'agent_selectionne': intention,
        'intention': intention,
        'profil_entreprise': profil or {},
        'historique_conversation': state.get('historique_conversation', [])
    }


def noeud_agent_crm(state: AgentState) -> Dict[str, Any]:
    """
    Agent CRM : gere les clients, segments, RFM, relances.
    """
    print("[Agent CRM] Traitement de la requete...")
    debut = time.time()
    
    entreprise_id = state.get('entreprise_id')
    requete = state.get('requete', '')
    tools = AgentTools(entreprise_id) if entreprise_id else None
    
    if not tools:
        return {
            'resultat_crm': "Erreur: Aucune entreprise associee a l'utilisateur.",
            'erreur': 'Entreprise non trouvee'
        }
    
    try:
        resultats = []
        requete_lower = requete.lower()
        
        if 'top client' in requete_lower or 'meilleur client' in requete_lower or 'client' in requete_lower:
            top_clients = tools.get_top_clients(limit=5)
            if top_clients:
                resultats.append("MEILLEURS CLIENTS")
                resultats.append("")
                for i, client in enumerate(top_clients, 1):
                    resultats.append(
                        f"{i}. {client['nom']} - {client['segment']} - "
                        f"Score RFM: {client['score_rfm']} ({client['niveau_rfm']}) - "
                        f"CA: {client['montant_total_achats']:,.0f} FCFA"
                    )
            else:
                resultats.append("Aucun client trouve.")
        
        elif 'relancer' in requete_lower or 'relance' in requete_lower:
            clients_a_relancer = tools.get_clients_a_relancer()
            if clients_a_relancer:
                resultats.append("CLIENTS A RELANCER")
                resultats.append("")
                for client in clients_a_relancer[:5]:
                    resultats.append(
                        f"- {client['nom']} - {client['segment']} - "
                        f"Dernier achat: {client['dernier_achat']} ({client['jours_sans_achat']} jours)"
                    )
                resultats.append("")
                resultats.append("Conseil: Contactez ces clients pour renouer la relation.")
            else:
                resultats.append("Tous vos clients sont actifs, aucun besoin de relance.")
        
        elif 'statistique' in requete_lower or 'synthese' in requete_lower:
            stats = tools.get_statistiques_clients()
            resultats.append("SYNTHESE CRM")
            resultats.append("")
            resultats.append(f"- Total clients: {stats['total_clients']}")
            resultats.append(f"- Clients actifs: {stats['clients_actifs']} ({stats['taux_activite']}%)")
            resultats.append(f"- RFM moyen: {stats['rfm_moyen']}")
            resultats.append(f"- CA total clients: {stats['ca_total_clients']:,.0f} FCFA")
            resultats.append("")
            resultats.append("REPARTITION PAR SEGMENT")
            for segment, count in stats['segments'].items():
                if count > 0:
                    resultats.append(f"- {segment}: {count} clients")
        
        else:
            top_clients = tools.get_top_clients(limit=3)
            stats = tools.get_statistiques_clients()
            resultats.append("APERCU DE VOTRE CRM")
            resultats.append("")
            resultats.append(f"- {stats['total_clients']} clients au total, {stats['clients_actifs']} actifs")
            if top_clients:
                resultats.append(f"- Meilleur client: {top_clients[0]['nom']} ({top_clients[0]['montant_total_achats']:,.0f} FCFA)")
            resultats.append("")
            resultats.append("Que souhaitez-vous faire ?")
            resultats.append("- Voir mes top clients")
            resultats.append("- Gerer les relances")
            resultats.append("- Consulter les statistiques")
        
        temps = round(time.time() - debut, 2)
        resultat_final = "\n".join(resultats)
        
        print(f"[Agent CRM] Termine en {temps}s")
        
        return {
            'resultat_crm': resultat_final,
            'temps_execution': temps
        }
        
    except Exception as e:
        print(f"[Agent CRM] Erreur: {str(e)}")
        return {
            'resultat_crm': f"Erreur: {str(e)}",
            'erreur': str(e)
        }


def noeud_agent_ventes(state: AgentState) -> Dict[str, Any]:
    """
    Agent Ventes : gere le chiffre d'affaires, les performances, les previsions.
    """
    print("[Agent Ventes] Traitement de la requete...")
    debut = time.time()
    
    entreprise_id = state.get('entreprise_id')
    requete = state.get('requete', '')
    tools = AgentTools(entreprise_id) if entreprise_id else None
    
    if not tools:
        return {
            'resultat_ventes': "Erreur: Aucune entreprise associee a l'utilisateur.",
            'erreur': 'Entreprise non trouvee'
        }
    
    try:
        from ventes.models import Vente
        
        resultats = []
        requete_lower = requete.lower()
        
        if 'dernier' in requete_lower and 'vente' in requete_lower:
            ventes = Vente.objects.filter(
                entreprise_id=entreprise_id
            ).order_by('-date_vente')[:5]
            
            if ventes.exists():
                resultats.append("DERNIERES VENTES")
                resultats.append("")
                for vente in ventes:
                    client_nom = vente.client.nom if vente.client else "Client inconnu"
                    resultats.append(
                        f"- {vente.numero_facture} | {client_nom} | "
                        f"{vente.date_vente.strftime('%d/%m/%Y')} | "
                        f"{vente.montant_total:,.0f} FCFA | "
                        f"{vente.get_statut_display()}"
                    )
            else:
                resultats.append("Aucune vente enregistree")
        
        elif 'chiffre d\'affaire' in requete_lower or 'ca' in requete_lower:
            ca = tools.get_chiffre_affaires('mois')
            resultats.append("CHIFFRE D'AFFAIRES DU MOIS")
            resultats.append("")
            resultats.append(f"- CA total: {ca['ca_total']:,.0f} FCFA")
            resultats.append(f"- Nombre de ventes: {ca['nombre_ventes']}")
            resultats.append(f"- Panier moyen: {ca['panier_moyen']:,.0f} FCFA")
            if ca['evolution'] is not None:
                if ca['evolution'] > 0:
                    resultats.append(f"- Evolution: +{ca['evolution']}% par rapport a la periode precedente")
                else:
                    resultats.append(f"- Evolution: {ca['evolution']}% par rapport a la periode precedente")
            resultats.append(f"- Periode: {ca['date_debut']}")
            
            if ca['top_produits']:
                resultats.append("")
                resultats.append("TOP PRODUITS")
                for produit in ca['top_produits'][:3]:
                    resultats.append(f"- {produit['produit']}: {produit['total_quantite']} unites")
        
        elif 'prevision' in requete_lower or 'projection' in requete_lower:
            prev = tools.get_previsions_ventes()
            resultats.append("PREVISIONS DE VENTES")
            resultats.append("")
            resultats.append(f"- CA mensuel moyen: {prev['ca_mensuel_moyen']:,.0f} FCFA")
            resultats.append(f"- Projection 30 jours: {prev['projection_30_jours']:,.0f} FCFA")
            resultats.append(f"- Ventes mensuelles moyennes: {prev['nombre_ventes_mensuel_moyen']}")
            resultats.append(f"- Base sur les {prev['periode_reference']}")
        
        elif 'performance' in requete_lower or 'kpi' in requete_lower:
            perf = tools.get_performance_ventes()
            resultats.append("PERFORMANCE DES VENTES")
            resultats.append("")
            resultats.append(f"- CA ce mois: {perf['ca_mois_courant']:,.0f} FCFA")
            if perf['evolution_mensuelle'] > 0:
                resultats.append(f"- Evolution: +{perf['evolution_mensuelle']}%")
            else:
                resultats.append(f"- Evolution: {perf['evolution_mensuelle']}%")
            resultats.append(f"- Taux de conversion: {perf['taux_conversion']}%")
            resultats.append(f"- Objectif mensuel: {perf['objectif_mensuel']:,.0f} FCFA")
            
            if perf['ca_mois_courant'] < perf['objectif_mensuel'] * 0.8:
                resultats.append("")
                resultats.append("ATTENTION: Vous etes en dessous de votre objectif. Augmentez vos efforts commerciaux !")
        
        else:
            ventes = Vente.objects.filter(
                entreprise_id=entreprise_id
            ).order_by('-date_vente')[:5]
            
            if ventes.exists():
                resultats.append("DERNIERES VENTES")
                resultats.append("")
                for vente in ventes:
                    client_nom = vente.client.nom if vente.client else "Client inconnu"
                    resultats.append(
                        f"- {vente.numero_facture} | {client_nom} | "
                        f"{vente.date_vente.strftime('%d/%m/%Y')} | "
                        f"{vente.montant_total:,.0f} FCFA | "
                        f"{vente.get_statut_display()}"
                    )
            else:
                resultats.append("Aucune vente enregistree")
            
            resultats.append("")
            resultats.append("Que souhaitez-vous faire ?")
            resultats.append("- Voir le CA detaille")
            resultats.append("- Consulter les previsions")
            resultats.append("- Analyser la performance")
        
        temps = round(time.time() - debut, 2)
        resultat_final = "\n".join(resultats)
        
        print(f"[Agent Ventes] Termine en {temps}s")
        
        return {
            'resultat_ventes': resultat_final,
            'temps_execution': temps
        }
        
    except Exception as e:
        print(f"[Agent Ventes] Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'resultat_ventes': f"Erreur: {str(e)}",
            'erreur': str(e)
        }


def noeud_synthese(state: AgentState) -> Dict[str, Any]:
    """
    Noeud Synthese : recompose la reponse finale.
    """
    print("[Synthese] Generation de la reponse finale...")
    
    agent = state.get('agent_selectionne')
    reponse_finale = ""
    notification_necessaire = False
    notification_message = None
    
    print(f"[Synthese] Agent recu: {agent}")
    print(f"[Synthese] Resultat CRM: {state.get('resultat_crm', 'NON PRESENT')}")
    print(f"[Synthese] Resultat Ventes: {state.get('resultat_ventes', 'NON PRESENT')}")
    print(f"[Synthese] Resultat Communication: {state.get('resultat_communication', 'NON PRESENT')}")
    print(f"[Synthese] Resultat Decision: {state.get('resultat_decision', 'NON PRESENT')}")
    
    if agent == 'crm':
        reponse_finale = state.get('resultat_crm', "Desole, je n'ai pas pu traiter votre demande.")
        if 'relancer' in reponse_finale.lower():
            notification_necessaire = True
            notification_message = "Des clients sont a relancer. Consultez le rapport."
            
    elif agent == 'ventes':
        reponse_finale = state.get('resultat_ventes', "Desole, je n'ai pas pu traiter votre demande.")
        if 'en dessous' in reponse_finale.lower() or 'progression' in reponse_finale.lower():
            notification_necessaire = True
            notification_message = "Attention: vos ventes sont en dessous de l'objectif."
    
    elif agent == 'communication':
        reponse_finale = state.get('resultat_communication', "Desole, je n'ai pas pu traiter votre demande.")
        # Verifier si une publication est en attente
        if state.get('action_en_attente'):
            notification_necessaire = True
            notification_message = "Une publication est en attente de confirmation."
    
    elif agent == 'decision':
        reponse_finale = state.get('resultat_decision', "Desole, je n'ai pas pu traiter votre demande.")
        if 'HAUTE' in reponse_finale or 'URGENT' in reponse_finale:
            notification_necessaire = True
            notification_message = "Une recommendation strategique prioritaire est disponible."
    
    else:
        print(f"[Synthese] AGENT INCONNU: {agent}")
        reponse_finale = "Je ne comprends pas votre demande. Pouvez-vous reformuler ?"
    
    print(f"[Synthese] Reponse finale: {reponse_finale[:100]}...")
    print("[Synthese] Reponse generee avec succes")
    
    return {
        'reponse_finale': reponse_finale,
        'notification_necessaire': notification_necessaire,
        'notification_message': notification_message
    }


# ============ NOUVEAUX NOEUDS ============

def noeud_memoire(state: AgentState) -> Dict[str, Any]:
    """
    Noeud Memoire : lit et ecrit dans la memoire longue.
    """
    print("[Memoire] Acces a la memoire...")
    
    entreprise_id = state.get('entreprise_id')
    
    if not entreprise_id:
        return {'memoire': None}
    
    try:
        from core.models import ResumeMemoire
        
        memoires = ResumeMemoire.objects.filter(
            entreprise_id=entreprise_id
        ).order_by('-date_maj')
        
        if memoires.exists():
            derniere_memoire = memoires.first()
            memoire = {
                'contenu': derniere_memoire.contenu_resume,
                'date': derniere_memoire.date_maj.isoformat(),
                'dernier_sujet': derniere_memoire.dernier_sujet,
                'decisions': derniere_memoire.decisions_prises,
                'recommandations': derniere_memoire.recommandations
            }
            print(f"[Memoire] Memoire chargee: {len(memoire['contenu'])} caracteres")
        else:
            memoire = {
                'contenu': "Premiere interaction avec l'entreprise.",
                'date': None,
                'dernier_sujet': '',
                'decisions': [],
                'recommandations': []
            }
            print("[Memoire] Aucune memoire existante, creation d'une nouvelle.")
        
        return {'memoire': memoire}
        
    except Exception as e:
        print(f"[Memoire] Erreur: {str(e)}")
        return {'memoire': None, 'erreur': str(e)}


def noeud_agent_communication(state: AgentState) -> Dict[str, Any]:
    """
    Agent Communication : genere des messages de relance et gere les publications Facebook.
    Version avec publication automatique (sans confirmation).
    """
    print("[Agent Communication] Traitement de la requete...")
    debut = time.time()
    
    entreprise_id = state.get('entreprise_id')
    requete = state.get('requete', '')
    tools = AgentTools(entreprise_id) if entreprise_id else None
    
    if not tools:
        return {
            'resultat_communication': "Erreur: Aucune entreprise associee.",
            'erreur': 'Entreprise non trouvee'
        }
    
    try:
        resultats = []
        requete_lower = requete.lower()
        
        # ============================================
        # DETECTION DES PUBLICATIONS FACEBOOK
        # ============================================
        publication_keywords = ['publie', 'publication', 'annonce', 'post sur facebook', 'programme un post', 'poster']
        
        if any(kw in requete_lower for kw in publication_keywords):
            # Extraire le contenu et la date
            contenu = requete
            date_publication = None
            
            # Extraire la date si mentionnee
            date_patterns = [
                r'à\s*(\d{1,2})h\s*(aujourd\'hui|aujourd\'hui)?',
                r'demain\s*à?\s*(\d{1,2})h',
                r'aujourd\'hui\s*à?\s*(\d{1,2})h',
                r'(\d{1,2})h\s*(aujourd\'hui|demain)?',
                r'(\d{2})/(\d{2})/(\d{4})\s*(\d{1,2})h',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, requete_lower)
                if match:
                    if 'aujourd\'hui' in requete_lower:
                        date_publication = "aujourd'hui"
                    elif 'demain' in requete_lower:
                        date_publication = "demain"
                    else:
                        date_publication = match.group(0)
                    break
            
            # Verifier la connexion Facebook
            connexion = tools.verifier_connexion_facebook()
            
            if not connexion['connecte']:
                resultats.append(f"Information: {connexion['message']}")
                resultats.append(f"➡️ {connexion.get('lien', '/communication/integrations/')}")
            else:
                # Preparer le brouillon
                brouillon = tools.preparer_publication_facebook(contenu, date_publication)
                
                if not brouillon.get('pret'):
                    resultats.append(f"Erreur: {brouillon.get('erreur', 'Erreur inconnue')}")
                else:
                    # ============================================
                    # PUBLICATION AUTOMATIQUE - SANS CONFIRMATION
                    # ============================================
                    # Creer la publication
                    resultat_publication = tools.confirmer_publication_facebook(
                        brouillon['contenu'],
                        brouillon.get('date_publication')
                    )
                    
                    if resultat_publication.get('succes'):
                        if resultat_publication.get('statut') == 'programmee':
                            resultats.append("PUBLICATION PROGRAMMEE")
                            resultats.append("")
                            resultats.append(resultat_publication['message'])
                            resultats.append("")
                            resultats.append(f"Page: {brouillon['page_nom']}")
                            resultats.append("")
                            resultats.append("---")
                            resultats.append(brouillon['contenu'])
                            resultats.append("---")
                        else:
                            resultats.append("PUBLICATION PUBLIEE AVEC SUCCES")
                            resultats.append("")
                            resultats.append(resultat_publication['message'])
                            if resultat_publication.get('url'):
                                resultats.append(f"Lien: {resultat_publication['url']}")
                            resultats.append("")
                            resultats.append("---")
                            resultats.append(brouillon['contenu'])
                            resultats.append("---")
                    else:
                        resultats.append(f"Erreur lors de la publication: {resultat_publication.get('erreur', 'Erreur inconnue')}")
        
        # ============================================
        # DETECTION DES RELANCES
        # ============================================
        elif 'relance' in requete_lower or 'message' in requete_lower:
            client_match = re.search(r'pour\s+(\w+)', requete)
            client_nom = client_match.group(1) if client_match else None
            
            if client_nom:
                message = tools.generer_message_relance(client_nom)
                resultats.append(message)
            else:
                clients_a_relancer = tools.get_clients_a_relancer()
                if clients_a_relancer:
                    resultats.append("CLIENTS A RELANCER")
                    resultats.append("")
                    for client in clients_a_relancer[:3]:
                        resultats.append(f"- {client['nom']} ({client['telephone']}) - Dernier achat: {client['dernier_achat']}")
                    
                    resultats.append("")
                    resultats.append("Dites-moi 'Genere un message pour [nom du client]' pour creer un message personnalise.")
                else:
                    resultats.append("Tous vos clients sont actifs. Aucun besoin de relance pour le moment.")
        
        else:
            # Message par defaut
            resultats.append("ASSISTANT COMMUNICATION")
            resultats.append("")
            resultats.append("Je peux vous aider a :")
            resultats.append("  - Generer des messages de relance pour vos clients")
            resultats.append("  - Publier sur votre page Facebook")
            resultats.append("")
            resultats.append("Exemples :")
            resultats.append("  - 'Genere un message de relance pour Nadia'")
            resultats.append("  - 'Publie une offre pour un ordinateur a 700 000 FCFA'")
            resultats.append("  - 'Quels sont les clients a relancer ?'")
        
        temps = round(time.time() - debut, 2)
        resultat_final = "\n".join(resultats)
        
        print(f"[Agent Communication] Termine en {temps}s")
        
        return {
            'resultat_communication': resultat_final,
            'temps_execution': temps,
            'action_en_attente': state.get('action_en_attente')
        }
        
    except Exception as e:
        print(f"[Agent Communication] Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'resultat_communication': f"Erreur: {str(e)}",
            'erreur': str(e)
        }


def noeud_agent_decision(state: AgentState) -> Dict[str, Any]:
    """
    Agent Decision : synthetise les sorties des autres agents en recommandations.
    Version amelioree pour les questions strategiques.
    """
    print("[Agent Decision] Generation des recommandations...")
    debut = time.time()
    
    entreprise_id = state.get('entreprise_id')
    utilisateur_id = state.get('utilisateur_id')
    tools = AgentTools(entreprise_id) if entreprise_id else None
    requete = state.get('requete', '')
    
    if not tools:
        return {
            'resultat_decision': "Erreur: Aucune entreprise associee.",
            'erreur': 'Entreprise non trouvee'
        }
    
    try:
        donnees = {}
        
        try:
            stats_crm = tools.get_statistiques_clients()
            donnees['crm'] = stats_crm
        except:
            pass
        
        try:
            perf_ventes = tools.get_performance_ventes()
            ca = tools.get_chiffre_affaires('mois')
            previsions = tools.get_previsions_ventes()
            donnees['ventes'] = perf_ventes
            donnees['ca'] = ca
            donnees['previsions'] = previsions
        except:
            pass
        
        try:
            clients_potentiels = tools.analyser_clients_a_fort_potentiel()
            donnees['clients_potentiels'] = clients_potentiels
        except:
            pass
        
        try:
            produits_sous_performants = tools.analyser_produits_sous_performants()
            donnees['produits_sous_performants'] = produits_sous_performants
        except:
            pass
        
        try:
            objectif_analyse = tools.comparer_objectif_vs_reel()
            donnees['objectif'] = objectif_analyse
        except:
            pass
        
        try:
            opportunites = tools.identifier_opportunites()
            donnees['opportunites'] = opportunites
        except:
            pass
        
        prompt = f"""
Tu es un conseiller strategique pour une PME africaine. L'utilisateur pose la question suivante:
"{requete}"

Voici les donnees disponibles sur son entreprise:
{json.dumps(donnees, ensure_ascii=False, indent=2, default=str)}

Objectif de l'entreprise (defini lors de l'onboarding):
{json.dumps(state.get('profil_entreprise', {}), ensure_ascii=False, indent=2, default=str)}

STRUCTURE TA REPONSE OBLIGATOIREMENT COMME SUIT:

1. IDENTIFICATION DES OPPORTUNITES
   - Liste 2-3 opportunites concretes basees sur les donnees reelles
   - Cite des chiffres precis

2. RECOMMANDATIONS PRIORITAIRES
   - 2-3 actions concretes a mettre en oeuvre
   - Chaque action doit etre reliee a l'objectif de l'entreprise
   - Indique la priorite (HAUTE, MOYENNE, BASSE)
   - Indique l'impact attendu en chiffres

3. PLAN D'ACTION
   - Etape 1: Action immediate (semaine 1)
   - Etape 2: Action a moyen terme (mois 1-3)
   - Etape 3: Action a long terme (3-6 mois)

REGLES:
- Utilise UNIQUEMENT les chiffres reels des donnees fournies
- Ne cite JAMAIS de chiffres inventes
- Relie chaque recommandation a l'objectif de l'entreprise
- Structure claire avec des titres et des puces
- Reponse en francais, professionnelle et operationnelle
- Longueur: 300-500 mots

RECOMMANDATIONS STRATEGIQUES:
"""
        
        recommandations = LLM.generate_decision(prompt, donnees)
        
        if utilisateur_id and ('HAUTE' in recommandations or 'URGENT' in recommandations):
            try:
                from notifications.tasks import notifier_recommandation_prioritaire
                lignes = recommandations.split('\n')
                premier_prioritaire = ""
                for ligne in lignes:
                    if 'HAUTE' in ligne or 'URGENT' in ligne:
                        premier_prioritaire = ligne
                        break
                
                if premier_prioritaire:
                    notifier_recommandation_prioritaire.delay(
                        utilisateur_id=utilisateur_id,
                        recommandation=premier_prioritaire,
                        donnees={'contexte': donnees}
                    )
                    print(f"[Agent Decision] Notification envoyee pour recommandation prioritaire")
            except Exception as notif_error:
                print(f"[Agent Decision] Erreur notification: {notif_error}")
        
        temps = round(time.time() - debut, 2)
        
        print(f"[Agent Decision] Termine en {temps}s")
        
        return {
            'resultat_decision': recommandations,
            'temps_execution': temps
        }
        
    except Exception as e:
        print(f"[Agent Decision] Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'resultat_decision': f"Erreur lors de la generation des recommandations: {str(e)}",
            'erreur': str(e)
        }


def router_superviseur(state: AgentState) -> str:
    """
    Routeur du superviseur : dirige vers le bon agent.
    Priorite : Communication (publications) > Decision > CRM > Ventes
    """
    agent = state.get('agent_selectionne', 'decision')
    requete = state.get('requete', '').lower()
    
    print(f"[Routeur] Direction vers l'agent: {agent}")
    print(f"[Routeur] Requete: {requete}")
    
    # ============================================
    # 1. PRIORITE MAXIMALE : COMMUNICATION (PUBLICATIONS)
    # ============================================
    communication_keywords = [
        'publie', 'publication', 'post', 'annonce', 'publier',
        'poster', 'facebook', 'page', 'message', 'relance', 
        'email', 'communication', 'contenu', 'ecrire'
    ]
    for kw in communication_keywords:
        if kw in requete:
            print(f"[Routeur] Communication detectee (mot: {kw}) -> Agent Communication")
            return 'agent_communication'
    
    # ============================================
    # 2. QUESTIONS STRATEGIQUES -> DECISION
    # ============================================
    strategie_keywords = [
        'comment', 'pourquoi', 'conseil', 'strategie', 'recommandation', 
        'ameliorer', 'developper', 'augmenter', 'acquerir', 'attirer',
        'avoir plus', 'comment faire', 'croissance', 'grossir',
        'optimiser', 'performance', 'progression', 'objectif',
        'que dois-je', 'que puis-je', 'solution', 'idee'
    ]
    
    for kw in strategie_keywords:
        if kw in requete:
            print(f"[Routeur] Question strategique detectee (mot: {kw}) -> Agent Decision")
            return 'agent_decision'
    
    # ============================================
    # 3. CRM
    # ============================================
    crm_keywords = ['client', 'rfm', 'segment', 'fideliser', 'prospect', 'relancer', 'contact']
    for kw in crm_keywords:
        if kw in requete:
            print(f"[Routeur] CRM detecte -> Agent CRM")
            return 'agent_crm'
    
    # ============================================
    # 4. VENTES
    # ============================================
    ventes_keywords = ['vente', 'ca', 'chiffre', 'affaire', 'panier', 'facture']
    if agent == 'ventes' or any(kw in requete for kw in ventes_keywords):
        print(f"[Routeur] Ventes detecte -> Agent Ventes")
        return 'agent_ventes'
    
    # ============================================
    # 5. PAR DEFAUT : DECISION
    # ============================================
    print(f"[Routeur] Aucune correspondance specifique -> Agent Decision (par defaut)")
    return 'agent_decision'