import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class MultiTenantManager:
    """Gère les connexions multi-tenant"""
    
    def __init__(self):
        self.connections = {}
        self.base_engine = create_engine(os.environ.get('DATABASE_URL'))
    
    def get_engine_for_client(self, client_id):
        """Retourne le moteur de base de données pour un client"""
        if client_id not in self.connections:
            # Dans un setup réel, vous récupéreriez les infos de connexion de la base client
            # Pour l'exemple, on utilise la même base mais avec un schéma différent
            engine = create_engine(
                os.environ.get('DATABASE_URL'),
                connect_args={'options': f'-c search_path=client_{client_id},public'}
            )
            self.connections[client_id] = engine
        return self.connections[client_id]
    
    def get_session_for_client(self, client_id):
        """Retourne une session pour un client"""
        engine = self.get_engine_for_client(client_id)
        Session = sessionmaker(bind=engine)
        return Session()

# Singleton
tenant_manager = MultiTenantManager()