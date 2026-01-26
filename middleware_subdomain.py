# middleware_subdomain.py
from flask import request, g, redirect, url_for
import re

@app.before_request
def detect_client_subdomain():
    """Détecte le sous-domaine et route vers le client correspondant"""
    host = request.host
    
    # En production, extraire le sous-domaine
    if 'votresociete.com' in host:
        subdomain = host.replace('.votresociete.com', '')
        
        # Si c'est un sous-domaine client (pas www, pas api)
        if subdomain and subdomain not in ['www', 'api', 'admin']:
            # Trouver le client par sous-domaine
            client = Client.query.filter_by(sous_domaine=f"{subdomain}.votresociete.com").first()
            if client:
                g.client_id = client.id
                g.client_subdomain = subdomain
                
                # Si l'utilisateur n'est pas connecté, rediriger vers login client
                if not current_user.is_authenticated and request.endpoint != 'client_login':
                    return redirect(url_for('client_login', client_reference=client.reference))

# Route pour login avec sous-domaine
@app.route('/client-login', methods=['GET', 'POST'])
def client_login_subdomain():
    """Login automatique par sous-domaine"""
    if hasattr(g, 'client_subdomain'):
        client = Client.query.filter(
            Client.sous_domaine.like(f"%{g.client_subdomain}%")
        ).first()
        
        if client:
            # Rediriger vers la page de login spécifique
            return redirect(url_for('client_login_page', client_reference=client.reference))
    
    return redirect(url_for('public_home'))