"""
Tools Django ORM pour les agents, avec isolation multi-tenant
"""
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from crm.models import Client, Interaction
from ventes.models import Vente, LigneVente
from core.models import ProfilEntreprise, Utilisateur
from typing import Dict, Any, List, Optional
import json
import re


class AgentTools:
    """Conteneur pour les tools des agents, scopés par entreprise"""
    
    def __init__(self, entreprise_id: int):
        self.entreprise_id = entreprise_id
    
    # ============ TOOLS CRM ============
    
    def get_top_clients(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère les meilleurs clients de l'entreprise."""
        clients = Client.objects.filter(
            entreprise_id=self.entreprise_id,
            est_actif=True
        ).order_by('-montant_total_achats')[:limit]
        
        return [
            {
                'nom': client.nom,
                'segment': client.segment,
                'score_rfm': client.score_rfm,
                'montant_total_achats': float(client.montant_total_achats),
                'nombre_achats': client.nombre_achats,
                'dernier_achat': client.date_dernier_achat.strftime('%d/%m/%Y') if client.date_dernier_achat else 'N/A',
                'niveau_rfm': client.get_niveau_rfm()
            }
            for client in clients
        ]
    
    def get_clients_a_relancer(self) -> List[Dict[str, Any]]:
        """Récupère les clients à relancer (pas d'achat depuis 90 jours)."""
        date_limite = timezone.now().date() - timedelta(days=90)
        
        clients = Client.objects.filter(
            entreprise_id=self.entreprise_id,
            est_actif=True
        ).filter(
            Q(date_dernier_achat__isnull=True) | Q(date_dernier_achat__lt=date_limite)
        ).order_by('date_dernier_achat')[:10]
        
        return [
            {
                'nom': client.nom,
                'telephone': client.telephone or 'N/A',
                'segment': client.segment,
                'dernier_achat': client.date_dernier_achat.strftime('%d/%m/%Y') if client.date_dernier_achat else 'Jamais',
                'jours_sans_achat': (timezone.now().date() - client.date_dernier_achat).days if client.date_dernier_achat else 'N/A'
            }
            for client in clients
        ]
    
    def get_statistiques_clients(self) -> Dict[str, Any]:
        """Récupère les statistiques globales des clients."""
        clients = Client.objects.filter(entreprise_id=self.entreprise_id)
        
        total_clients = clients.count()
        clients_actifs = clients.filter(est_actif=True).count()
        
        segments = {}
        for segment in dict(Client.SEGMENTS).keys():
            segments[segment] = clients.filter(segment=segment).count()
        
        avg_rfm = clients.aggregate(Avg('score_rfm'))['score_rfm__avg'] or 0
        
        return {
            'total_clients': total_clients,
            'clients_actifs': clients_actifs,
            'taux_activite': round((clients_actifs / total_clients * 100) if total_clients > 0 else 0, 2),
            'segments': segments,
            'rfm_moyen': round(avg_rfm, 2),
            'ca_total_clients': float(clients.aggregate(Sum('montant_total_achats'))['montant_total_achats__sum'] or 0)
        }
    
    # ============ TOOLS VENTES ============
    
    def get_chiffre_affaires(self, periode: str = 'mois') -> Dict[str, Any]:
        """Récupère le chiffre d'affaires pour une période donnée."""
        maintenant = timezone.now()
        
        if periode == 'mois':
            date_debut = maintenant.replace(day=1, hour=0, minute=0, second=0)
        elif periode == 'trimestre':
            mois = (maintenant.month - 1) // 3 * 3 + 1
            date_debut = maintenant.replace(month=mois, day=1, hour=0, minute=0, second=0)
        elif periode == 'annee':
            date_debut = maintenant.replace(month=1, day=1, hour=0, minute=0, second=0)
        else:
            date_debut = None
        
        ventes = Vente.objects.filter(
            entreprise_id=self.entreprise_id,
            statut__in=['VALIDE', 'LIVREE']
        )
        
        if date_debut:
            ventes = ventes.filter(date_vente__gte=date_debut)
        
        total_ventes = ventes.count()
        ca_total = ventes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        top_produits = LigneVente.objects.filter(
            vente__entreprise_id=self.entreprise_id
        ).values('produit').annotate(
            total_quantite=Sum('quantite'),
            total_ca=Sum('total_ligne')
        ).order_by('-total_ca')[:5]
        
        top_produits_list = []
        for item in top_produits:
            top_produits_list.append({
                'produit': item['produit'],
                'total_quantite': int(item['total_quantite'] or 0),
                'total_ca': float(item['total_ca'] or 0)
            })
        
        if date_debut:
            duree = maintenant - date_debut
            date_debut_prec = date_debut - duree
            ca_prec = Vente.objects.filter(
                entreprise_id=self.entreprise_id,
                statut__in=['VALIDE', 'LIVREE'],
                date_vente__gte=date_debut_prec,
                date_vente__lt=date_debut
            ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
            
            if ca_prec > 0:
                evolution = ((float(ca_total) - float(ca_prec)) / float(ca_prec)) * 100
            else:
                evolution = 100 if ca_total > 0 else 0
        else:
            evolution = None
        
        return {
            'periode': periode,
            'ca_total': float(ca_total),
            'nombre_ventes': total_ventes,
            'panier_moyen': float(ca_total / total_ventes) if total_ventes > 0 else 0,
            'top_produits': top_produits_list,
            'evolution': round(evolution, 2) if evolution is not None else None,
            'date_debut': date_debut.strftime('%d/%m/%Y') if date_debut else 'Toutes'
        }
    
    def get_previsions_ventes(self) -> Dict[str, Any]:
        """Génère des prévisions de ventes basées sur l'historique."""
        maintenant = timezone.now()
        date_limite = maintenant - timedelta(days=90)
        
        ventes_3mois = Vente.objects.filter(
            entreprise_id=self.entreprise_id,
            statut__in=['VALIDE', 'LIVREE'],
            date_vente__gte=date_limite
        )
        
        ca_3mois = ventes_3mois.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        nb_ventes_3mois = ventes_3mois.count()
        
        ca_mensuel_moyen = ca_3mois / 3
        ca_journalier_moyen = ca_3mois / 90
        
        projection_30j = ca_journalier_moyen * 30
        
        return {
            'ca_mensuel_moyen': float(ca_mensuel_moyen),
            'ca_journalier_moyen': float(ca_journalier_moyen),
            'projection_30_jours': float(projection_30j),
            'nombre_ventes_mensuel_moyen': round(nb_ventes_3mois / 3, 2),
            'periode_reference': '3 derniers mois'
        }
    
    def get_performance_ventes(self) -> Dict[str, Any]:
        """Récupère les indicateurs de performance des ventes."""
        maintenant = timezone.now()
        mois_courant = maintenant.replace(day=1, hour=0, minute=0, second=0)
        mois_precedent = (mois_courant - timedelta(days=1)).replace(day=1)
        
        ventes_mois = Vente.objects.filter(
            entreprise_id=self.entreprise_id,
            date_vente__gte=mois_courant
        )
        ventes_mois_prec = Vente.objects.filter(
            entreprise_id=self.entreprise_id,
            date_vente__gte=mois_precedent,
            date_vente__lt=mois_courant
        )
        
        ca_mois = ventes_mois.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        ca_mois_prec = ventes_mois_prec.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        interactions_mois = Interaction.objects.filter(
            client__entreprise_id=self.entreprise_id,
            date__gte=mois_courant
        ).count()
        
        taux_conversion = (ventes_mois.count() / interactions_mois * 100) if interactions_mois > 0 else 0
        
        ca_mois_float = float(ca_mois)
        ca_mois_prec_float = float(ca_mois_prec)
        
        if ca_mois_prec_float > 0:
            evolution = ((ca_mois_float - ca_mois_prec_float) / ca_mois_prec_float) * 100
        else:
            evolution = 0
        
        return {
            'ca_mois_courant': ca_mois_float,
            'ca_mois_precedent': ca_mois_prec_float,
            'evolution_mensuelle': round(evolution, 2),
            'nombre_ventes_mois': ventes_mois.count(),
            'taux_conversion': round(taux_conversion, 2),
            'objectif_mensuel': round(ca_mois_float * 1.15, 2)
        }
    
    # ============ TOOLS COMMUNICATION ============
    
    def generer_message_relance(self, client_nom: str) -> str:
        """Génère un message de relance personnalisé pour un client."""
        client = Client.objects.filter(
            entreprise_id=self.entreprise_id,
            nom__icontains=client_nom
        ).first()
        
        if not client:
            return f"Client '{client_nom}' non trouve."
        
        profil = ProfilEntreprise.objects.filter(entreprise_id=self.entreprise_id).first()
        derniers_achats = Vente.objects.filter(
            entreprise_id=self.entreprise_id,
            client=client
        ).order_by('-date_vente')[:3]
        
        message = f"""
MESSAGE DE RELANCE PERSONNALISE

A l'attention de : {client.nom}
Entreprise : {client.entreprise.nom if client.entreprise else 'N/A'}

---

Bonjour {client.nom},

Nous sommes ravis de vous compter parmi nos clients fidèles.

"""
        
        if derniers_achats:
            message += f"""
VOTRE HISTORIQUE :
- Dernier achat : {derniers_achats[0].date_vente.strftime('%d/%m/%Y')}
- Montant total : {client.montant_total_achats:,.0f} FCFA
- Nombre d'achats : {client.nombre_achats}
"""
        
        message += """
Nous souhaitons vous remercier pour votre confiance.

Offre speciale :
- 10% de reduction sur votre prochain achat
- Livraison gratuite pour toute commande

Nous restons a votre disposition.

Cordialement,
L'equipe """ + (client.entreprise.nom if client.entreprise else 'notre entreprise')
        
        return message
    
    def envoyer_email(self, destinataire: str, sujet: str, message: str) -> Dict[str, Any]:
        """Simule l'envoi d'un email (connecteur MCP simple)."""
        if not destinataire or '@' not in destinataire:
            return {
                'statut': 'erreur',
                'message': 'Adresse email invalide'
            }
        
        print(f"[MCP] Envoi d'email à {destinataire}")
        print(f"[MCP] Sujet: {sujet}")
        
        from notifications.models import Notification
        try:
            utilisateur = Utilisateur.objects.first()
            if utilisateur:
                Notification.objects.create(
                    utilisateur=utilisateur,
                    type='EMAIL',
                    message=f"Email envoyé à {destinataire}: {sujet}",
                    est_lue=False
                )
        except Exception as e:
            print(f"[MCP] Erreur lors de l'enregistrement: {e}")
        
        return {
            'statut': 'succes',
            'message': f"Email envoyé avec succès à {destinataire}",
            'destinataire': destinataire,
            'sujet': sujet
        }
    
    # ============ NOUVEAUX TOOLS POUR L'AGENT DECISION ============
    
    def analyser_clients_a_fort_potentiel(self) -> Dict[str, Any]:
        """
        Analyse les clients à fort potentiel (RFM élevé) qui n'ont pas acheté récemment.
        """
        date_limite = timezone.now().date() - timedelta(days=60)
        
        clients_potentiels = Client.objects.filter(
            entreprise_id=self.entreprise_id,
            est_actif=True,
            score_rfm__gte=600
        ).filter(
            Q(date_dernier_achat__isnull=True) | Q(date_dernier_achat__lt=date_limite)
        ).order_by('-score_rfm')[:10]
        
        resultats = []
        for client in clients_potentiels:
            resultats.append({
                'nom': client.nom,
                'segment': client.segment,
                'score_rfm': client.score_rfm,
                'niveau_rfm': client.get_niveau_rfm(),
                'dernier_achat': client.date_dernier_achat.strftime('%d/%m/%Y') if client.date_dernier_achat else 'Jamais',
                'montant_total': float(client.montant_total_achats),
                'nombre_achats': client.nombre_achats,
                'jours_sans_achat': (timezone.now().date() - client.date_dernier_achat).days if client.date_dernier_achat else None
            })
        
        return {
            'clients_potentiels': resultats,
            'nombre_clients': len(resultats),
            'message': f"{len(resultats)} clients a fort potentiel identifes"
        }
    
    def analyser_produits_sous_performants(self) -> Dict[str, Any]:
        """
        Analyse les produits dont les ventes baissent sur la période récente.
        """
        maintenant = timezone.now()
        periode_recente = maintenant - timedelta(days=30)
        periode_precedente = maintenant - timedelta(days=60)
        
        ventes_recentes = LigneVente.objects.filter(
            vente__entreprise_id=self.entreprise_id,
            vente__date_vente__gte=periode_recente
        ).values('produit').annotate(
            quantite_recente=Sum('quantite'),
            ca_recent=Sum('total_ligne')
        )
        
        ventes_precedentes = LigneVente.objects.filter(
            vente__entreprise_id=self.entreprise_id,
            vente__date_vente__gte=periode_precedente,
            vente__date_vente__lt=periode_recente
        ).values('produit').annotate(
            quantite_precedente=Sum('quantite'),
            ca_precedent=Sum('total_ligne')
        )
        
        ventes_prec_dict = {}
        for item in ventes_precedentes:
            ventes_prec_dict[item['produit']] = {
                'quantite': int(item['quantite_precedente'] or 0),
                'ca': float(item['ca_precedent'] or 0)
            }
        
        sous_performants = []
        for item in ventes_recentes:
            produit = item['produit']
            quantite_recente = int(item['quantite_recente'] or 0)
            ca_recent = float(item['ca_recent'] or 0)
            
            if produit in ventes_prec_dict:
                prec = ventes_prec_dict[produit]
                evolution_quantite = ((quantite_recente - prec['quantite']) / prec['quantite'] * 100) if prec['quantite'] > 0 else 0
                evolution_ca = ((ca_recent - prec['ca']) / prec['ca'] * 100) if prec['ca'] > 0 else 0
                
                if evolution_quantite < -20 or evolution_ca < -20:
                    sous_performants.append({
                        'produit': produit,
                        'quantite_recente': quantite_recente,
                        'quantite_precedente': prec['quantite'],
                        'evolution_quantite': round(evolution_quantite, 1),
                        'ca_recent': ca_recent,
                        'ca_precedent': prec['ca'],
                        'evolution_ca': round(evolution_ca, 1)
                    })
        
        return {
            'produits_sous_performants': sous_performants,
            'nombre_produits': len(sous_performants),
            'message': f"{len(sous_performants)} produits sous-performants identifies"
        }
    
    def comparer_objectif_vs_reel(self) -> Dict[str, Any]:
        """
        Compare le rythme de vente actuel à l'objectif défini dans ProfilEntreprise.
        """
        try:
            profil = ProfilEntreprise.objects.get(entreprise_id=self.entreprise_id)
        except ProfilEntreprise.DoesNotExist:
            return {
                'objectif_defini': False,
                'message': "Aucun objectif defini dans le profil entreprise"
            }
        
        maintenant = timezone.now()
        date_debut = maintenant - timedelta(days=30)
        
        ca_30j = Vente.objects.filter(
            entreprise_id=self.entreprise_id,
            statut__in=['VALIDE', 'LIVREE'],
            date_vente__gte=date_debut
        ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        ca_annuel_projete = float(ca_30j) * 12
        
        resultat = {
            'objectif_defini': True,
            'ca_30_jours': float(ca_30j),
            'ca_annuel_projete': ca_annuel_projete,
            'objectif_court_terme': profil.objectif_court_terme[:100] if profil.objectif_court_terme else "Non defini",
            'objectif_long_terme': profil.objectif_long_terme[:100] if profil.objectif_long_terme else "Non defini"
        }
        
        import re
        if profil.objectif_court_terme:
            chiffres = re.findall(r'\d+', profil.objectif_court_terme)
            if chiffres:
                resultat['objectif_chiffre'] = int(chiffres[0])
        
        return resultat
    
    def identifier_opportunites(self) -> Dict[str, Any]:
        """
        Combine les analyses précédentes pour identifier 2-3 axes d'action concrets.
        """
        clients_potentiels = self.analyser_clients_a_fort_potentiel()
        produits_sous_performants = self.analyser_produits_sous_performants()
        objectif_analyse = self.comparer_objectif_vs_reel()
        
        opportunites = []
        
        if clients_potentiels['nombre_clients'] > 0:
            opportunites.append({
                'axe': 'RELANCE_CLIENTS_POTENTIELS',
                'titre': 'Relancer vos meilleurs clients inactifs',
                'description': f"{clients_potentiels['nombre_clients']} clients avec un score RFM eleve n'ont pas achete recemment",
                'action': f"Contactez ces clients avec une offre personnalisee: {', '.join([c['nom'] for c in clients_potentiels['clients_potentiels'][:3]])}",
                'impact_potentiel': 'Elevé',
                'priorite': 'HAUTE'
            })
        
        if produits_sous_performants['nombre_produits'] > 0:
            produits = produits_sous_performants['produits_sous_performants']
            opportunites.append({
                'axe': 'PRODUITS_SOUS_PERFORMANTS',
                'titre': 'Revoir la strategie des produits en baisse',
                'description': f"{produits_sous_performants['nombre_produits']} produits montrent une baisse de ventes",
                'action': f"Analysez les causes: {', '.join([p['produit'] for p in produits[:3]])}. Envisagez promotions, communication ou retrait",
                'impact_potentiel': 'Moyen',
                'priorite': 'MOYENNE'
            })
        
        if objectif_analyse.get('objectif_defini'):
            opportunites.append({
                'axe': 'OBJECTIFS_STRATEGIQUES',
                'titre': f"Objectif: {objectif_analyse.get('objectif_court_terme', '')[:60]}",
                'description': f"CA annuel projete: {objectif_analyse.get('ca_annuel_projete', 0):,.0f} FCFA",
                'action': "Alignez vos actions commerciales sur cet objectif. Priorisez les clients et produits a fort potentiel.",
                'impact_potentiel': 'Strategique',
                'priorite': 'HAUTE'
            })
        
        if not opportunites:
            opportunites.append({
                'axe': 'CONSEILS_GENERAUX',
                'titre': 'Optimisation generale',
                'description': "Votre entreprise semble stable. Explorez ces pistes:",
                'action': "1. Diversifiez votre offre\n2. Developpez votre presence en ligne\n3. Fidelisez vos meilleurs clients",
                'impact_potentiel': 'Moyen',
                'priorite': 'MOYENNE'
            })
        
        return {
            'opportunites': opportunites,
            'nombre_opportunites': len(opportunites),
            'message': f"{len(opportunites)} axes d'action identifies"
        }
    
    # ============ TOOLS DECISION ============
    
    def synthetiser_recommandations(self, donnees: Dict[str, Any]) -> str:
        """
        Synthétise les données en recommandations stratégiques.
        """
        recommandations = []
        
        clients_potentiels = self.analyser_clients_a_fort_potentiel()
        if clients_potentiels['nombre_clients'] > 0:
            recommandations.append({
                'categorie': 'CRM',
                'priorite': 'HAUTE',
                'action': f"Relancez vos {clients_potentiels['nombre_clients']} clients a fort potentiel qui n'ont pas achete recemment.",
                'impact': 'Potentiel de +15% de CA sur ces clients'
            })
        
        produits = self.analyser_produits_sous_performants()
        if produits['nombre_produits'] > 0:
            recommandations.append({
                'categorie': 'PRODUITS',
                'priorite': 'MOYENNE',
                'action': f"Analysez la baisse de ventes de {produits['nombre_produits']} produits et envisagez des actions correctives.",
                'impact': 'Potentiel de +10% de CA'
            })
        
        objectif_analyse = self.comparer_objectif_vs_reel()
        if objectif_analyse.get('objectif_defini'):
            ca_projete = objectif_analyse.get('ca_annuel_projete', 0)
            recommandations.append({
                'categorie': 'STRATEGIE',
                'priorite': 'HAUTE',
                'action': f"Votre objectif: {objectif_analyse.get('objectif_court_terme', '')[:60]}... CA annuel projete: {ca_projete:,.0f} FCFA",
                'impact': 'Alignement strategique'
            })
        
        if not recommandations:
            recommandations.append({
                'categorie': 'STRATEGIE',
                'priorite': 'BASSE',
                'action': "Continuez vos efforts. Pensez a diversifier votre offre et a fideliser vos clients.",
                'impact': 'Maintien de la performance'
            })
        
        priorite_order = {'HAUTE': 0, 'MOYENNE': 1, 'BASSE': 2}
        recommandations.sort(key=lambda x: priorite_order.get(x.get('priorite', 'BASSE'), 2))
        
        resultat = "RECOMMANDATIONS STRATEGIQUES\n\n"
        for i, rec in enumerate(recommandations, 1):
            priorite_text = rec['priorite']
            resultat += f"{i}. {priorite_text} - {rec['categorie']}\n"
            resultat += f"   {rec['action']}\n"
            resultat += f"   Impact: {rec['impact']}\n\n"
        
        return resultat
    
    # ============ TOOLS FACEBOOK PUBLICATION ============
    
    def verifier_connexion_facebook(self) -> Dict[str, Any]:
        """
        Verifie si l'entreprise a une connexion Facebook active.
        """
        from communication.models import ConnexionFacebook
        
        try:
            connexion = ConnexionFacebook.objects.get(
                entreprise_id=self.entreprise_id,
                est_active=True
            )
            
            return {
                'connecte': True,
                'page_id': connexion.page_id,
                'page_nom': connexion.page_nom,
                'connexion': connexion
            }
        except ConnexionFacebook.DoesNotExist:
            return {
                'connecte': False,
                'message': 'Aucune page Facebook connectee. Connectez-vous depuis les integrations.',
                'lien': '/communication/integrations/'
            }
    
    def preparer_publication_facebook(self, contenu: str, date_publication: str = None) -> Dict[str, Any]:
        """
        Prepare un brouillon de publication Facebook.
        
        Args:
            contenu: Le texte du post ou une description de ce qu'il doit contenir
            date_publication: Date/heure demandee (ex: "12h00 aujourd'hui", "demain 9h")
        
        Returns:
            Dictionnaire avec le brouillon prepare
        """
        from datetime import datetime, timedelta
        
        # Verifier la connexion
        connexion = self.verifier_connexion_facebook()
        if not connexion['connecte']:
            return {
                'pret': False,
                'erreur': connexion['message'],
                'lien': connexion.get('lien', '/communication/integrations/')
            }
        
        # Utiliser le LLM pour generer le contenu du post si necessaire
        from .llm import get_llm_for_response
        
        # Determiner si le contenu est deja un post complet ou une idee
        contenu_lower = contenu.lower()
        est_une_idee = any(kw in contenu_lower for kw in [
            'publie', 'publication', 'post', 'annonce', 'offre', 'vendre', 'promotion'
        ]) and len(contenu) < 150
        
        if est_une_idee:
            llm = get_llm_for_response()
            prompt = f"""
Tu es un expert en copywriting pour les PME africaines.
L'utilisateur veut publier ceci sur Facebook: "{contenu}"

Genere un post publicitaire professionnel et engageant.
Le post doit:
- Avoir un titre accrocheur
- Etre en francais
- Inclure un appel a l'action
- Faire entre 50 et 100 mots
- Ne pas contenir d'emojis
- Etre adapte au contexte des PME africaines

Post genere:"""
            
            response = llm.invoke(prompt)
            texte_post = response.content.strip()
        else:
            texte_post = contenu
        
        # Parser la date de publication
        date_obj = None
        maintenant = datetime.now()
        
        if date_publication:
            date_publication_lower = date_publication.lower()
            
            if 'aujourd\'hui' in date_publication_lower or "aujourd'hui" in date_publication_lower:
                heures = re.search(r'(\d{1,2})h', date_publication_lower)
                minutes = re.search(r'(\d{1,2})min', date_publication_lower)
                
                heure = int(heures.group(1)) if heures else maintenant.hour + 1
                minute = int(minutes.group(1)) if minutes else 0
                
                date_obj = maintenant.replace(hour=heure, minute=minute, second=0, microsecond=0)
                if date_obj < maintenant:
                    date_obj = date_obj + timedelta(days=1)
                    
            elif 'demain' in date_publication_lower:
                heures = re.search(r'(\d{1,2})h', date_publication_lower)
                heure = int(heures.group(1)) if heures else 9
                
                date_obj = (maintenant + timedelta(days=1)).replace(hour=heure, minute=0, second=0, microsecond=0)
        
        if date_obj and date_obj < datetime.now():
            date_obj = None
        
        return {
            'pret': True,
            'contenu': texte_post,
            'date_publication': date_obj.isoformat() if date_obj else None,
            'date_texte': date_obj.strftime('%d/%m/%Y %H:%M') if date_obj else 'Immediatement',
            'page_id': connexion['page_id'],
            'page_nom': connexion['page_nom'],
            'est_immediat': date_obj is None,
            'action': 'publication_facebook'
        }
    
    def confirmer_publication_facebook(self, contenu: str, date_publication: str = None) -> Dict[str, Any]:
        """
        Confirme et cree la publication Facebook programmee.
        """
        from communication.models import ConnexionFacebook, PublicationProgrammee
        from django.utils import timezone
        from datetime import datetime
        
        connexion = self.verifier_connexion_facebook()
        if not connexion['connecte']:
            return {
                'succes': False,
                'erreur': connexion['message'],
                'lien': connexion.get('lien', '/communication/integrations/')
            }
        
        date_obj = None
        if date_publication:
            try:
                date_obj = datetime.fromisoformat(date_publication.replace('Z', '+00:00'))
            except:
                date_obj = None
        
        publication = PublicationProgrammee.objects.create(
            entreprise_id=self.entreprise_id,
            page_id=connexion['page_id'],
            page_nom=connexion['page_nom'],
            contenu_texte=contenu,
            date_publication=date_obj,
            statut='EN_ATTENTE'
        )
        
        if not date_obj or date_obj <= timezone.now():
            return self.publier_maintenant(publication.id)
        
        return {
            'succes': True,
            'message': f"Publication programmee pour le {date_obj.strftime('%d/%m/%Y')} a {date_obj.strftime('%H:%M')}",
            'publication_id': publication.id,
            'statut': 'programmee'
        }
    
    def publier_maintenant(self, publication_id: int) -> Dict[str, Any]:
        """
        Publie immediatement une publication sur Facebook.
        """
        from communication.models import ConnexionFacebook, PublicationProgrammee
        from django.utils import timezone
        import requests
        
        try:
            publication = PublicationProgrammee.objects.get(id=publication_id, entreprise_id=self.entreprise_id)
        except PublicationProgrammee.DoesNotExist:
            return {'succes': False, 'erreur': 'Publication non trouvee'}
        
        connexion = self.verifier_connexion_facebook()
        if not connexion['connecte']:
            publication.statut = 'ECHEC'
            publication.message_erreur = connexion['message']
            publication.save()
            return {'succes': False, 'erreur': connexion['message']}
        
        url = f"https://graph.facebook.com/v19.0/{connexion['page_id']}/feed"
        params = {
            'message': publication.contenu_texte,
            'access_token': connexion['connexion'].access_token
        }
        
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            data = response.json()
            
            publication.statut = 'PUBLIEE'
            publication.date_publication_reelle = timezone.now()
            publication.publication_id_facebook = data.get('id')
            publication.save()
            
            return {
                'succes': True,
                'message': "Publication publiee avec succes sur Facebook !",
                'post_id': data.get('id'),
                'url': f"https://www.facebook.com/{data.get('id')}"
            }
        except requests.RequestException as e:
            publication.statut = 'ECHEC'
            publication.message_erreur = str(e)
            publication.save()
            
            return {
                'succes': False,
                'erreur': f"Erreur lors de la publication: {str(e)}"
            }