#!/usr/bin/env python3
"""
Script pour exécuter les outils IA dans le contexte Flask
"""

import os
import sys

# Ajoutez le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Point d'entrée principal"""
    
    # Charger l'application Flask
    try:
        from app import app
        
        # Exécuter dans le contexte de l'application
        with app.app_context():
            # Importez et exécutez manage_ia depuis ici
            from manage_ia import main as ia_main
            
            # Parser les arguments
            import argparse
            parser = argparse.ArgumentParser(description='Gestion de l\'analyse IA')
            parser.add_argument('--check', action='store_true', help='Vérifier OpenAI')
            parser.add_argument('--test', action='store_true', help='Tester service IA')
            parser.add_argument('--setup', action='store_true', help='Configurer environnement')
            parser.add_argument('--cleanup', type=int, nargs='?', const=30, help='Nettoyer analyses')
            parser.add_argument('--export', action='store_true', help='Exporter statistiques')
            parser.add_argument('--repair', action='store_true', help='Réparer données IA')
            parser.add_argument('--all', action='store_true', help='Tout vérifier')
            
            args = parser.parse_args()
            
            if args.check:
                from manage_ia import check_openai_connection
                check_openai_connection()
            elif args.test:
                from manage_ia import test_ia_service
                test_ia_service()
            elif args.setup:
                from manage_ia import setup_environment
                setup_environment()
            elif args.cleanup is not None:
                from manage_ia import cleanup_old_analyses
                cleanup_old_analyses(args.cleanup)
            elif args.export:
                from manage_ia import export_analyses_stats
                export_analyses_stats()
            elif args.repair:
                from manage_ia import repair_ia_data
                repair_ia_data()
            elif args.all:
                from manage_ia import setup_environment, check_project_structure, check_openai_connection, test_ia_service, cleanup_old_analyses, export_analyses_stats, repair_ia_data
                setup_environment()
                check_project_structure()
                check_openai_connection()
                test_ia_service()
                cleanup_old_analyses(30)
                export_analyses_stats()
                repair_ia_data()
            else:
                # Mode interactif
                from manage_ia import interactive_mode
                interactive_mode()
                
    except ImportError as e:
        print(f"❌ Impossible d'importer l'application Flask: {e}")
        print("Assurez-vous d'être dans le bon répertoire")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()