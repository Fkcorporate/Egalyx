import re
from markupsafe import escape, Markup

def nl2br(value):
    """Convert newlines to <br> tags, preserving HTML safety."""
    if value is None:
        return ''
    
    # Convertir en chaîne
    text = str(value)
    
    # Échapper le HTML pour la sécurité
    escaped = escape(text)
    
    # Remplacer les retours à la ligne par <br>
    result = escaped.replace('\n', '<br>\n')
    
    # Retourner comme Markup pour éviter le double échappement
    return Markup(result)

def safe_nl2br(value):
    """Convert newlines to <br> tags without escaping HTML (use with caution)."""
    if value is None:
        return ''
    
    text = str(value)
    # Direct replacement, assuming HTML is already safe
    result = text.replace('\n', '<br>\n')
    return Markup(result)

def truncate(text, length=100, end='...'):
    """Tronque le texte à une longueur spécifiée."""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length - len(end)] + end

def format_date(value, format='%d/%m/%Y'):
    """Formate une date."""
    if not value:
        return ''
    return value.strftime(format)

def format_datetime(value, format='%d/%m/%Y %H:%M'):
    """Formate une date et heure."""
    if not value:
        return ''
    return value.strftime(format)

def yes_no(value):
    """Convertit un booléen en Oui/Non."""
    return 'Oui' if value else 'Non'

def join_list(value, separator=', '):
    """Join a list into a string."""
    if not value:
        return ''
    if isinstance(value, list):
        return separator.join(str(item) for item in value)
    return str(value)

def markdown_to_html(text):
    """Convert markdown to HTML (simplified version)."""
    if not text:
        return ''
    
    # Simple markdown conversions
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = text.replace('\n', '<br>\n')
    
    return Markup(text)

# Fonction d'initialisation (optionnelle)
def init_filters(app):
    """Initialise tous les filtres Jinja2."""
    app.jinja_env.filters['nl2br'] = nl2br
    app.jinja_env.filters['safe_nl2br'] = safe_nl2br
    app.jinja_env.filters['truncate'] = truncate
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['yes_no'] = yes_no
    app.jinja_env.filters['join_list'] = join_list
    app.jinja_env.filters['markdown_to_html'] = markdown_to_html
    
    return app
