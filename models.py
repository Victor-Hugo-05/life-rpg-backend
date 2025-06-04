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