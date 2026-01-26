from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, RadioField, SubmitField, HiddenField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange

class EvaluationTriPhaseForm(FlaskForm):
    # Phase 1: Pré-évaluation
    referent_pre_evaluation_id = SelectField('Référent pré-évaluation', coerce=int, validators=[DataRequired()])
    impact_pre = SelectField('Impact', choices=[
        (0, 'Sélectionnez un niveau'),
        (1, '1 - Négligeable'),
        (2, '2 - Mineur'),
        (3, '3 - Modéré'),
        (4, '4 - Important'),
        (5, '5 - Critique')
    ], coerce=int, validators=[DataRequired()])
    probabilite_pre = SelectField('Probabilité', choices=[
        (0, 'Sélectionnez un niveau'),
        (1, '1 - Très rare'),
        (2, '2 - Rare'),
        (3, '3 - Possible'),
        (4, '4 - Probable'),
        (5, '5 - Très probable')
    ], coerce=int, validators=[DataRequired()])
    niveau_maitrise_pre = SelectField('Niveau de maîtrise', choices=[
        (0, 'Sélectionnez un niveau'),
        (1, '1 - Insuffisant'),
        (2, '2 - Partiel'),
        (3, '3 - Adéquat'),
        (4, '4 - Bon'),
        (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    commentaire_pre_evaluation = TextAreaField('Commentaire pré-évaluation')
    
    # Phase 2: Validation
    statut_validation = RadioField('Validation', choices=[
        ('valide', '✅ Valider la pré-évaluation'),
        ('rejetee', '🔄 Rejeter et modifier'),
        ('en_attente', '⏳ En attente')
    ], default='en_attente')
    impact_val = SelectField('Impact (validation)', choices=[
        (0, 'Conserver pré-évaluation'),
        (1, '1 - Négligeable'),
        (2, '2 - Mineur'),
        (3, '3 - Modéré'),
        (4, '4 - Important'),
        (5, '5 - Critique')
    ], coerce=int, validators=[Optional()])
    probabilite_val = SelectField('Probabilité (validation)', choices=[
        (0, 'Conserver pré-évaluation'),
        (1, '1 - Très rare'),
        (2, '2 - Rare'),
        (3, '3 - Possible'),
        (4, '4 - Probable'),
        (5, '5 - Très probable')
    ], coerce=int, validators=[Optional()])
    niveau_maitrise_val = SelectField('Niveau de maîtrise (validation)', choices=[  # AJOUTÉ
        (0, 'Conserver pré-évaluation'),
        (1, '1 - Insuffisant'),
        (2, '2 - Partiel'),
        (3, '3 - Adéquat'),
        (4, '4 - Bon'),
        (5, '5 - Excellent')
    ], coerce=int, validators=[Optional()])
    commentaire_validation = TextAreaField('Commentaire validation')
    
    # Phase 3: Confirmation
    impact_conf = SelectField('Impact (confirmation)', choices=[
        (0, 'Conserver validation'),
        (1, '1 - Négligeable'),
        (2, '2 - Mineur'),
        (3, '3 - Modéré'),
        (4, '4 - Important'),
        (5, '5 - Critique')
    ], coerce=int, validators=[Optional()])
    probabilite_conf = SelectField('Probabilité (confirmation)', choices=[
        (0, 'Conserver validation'),
        (1, '1 - Très rare'),
        (2, '2 - Rare'),
        (3, '3 - Possible'),
        (4, '4 - Probable'),
        (5, '5 - Très probable')
    ], coerce=int, validators=[Optional()])
    niveau_maitrise_conf = SelectField('Niveau de maîtrise (confirmation)', choices=[  # AJOUTÉ
        (0, 'Conserver validation'),
        (1, '1 - Insuffisant'),
        (2, '2 - Partiel'),
        (3, '3 - Adéquat'),
        (4, '4 - Bon'),
        (5, '5 - Excellent')
    ], coerce=int, validators=[Optional()])
    commentaire_confirmation = TextAreaField('Commentaire confirmation')
    
    # Informations de campagne d'évaluation
    campagne_nom = StringField('Nom de la campagne d\'évaluation', validators=[Optional()])
    campagne_date_debut = DateField('Date de début de campagne', format='%Y-%m-%d', validators=[Optional()])
    campagne_date_fin = DateField('Date de fin de campagne', format='%Y-%m-%d', validators=[Optional()])
    campagne_objectif = TextAreaField('Objectif de la campagne', validators=[Optional()])
    
    # Boutons de soumission avec icônes
    submit_phase1 = SubmitField('📝 Enregistrer la Pré-évaluation')
    submit_phase2 = SubmitField('✅ Valider l\'Évaluation')
    submit_phase3 = SubmitField('🎯 Confirmer l\'Évaluation Finale')
