#!/usr/bin/env python3
# Script pour extraire TOUS les textes de TOUS les templates

import os
import re
import csv
from collections import defaultdict, OrderedDict

def extract_text_from_html(html_content):
    """Extrait tous les textes d'un contenu HTML (hors code Jinja/JS)"""
    texts = []
    
    # 1. Textes entre balises (sans balises enfants)
    # Ex: <span>Texte à extraire</span>
    tag_pattern = r'>\s*([^<>{}\n]+?)\s*<'
    for match in re.finditer(tag_pattern, html_content):
        text = match.group(1).strip()
        if text and len(text) > 1:
            texts.append(text)
    
    # 2. Textes dans les attributs
    # Ex: placeholder="Texte", title="Texte", alt="Texte"
    attr_patterns = [
        r'placeholder=["\']([^"\']+)["\']',
        r'title=["\']([^"\']+)["\']',
        r'alt=["\']([^"\']+)["\']',
        r'label=["\']([^"\']+)["\']',
        r'aria-label=["\']([^"\']+)["\']',
    ]
    
    for pattern in attr_patterns:
        for match in re.finditer(pattern, html_content):
            text = match.group(1).strip()
            if text and len(text) > 1:
                texts.append(text)
    
    # 3. Textes dans les boutons, liens, etc.
    # Ex: <button>Texte</button>, <a href="#">Texte</a>
    element_patterns = [
        r'<button[^>]*>([^<]+)</button>',
        r'<a [^>]*>([^<]+)</a>',
        r'<label[^>]*>([^<]+)</label>',
        r'<option[^>]*>([^<]+)</option>',
        r'<th[^>]*>([^<]+)</th>',
        r'<td[^>]*>([^<]+)</td>',
        r'<li[^>]*>([^<]+)</li>',
        r'<span[^>]*>([^<]+)</span>',
        r'<div[^>]*>([^<]+)</div>',
        r'<p[^>]*>([^<]+)</p>',
        r'<h1[^>]*>([^<]+)</h1>',
        r'<h2[^>]*>([^<]+)</h2>',
        r'<h3[^>]*>([^<]+)</h3>',
        r'<h4[^>]*>([^<]+)</h4>',
        r'<h5[^>]*>([^<]+)</h5>',
        r'<h6[^>]*>([^<]+)</h6>',
    ]
    
    for pattern in element_patterns:
        for match in re.finditer(pattern, html_content):
            text = match.group(1).strip()
            if text and len(text) > 1:
                texts.append(text)
    
    # Nettoyer les textes
    cleaned_texts = []
    for text in texts:
        # Ignorer les codes Jinja, variables, nombres seuls, URLs
        if not any(char in text for char in ['{', '}', '%', '$', '@']):
            if not text.isdigit():
                if not text.startswith('http'):
                    if len(text) > 1 and text not in cleaned_texts:
                        cleaned_texts.append(text)
    
    return cleaned_texts

def extract_from_all_templates():
    """Extrait les textes de tous les templates"""
    all_texts = defaultdict(list)  # template -> [textes]
    unique_texts = OrderedDict()   # texte -> occurrences
    
    templates_dir = 'templates'
    
    if not os.path.exists(templates_dir):
        print(f"❌ Dossier {templates_dir} non trouvé")
        return all_texts, unique_texts
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, templates_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extraire les textes
                    texts = extract_text_from_html(content)
                    
                    if texts:
                        all_texts[relative_path] = texts
                        
                        # Compter les occurrences
                        for text in texts:
                            if text in unique_texts:
                                unique_texts[text]['count'] += 1
                                unique_texts[text]['templates'].append(relative_path)
                            else:
                                unique_texts[text] = {
                                    'count': 1,
                                    'templates': [relative_path],
                                    'translated': False
                                }
                        
                        print(f"✅ {relative_path}: {len(texts)} textes extraits")
                    else:
                        print(f"⚠️  {relative_path}: aucun texte extrait")
                        
                except Exception as e:
                    print(f"❌ Erreur {relative_path}: {e}")
    
    return all_texts, unique_texts

def generate_csv(unique_texts, csv_path='translations/to_translate.csv'):
    """Génère/MAJ le CSV avec les nouveaux textes"""
    
    # Charger les traductions existantes
    existing_translations = {}
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        french = row[0].strip()
                        english = row[1].strip()
                        if french and english:
                            existing_translations[french] = english
            print(f"📖 {len(existing_translations)} traductions existantes chargées")
        except Exception as e:
            print(f"⚠️  Erreur chargement CSV: {e}")
    
    # Préparer les nouvelles entrées
    new_entries = []
    updated_count = 0
    
    for french_text, info in unique_texts.items():
        if french_text not in existing_translations:
            # Nouveau texte à traduire
            new_entries.append([french_text, ''])  # Anglais vide
            updated_count += 1
            print(f"➕ Nouveau: {french_text[:50]}...")
    
    # Ajouter au CSV
    if new_entries:
        mode = 'a' if os.path.exists(csv_path) else 'w'
        with open(csv_path, mode, encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(new_entries)
        
        print(f"\n📊 STATISTIQUES:")
        print(f"   Textes uniques: {len(unique_texts)}")
        print(f"   Traductions existantes: {len(existing_translations)}")
        print(f"   Nouvelles entrées ajoutées: {updated_count}")
        print(f"   Total après mise à jour: {len(existing_translations) + updated_count}")
    else:
        print("✅ Aucun nouveau texte à ajouter")
    
    return existing_translations

def main():
    print("=" * 60)
    print("🔍 EXTRACTION DE TOUS LES TEXTES DES TEMPLATES")
    print("=" * 60)
    
    # 1. Extraire
    all_texts, unique_texts = extract_from_all_templates()
    
    print(f"\n📋 RÉSULTATS GLOBAUX:")
    print(f"   Templates analysés: {len(all_texts)}")
    print(f"   Textes uniques trouvés: {len(unique_texts)}")
    
    # 2. Générer/MAJ CSV
    csv_path = 'translations/to_translate.csv'
    existing_translations = generate_csv(unique_texts, csv_path)
    
    # 3. Générer un rapport
    generate_report(all_texts, unique_texts, existing_translations)
    
    print("\n✅ EXTRACTION TERMINÉE !")
    print("\n📝 PROCHAINES ÉTAPES:")
    print("1. Traduisez les textes anglais vides dans le CSV")
    print("2. Lancez le script de mise à jour des templates")
    print("3. Testez la traduction")

def generate_report(all_texts, unique_texts, existing_translations):
    """Génère un rapport détaillé"""
    report_path = 'translation_report.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("📊 RAPPORT D'EXTRACTION DES TRADUCTIONS\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("📈 STATISTIQUES GLOBALES:\n")
        f.write(f"- Templates analysés: {len(all_texts)}\n")
        f.write(f"- Textes uniques: {len(unique_texts)}\n")
        f.write(f"- Déjà traduits: {len([t for t in unique_texts if t in existing_translations])}\n")
        f.write(f"- À traduire: {len([t for t in unique_texts if t not in existing_translations])}\n\n")
        
        f.write("📁 TEMPLATES PAR NOMBRE DE TEXTES:\n")
        for template, texts in sorted(all_texts.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"- {template}: {len(texts)} textes\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("📋 LISTE COMPLÈTE DES TEXTES À TRADUIRE:\n")
        f.write("=" * 60 + "\n\n")
        
        # Textes non traduits
        untranslated = [t for t in unique_texts if t not in existing_translations]
        if untranslated:
            f.write("❌ NON TRADUITS:\n")
            for i, text in enumerate(untranslated, 1):
                f.write(f"{i:3d}. {text}\n")
                f.write(f"     Templates: {', '.join(unique_texts[text]['templates'][:3])}")
                if len(unique_texts[text]['templates']) > 3:
                    f.write(f"... (+{len(unique_texts[text]['templates']) - 3} autres)")
                f.write("\n")
        else:
            f.write("✅ Tous les textes sont déjà dans le CSV !\n")
    
    print(f"\n📄 Rapport généré: {report_path}")

if __name__ == '__main__':
    main()