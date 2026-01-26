# forms_admin.py - VERSION CORRIGÉE
from datetime import datetime 
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, BooleanField, 
    SubmitField, TextAreaField, IntegerField, DecimalField,
    DateField, DateTimeField  
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional,
    NumberRange, ValidationError, URL, Regexp
)

# Dans forms_admin.py (ou là où est votre NouvelUtilisateurForm)
class NouvelUtilisateurForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(message='Le nom d\'utilisateur est requis')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Format d\'email invalide')
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit avoir au moins 6 caractères')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='Veuillez confirmer le mot de passe'),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    
    role = SelectField('Rôle', choices=[
        ('utilisateur', 'Utilisateur Standard'),
        ('auditeur', 'Auditeur'),
        ('compliance', 'Responsable Conformité'),
        ('manager', 'Manager'),
        ('consultant', 'Consultant')
    ], default='utilisateur')
    
    department = StringField('Département')
    is_active = BooleanField('Actif', default=True)
    template_permissions = SelectField('Template de permissions', coerce=int)
    submit = SubmitField('Créer l\'utilisateur')
    
    def __init__(self, *args, **kwargs):
        super(NouvelUtilisateurForm, self).__init__(*args, **kwargs)
        # Initialiser les choix dynamiquement
        self.template_permissions.choices = [(0, 'Aucun template')]


class EditerUtilisateurForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    
    role = SelectField('Rôle', choices=[
        ('utilisateur', 'Utilisateur'),
        ('auditeur', 'Auditeur'),
        ('compliance', 'Responsable Conformité'),
        ('manager', 'Manager'),
        ('admin', 'Administrateur'),
        ('super_admin', 'Super Administrateur'),
        ('consultant', 'Consultant')
    ], default='utilisateur')
    
    # AJOUTER CE CHAMP
    client_id = SelectField('Client', coerce=int, choices=[])
    
    department = StringField('Département', validators=[Optional(), Length(max=100)])
    is_active = BooleanField('Actif', default=True)
    
    password = PasswordField('Nouveau mot de passe (laisser vide pour ne pas changer)', 
                           validators=[Optional()])
    
    confirm_password = PasswordField('Confirmer le mot de passe', 
                                   validators=[Optional()])
    
    # Template de permissions - INITIALISER AVEC UNE LISTE VIDE
    template_permissions = SelectField('Template de permissions', 
                                     coerce=int, 
                                     choices=[],  # IMPORTANT : liste vide initiale
                                     validators=[Optional()])
    
    submit = SubmitField('Mettre à jour')
    
    def validate(self, extra_validators=None):
        initial_validation = super(EditerUtilisateurForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        
        if self.password.data and self.password.data != self.confirm_password.data:
            self.confirm_password.errors.append('Les mots de passe ne correspondent pas')
            return False
        
        return True


class PermissionTemplateForm(FlaskForm):
    name = StringField('Nom du template', validators=[DataRequired()])
    description = TextAreaField('Description')
    role = SelectField('Rôle associé', choices=[
        ('utilisateur', 'Utilisateur'),
        ('auditeur', 'Auditeur'),
        ('manager', 'Manager'),
        ('admin', 'Administrateur'),
        ('compliance', 'Conformité'),
        ('consultant', 'Consultant'),
        ('super_admin', 'Super Administrateur')
    ], default='utilisateur')
    
    # Permissions de base
    can_view_dashboard = BooleanField('Voir le tableau de bord', default=True)
    can_view_reports = BooleanField('Consulter les rapports', default=True)
    can_export_data = BooleanField('Exporter des données', default=False)
    
    # Gestion des données
    can_manage_risks = BooleanField('Gérer les risques', default=False)
    can_manage_kri = BooleanField('Gérer les KRI', default=False)
    can_manage_audit = BooleanField('Gérer les audits', default=False)
    can_manage_regulatory = BooleanField('Gérer la veille règlementaire', default=False)
    can_manage_logigram = BooleanField('Gérer les logigrammes', default=False)
    
    # Administration
    can_manage_users = BooleanField('Gérer les utilisateurs', default=False)
    can_manage_settings = BooleanField('Gérer les paramètres', default=False)
    can_manage_permissions = BooleanField('Gérer les permissions', default=False)
    
    # Permissions avancées
    can_delete_data = BooleanField('Supprimer des données', default=False)
    can_archive_data = BooleanField('Archiver des données', default=False)
    can_validate_risks = BooleanField('Valider les risques', default=False)
    can_confirm_evaluations = BooleanField('Confirmer les évaluations', default=False)
    
    # NOUVELLES PERMISSIONS
    can_view_departments = BooleanField('Voir directions/services', default=False)
    can_manage_departments = BooleanField('Gérer directions/services', default=False)
    can_view_users_list = BooleanField('Voir liste des utilisateurs', default=False)
    can_edit_users = BooleanField('Modifier les utilisateurs', default=False)
    can_access_all_departments = BooleanField('Accès à tous les départements', default=False)
    can_manage_clients = BooleanField('Gérer les clients', default=False)
    can_provision_servers = BooleanField('Provisionner des serveurs', default=False)
    
    submit = SubmitField('Enregistrer')


class NouveauClientForm(FlaskForm):
    nom = StringField('Nom du client', validators=[DataRequired()])
    reference = StringField('Référence client', validators=[DataRequired()])
    description = TextAreaField('Description')
    
    contact_nom = StringField('Nom du contact')
    contact_email = StringField('Email du contact', validators=[Email()])
    contact_telephone = StringField('Téléphone du contact')
    
    domaine = StringField('Domaine personnalisé (optionnel)')
    plan = SelectField('Plan', choices=[
        ('standard', 'Standard (10 utilisateurs)'),
        ('premium', 'Premium (50 utilisateurs)'),
        ('enterprise', 'Enterprise (Illimité)')
    ], default='standard')
    
    max_utilisateurs = IntegerField('Limite utilisateurs', default=10)
    max_risques = IntegerField('Limite risques', default=1000)
    max_audits = IntegerField('Limite audits', default=100)
    
    provisionner_serveur = BooleanField('Provisionner un serveur dédié', default=False)
    environnement_nom = StringField('Nom de l\'environnement')
    sous_domaine = StringField('Sous-domaine (ex: client1.mondomaine.com)')
    
    submit = SubmitField('Créer le client')


class EnvironnementClientForm(FlaskForm):
    nom = StringField('Nom de l\'environnement', validators=[DataRequired()])
    sous_domaine = StringField('Sous-domaine')
    
    server_ip = StringField('Adresse IP du serveur')
    server_port = IntegerField('Port SSH', default=22)
    server_ssh_user = StringField('Utilisateur SSH')
    
    cpu_alloue = StringField('CPU alloué', default='1 core')
    ram_alloue = StringField('RAM allouée', default='1GB')
    stockage_alloue = StringField('Stockage alloué', default='10GB')
    
    submit = SubmitField('Mettre à jour')


# Ajouter ces formulaires dans forms_admin.py

class FormuleAbonnementForm(FlaskForm):
    """Formulaire pour créer/modifier une formule"""
    nom = StringField('Nom de la formule', validators=[DataRequired()])
    code = StringField('Code (unique)', validators=[DataRequired()])
    description = TextAreaField('Description')
    
    # Prix
    prix_mensuel = DecimalField('Prix mensuel (€)', places=2, validators=[Optional()])
    prix_annuel = DecimalField('Prix annuel (€)', places=2, validators=[Optional()])
    
    # Limites
    max_utilisateurs = IntegerField('Max utilisateurs', default=10, validators=[DataRequired()])
    max_risques = IntegerField('Max risques', default=1000, validators=[DataRequired()])
    max_audits = IntegerField('Max audits', default=100, validators=[DataRequired()])
    max_processus = IntegerField('Max processus', default=50, validators=[Optional()])
    max_logigrammes = IntegerField('Max logigrammes', default=20, validators=[Optional()])
    
    # Stockage (en Mo)
    stockage_upload = IntegerField('Stockage uploads (Mo)', default=1024)
    stockage_documents = IntegerField('Stockage documents (Mo)', default=512)
    
    # Statut
    is_active = BooleanField('Active', default=True)
    is_public = BooleanField('Visible publiquement', default=True)
    ordre_affichage = IntegerField('Ordre d\'affichage', default=0)
    
    submit = SubmitField('Enregistrer')


class FeaturesForm(FlaskForm):
    """Formulaire pour configurer les features d'une formule"""
    # Features booléennes
    risques = BooleanField('Gestion des risques', default=True)
    kri = BooleanField('Indicateurs KRI', default=True)
    audit = BooleanField('Audit interne', default=True)
    veille_reglementaire = BooleanField('Veille règlementaire', default=False)
    logigrammes = BooleanField('Logigrammes/Processus', default=False)
    ia_analyse = BooleanField('Analyse IA', default=False)
    reports_avances = BooleanField('Rapports avancés', default=False)
    multi_sites = BooleanField('Multi-sites', default=False)
    api_avancee = BooleanField('API avancée', default=False)
    sauvegardes_auto = BooleanField('Sauvegardes automatiques', default=False)
    support_prioritaire = BooleanField('Support prioritaire', default=False)
    custom_domain = BooleanField('Domaine personnalisé', default=False)
    sso = BooleanField('SSO (Single Sign-On)', default=False)
    
    submit = SubmitField('Mettre à jour les features')


class ModulesForm(FlaskForm):
    """Formulaire pour configurer les modules d'une formule"""
    # Modules accessibles
    cartographie = BooleanField('Cartographie des risques', default=True)
    matrices_risque = BooleanField('Matrices de risque', default=True)
    suivi_kri = BooleanField('Suivi KRI', default=True)
    audit_interne = BooleanField('Audit interne', default=True)
    plans_action = BooleanField('Plans d\'action', default=True)
    veille = BooleanField('Veille règlementaire', default=False)
    processus = BooleanField('Gestion des processus', default=False)
    organigramme = BooleanField('Organigramme', default=False)
    questionnaires = BooleanField('Questionnaires', default=False)
    portail_fournisseurs = BooleanField('Portail fournisseurs', default=False)
    reporting_avance = BooleanField('Reporting avancé', default=False)
    tableaux_bord_personnalisables = BooleanField('Tableaux de bord personnalisables', default=False)
    
    submit = SubmitField('Mettre à jour les modules')


class RolesForm(FlaskForm):
    """Formulaire pour configurer les rôles autorisés"""
    utilisateur = BooleanField('Utilisateur Standard', default=True)
    auditeur = BooleanField('Auditeur', default=True)
    manager = BooleanField('Manager', default=True)
    admin = BooleanField('Administrateur Client', default=True)
    compliance = BooleanField('Responsable Conformité', default=False)
    consultant = BooleanField('Consultant', default=False)
    
    submit = SubmitField('Mettre à jour les rôles')


class ClientUpgradeForm(FlaskForm):
    """Formulaire pour changer la formule d'un client"""
    formule_id = SelectField('Nouvelle formule', coerce=int, validators=[DataRequired()])
    periode = SelectField('Période', choices=[
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel (économisez 20%)')
    ], default='mensuel')
    is_renouvellement_auto = BooleanField('Renouvellement automatique', default=True)
    date_effet = DateField('Date d\'effet', default=datetime.utcnow)
    
    submit = SubmitField('Changer la formule')
