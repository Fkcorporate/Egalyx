# Créer un fichier translation_manager.py
import json
import os

class TranslationManager:
    """Gestionnaire de traductions intelligentes"""
    
    def __init__(self, app):
        self.app = app
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Charge les traductions depuis des fichiers JSON"""
        translations_dir = os.path.join(app.root_path, 'translations')
        
        for lang in LANGUAGES.keys():
            file_path = os.path.join(translations_dir, f'{lang}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            else:
                self.translations[lang] = {}
    
    def translate(self, key, lang=None, default=None):
        """Traduit une clé dans la langue spécifiée"""
        if not key:
            return default or key
        
        target_lang = lang or get_locale()
        
        # Chercher la traduction
        translation = self.translations.get(target_lang, {}).get(key)
        
        if translation:
            return translation
        
        # Si pas de traduction, retourner la clé (pour l'anglais) ou la valeur par défaut
        if target_lang == 'en':
            return key
        
        return default or key
    
    def get_navigation_translations(self, lang=None):
        """Retourne les traductions pour la navigation"""
        nav_keys = [
            'Dashboard', 'Risk Management', 'Audit', 'Settings', 
            'Users', 'Logout', 'Quick Actions', 'Configuration',
            'Notifications', 'Client View', 'Profile'
        ]
        
        target_lang = lang or get_locale()
        return {key: self.translate(key, target_lang, key) for key in nav_keys}

# Initialiser le gestionnaire
translation_manager = TranslationManager(app)

# Injecter dans les templates
@app.context_processor
def inject_translations():
    """Injecte les traductions dans les templates"""
    current_lang = get_locale()
    
    return {
        't': translation_manager.translate,
        'nav_translations': translation_manager.get_navigation_translations(current_lang),
        'lang': current_lang
    }