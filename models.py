from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Character(db.Model):
    """
    Modelo para armazenar informações sobre personagens (usuários).
    
    Attributes:
        id (int): Identificador único do personagem.
        name (str): Nome do personagem (deve ser único).
        attributes (relationship): Relação com os atributos do personagem.
        missions (relationship): Relação com as missões do personagem.
    """
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relacionamentos
    attributes = db.relationship('CharacterAttribute', back_populates='character', uselist=False)
    missions = db.relationship('CharacterMission', back_populates='character')


class CharacterAttribute(db.Model):
    """
    Modelo para armazenar os atributos de um personagem.
    
    Attributes:
        id (int): Identificador único do registro de atributos.
        character_id (int): ID do personagem associado (chave estrangeira).
        strength_xp (int): Experiência acumulada em Força.
        discipline_xp (int): Experiência acumulada em Disciplina.
        charisma_xp (int): Experiência acumulada em Carisma.
        intelligence_xp (int): Experiência acumulada em Inteligência.
    """
    __tablename__ = 'character_attributes'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), unique=True, nullable=False)
    strength_xp = db.Column(db.Integer, default=0)
    discipline_xp = db.Column(db.Integer, default=0)
    charisma_xp = db.Column(db.Integer, default=0)
    intelligence_xp = db.Column(db.Integer, default=0)
    
    # Relacionamento
    character = db.relationship('Character', back_populates='attributes')


class CharacterMission(db.Model):
    """
    Modelo para armazenar as missões de um personagem.
    
    Attributes:
        id (int): Identificador único da missão.
        character_id (int): ID do personagem associado (chave estrangeira).
        title (str): Título da missão.
        description (str): Descrição detalhada da missão.
        xp_reward (int): Recompensa de XP por completar a missão.
        strength (bool): Indica se a missão está relacionada à Força.
        discipline (bool): Indica se a missão está relacionada à Disciplina.
        charisma (bool): Indica se a missão está relacionada ao Carisma.
        intelligence (bool): Indica se a missão está relacionada à Inteligência.
        completed (bool): Indica se a missão foi completada.
    """
    __tablename__ = 'character_missions'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    xp_reward = db.Column(db.Integer, default=0)
    strength = db.Column(db.Boolean, default=False)
    discipline = db.Column(db.Boolean, default=False)
    charisma = db.Column(db.Boolean, default=False)
    intelligence = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    streak = db.Column(db.Integer, default=0)
    
    # Relacionamento
    character = db.relationship('Character', back_populates='missions')

class CharacterRelic(db.Model):
    """
    Modelo para armazenar as relíquias conquistadas por um personagem.

    Attributes:
        id (int): Identificador único da relíquia.
        character_id (int): ID do personagem associado (chave estrangeira).
        name (str): Nome da relíquia.
        description (str): Descrição da relíquia, incluindo contexto ou lore.
        unlocked_at (datetime): Data e hora em que a relíquia foi desbloqueada.
        bonus_type (str): Tipo de bônus passivo associado (opcional).
        bonus_value (float): Valor do bônus (opcional, exemplo: 0.05 para +5% XP).
    """
    __tablename__ = 'character_relics'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    unlocked_at = db.Column(db.DateTime, nullable=False)
    bonus_type = db.Column(db.String(50), nullable=True)  # Ex: "strength_xp_boost", "mission_streak_bonus"
    bonus_value = db.Column(db.Float, default=0.0)

    # Relacionamento
    character = db.relationship('Character', backref='relics')

class MissionTemplate(db.Model):
    """
    Modelo para armazenar missões pré-definidas (catálogo).
    """
    __tablename__ = 'mission_templates'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    xp_reward = db.Column(db.Integer, default=0)
    strength = db.Column(db.Boolean, default=False)
    discipline = db.Column(db.Boolean, default=False)
    charisma = db.Column(db.Boolean, default=False)
    intelligence = db.Column(db.Boolean, default=False)