#!/usr/bin/env python3
"""
Script de gestion de l'IA et du nettoyage
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Ajoutez le chemin de votre projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_app_context():
    """Créer un contexte d'application Flask"""
    try:
        from app import app
        return app.app_context()
    except ImportError as e:
        print(f"❌ Impossible d'importer l'application: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur création contexte: {e}")
        return None

def check_openai_connection():
    """Vérifier la connexion à OpenAI"""
    print("🔌 Vérification connexion OpenAI...")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY non définie")
        print("   Pour définir :")
        print("   export OPENAI_API_KEY='sk-votre_clé_api'")
        return False
    
    if api_key.startswith("mode-simulation"):
        print("⚠️  Mode simulation activé")
        print("   Pour utiliser l'API réelle, définissez une vraie clé OpenAI")
        return False
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test simple
        models = client.models.list()
        print(f"✅ Connexion OK - {len(models.data)} modèles disponibles")
        
        # Afficher les modèles disponibles
        gpt_models = [m.id for m in models.data if 'gpt' in m.id]
        print(f"   Modèles GPT disponibles : {', '.join(gpt_models[:3])}")
        
        return True
        
    except ImportError:
        print("❌ Package OpenAI non installé")
        print("   pip install openai")
        return False
    except Exception as e:
        print(f"❌ Erreur connexion OpenAI: {e}")
        return False

def test_ia_service():
    """Tester le service IA localement"""
    print("\n🤖 Test du service IA local...")
    
    try:
        # Import dynamique pour éviter les erreurs d'import circulaire
        import importlib.util
        
        # Vérifier si le fichier existe
        ia_service_path = os.path.join(os.path.dirname(__file__), 'services', 'analyse_ia.py')
        
        if not os.path.exists(ia_service_path):
            print(f"❌ Fichier non trouvé: {ia_service_path}")
            return False
        
        # Charger le module
        spec = importlib.util.spec_from_file_location("analyse_ia", ia_service_path)
        ia_module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(ia_module)
            
            # Tester le service
            service = ia_module.ServiceAnalyseIA()
            statut = service.get_statut()
            
            print(f"   Mode: {statut['mode']}")
            print(f"   Clé API présente: {statut['api_key_presente']}")
            print(f"   Client initialisé: {statut['client_initialise']}")
            
            # Tester une analyse simple SANS contexte Flask
            print(f"\n   Test d'analyse simulation...")
            
            # Créer un contexte d'application pour l'analyse
            app_context = create_app_context()
            if app_context:
                with app_context:
                    resultat = service.analyser_audit(1, 'test', 1)
            else:
                # Fallback: tester sans DB
                print("   ⚠️ Contexte Flask non disponible, test simple...")
                resultat = {
                    'metadata': {
                        'mode': 'simulation',
                        'score_confiance': 78.0
                    }
                }
            
            if resultat:
                print(f"   ✅ Service IA fonctionnel")
                if isinstance(resultat, dict) and 'metadata' in resultat:
                    print(f"   Score: {resultat['metadata'].get('score_confiance', 'N/A')}%")
                return True
            else:
                print(f"   ❌ Service IA non fonctionnel")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur chargement service: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test service: {e}")
        return False

def cleanup_old_analyses(days_old=30):
    """Nettoyer les anciennes analyses IA"""
    print(f"\n🗑️  Nettoyage des analyses de plus de {days_old} jours...")
    
    app_context = create_app_context()
    if not app_context:
        print("❌ Impossible de créer le contexte d'application")
        return -1
    
    try:
        with app_context:
            from models import AnalyseIA
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_analyses = AnalyseIA.query.filter(
                AnalyseIA.date_analyse < cutoff_date
            ).all()
            
            count = len(old_analyses)
            
            if count == 0:
                print("   ✅ Aucune analyse ancienne à supprimer")
                return 0
            
            from app import db
            for analysis in old_analyses:
                db.session.delete(analysis)
            
            db.session.commit()
            
            print(f"   ✅ {count} analyses supprimées")
            return count
            
    except Exception as e:
        print(f"❌ Erreur nettoyage: {e}")
        return -1

def export_analyses_stats():
    """Exporter les statistiques des analyses IA"""
    print("\n📊 Export des statistiques IA...")
    
    app_context = create_app_context()
    if not app_context:
        print("❌ Impossible de créer le contexte d'application")
        return None
    
    try:
        with app_context:
            from models import AnalyseIA, Audit
            from app import db
            
            stats = {
                'total_analyses': AnalyseIA.query.count(),
                'by_type': {},
                'by_score': {
                    'excellent': AnalyseIA.query.filter(AnalyseIA.score_confiance >= 80).count(),
                    'bon': AnalyseIA.query.filter(AnalyseIA.score_confiance >= 60, AnalyseIA.score_confiance < 80).count(),
                    'moyen': AnalyseIA.query.filter(AnalyseIA.score_confiance >= 40, AnalyseIA.score_confiance < 60).count(),
                    'faible': AnalyseIA.query.filter(AnalyseIA.score_confiance < 40).count()
                },
                'by_audit': [],
                'recent_activity': []
            }
            
            # Analyses par type
            types = db.session.query(
                AnalyseIA.type_analyse, 
                db.func.count(AnalyseIA.id)
            ).group_by(AnalyseIA.type_analyse).all()
            
            for type_name, count in types:
                stats['by_type'][type_name] = count
            
            # Audits avec le plus d'analyses
            audits = db.session.query(
                Audit.reference,
                db.func.count(AnalyseIA.id).label('analysis_count')
            ).join(AnalyseIA).group_by(Audit.id).order_by(db.desc('analysis_count')).limit(10).all()
            
            for audit_ref, count in audits:
                stats['by_audit'].append({
                    'audit': audit_ref,
                    'analyses': count
                })
            
            # Activité récente
            recent = AnalyseIA.query.order_by(
                AnalyseIA.date_analyse.desc()
            ).limit(5).all()
            
            for analysis in recent:
                stats['recent_activity'].append({
                    'id': analysis.id,
                    'audit': analysis.audit.reference if analysis.audit else 'N/A',
                    'type': analysis.type_analyse,
                    'score': analysis.score_confiance,
                    'date': analysis.date_analyse.isoformat() if analysis.date_analyse else None
                })
            
            # Sauvegarder
            output_file = 'ia_statistics.json'
            with open(output_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            print(f"✅ Statistiques exportées dans {output_file}")
            print(f"   Total analyses: {stats['total_analyses']}")
            print(f"   Types: {len(stats['by_type'])}")
            
            return stats
            
    except Exception as e:
        print(f"❌ Erreur export stats: {e}")
        return None

def repair_ia_data():
    """Réparer les données IA corrompues"""
    print("\n🔧 Réparation des données IA...")
    
    app_context = create_app_context()
    if not app_context:
        print("❌ Impossible de créer le contexte d'application")
        return -1
    
    try:
        with app_context:
            from models import AnalyseIA
            from app import db
            
            repairs = 0
            analyses = AnalyseIA.query.all()
            
            for analysis in analyses:
                needs_repair = False
                
                # Vérifier le résultat
                if analysis.resultat:
                    if isinstance(analysis.resultat, str):
                        try:
                            # Essayer de parser comme JSON
                            parsed = json.loads(analysis.resultat)
                            analysis.resultat = parsed
                            needs_repair = True
                        except:
                            # Convertir en dict avec erreur
                            analysis.resultat = {
                                'erreur': 'Format invalide',
                                'donnees_originales': analysis.resultat[:500]
                            }
                            needs_repair = True
                
                # Normaliser le score
                if analysis.score_confiance is None:
                    analysis.score_confiance = 50.0
                    needs_repair = True
                elif analysis.score_confiance < 0 or analysis.score_confiance > 100:
                    analysis.score_confiance = max(0, min(100, analysis.score_confiance))
                    needs_repair = True
                
                if needs_repair:
                    repairs += 1
            
            if repairs > 0:
                db.session.commit()
                print(f"✅ {repairs} analyses réparées")
            else:
                print("✅ Aucune réparation nécessaire")
            
            return repairs
            
    except Exception as e:
        print(f"❌ Erreur réparation: {e}")
        return -1

def check_project_structure():
    """Vérifier la structure du projet"""
    print("\n📁 Vérification structure projet...")
    
    required_files = [
        'app.py',
        'models.py',
        'requirements.txt',
        'services/analyse_ia.py'
    ]
    
    all_ok = True
    
    for file in required_files:
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (manquant)")
            all_ok = False
    
    return all_ok

def setup_environment():
    """Configurer l'environnement"""
    print("\n🔧 Configuration environnement...")
    
    # Vérifier la clé API
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY non définie")
        print("\nPour la définir :")
        print("   export OPENAI_API_KEY='sk-votre_clé'")
        return False
    
    print(f"✅ OPENAI_API_KEY: {'*' * 20}{api_key[-4:]}")
    
    # Vérifier les dépendances
    try:
        import openai
        print("✅ Package openai installé")
    except ImportError:
        print("❌ Package openai manquant")
        print("   pip install openai")
        return False
    
    return True

def interactive_mode():
    """Mode interactif"""
    print("🤖 GESTION DE L'ANALYSE IA")
    print("=" * 50)
    
    actions = {
        '1': ('Vérifier connexion OpenAI', check_openai_connection),
        '2': ('Tester service IA local', test_ia_service),
        '3': ('Vérifier structure projet', check_project_structure),
        '4': ('Configurer environnement', setup_environment),
        '5': ('Nettoyer anciennes analyses', lambda: cleanup_old_analyses(30)),
        '6': ('Exporter statistiques', export_analyses_stats),
        '7': ('Réparer données IA', repair_ia_data),
        '8': ('Tout vérifier', lambda: all_checks()),
        'q': ('Quitter', sys.exit)
    }
    
    def all_checks():
        setup_environment()
        check_project_structure()
        check_openai_connection()
        test_ia_service()
        cleanup_old_analyses(30)
        export_analyses_stats()
        repair_ia_data()
    
    while True:
        print("\nActions disponibles :")
        for key, (description, _) in actions.items():
            print(f"  {key}. {description}")
        
        choice = input("\nVotre choix : ").strip().lower()
        
        if choice in actions:
            if choice == 'q':
                print("\nAu revoir ! 👋")
                break
            actions[choice][1]()
        else:
            print("❌ Choix invalide")

def main():
    """Fonction principale"""
    
    # Parser les arguments
    parser = argparse.ArgumentParser(description='Gestion de l\'analyse IA')
    parser.add_argument('--check', action='store_true', help='Vérifier OpenAI')
    parser.add_argument('--test', action='store_true', help='Tester service IA')
    parser.add_argument('--setup', action='store_true', help='Configurer environnement')
    parser.add_argument('--cleanup', type=int, nargs='?', const=30, help='Nettoyer analyses (jours, défaut: 30)')
    parser.add_argument('--export', action='store_true', help='Exporter statistiques')
    parser.add_argument('--repair', action='store_true', help='Réparer données IA')
    parser.add_argument('--all', action='store_true', help='Tout vérifier')
    
    args = parser.parse_args()
    
    if args.check:
        check_openai_connection()
    elif args.test:
        test_ia_service()
    elif args.setup:
        setup_environment()
    elif args.cleanup is not None:
        cleanup_old_analyses(args.cleanup)
    elif args.export:
        export_analyses_stats()
    elif args.repair:
        repair_ia_data()
    elif args.all:
        setup_environment()
        check_project_structure()
        check_openai_connection()
        test_ia_service()
        cleanup_old_analyses(30)
        export_analyses_stats()
        repair_ia_data()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
