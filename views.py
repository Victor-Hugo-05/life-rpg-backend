from datetime import datetime
from flask import Flask, request, jsonify
from models import db, Character, CharacterAttribute, CharacterMission
from sqlalchemy import func
from services import calculate_level_and_next
from flask_cors import CORS
from flask_migrate import Migrate
import os

app = Flask(__name__)
CORS(app)

# Configura o caminho absoluto para o banco dentro da pasta instance
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'character_data.db')

SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/anton/Documents/Projetos/RPG_Habitos_Backend/seu_banco.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# cria o objeto migrate
migrate = Migrate(app, db)


############################################
##                                        
##          🟩 GENERAL ENDPOINTS          
##                                        
############################################

# Aqui vão suas rotas do Flask, exemplo:
@app.route('/')
def home():
    return "RPG Habits API is running"

############################################
##                                        ##
##         🟦 CHARACTER ENDPOINTS         ##
##                                        ##
############################################

@app.route('/character/<string:name>', methods=['GET'])
def get_character(name):
    character = Character.query.filter_by(name=name).first()
    if not character:
        return jsonify({"error": "Character not found"}), 404

    if not character.attributes:
        return jsonify({"error": "Character attributes not found"}), 404

    return jsonify({
        "name": character.name,
        "attributes": {
            "Força": {"xp": character.attributes.strength_xp},
            "Disciplina": {"xp": character.attributes.discipline_xp},
            "Carisma": {"xp": character.attributes.charisma_xp},
            "Inteligência": {"xp": character.attributes.intelligence_xp},
        },
        "missions": [
            {
                "title": mission.title,
                "description": mission.description,
                "xp_reward": mission.xp_reward,
                "related_attributes": [
                    attr for attr, flag in [
                        ("Força", mission.strength),
                        ("Disciplina", mission.discipline),
                        ("Carisma", mission.charisma),
                        ("Inteligência", mission.intelligence)
                    ] if flag
                ],
                "completed": mission.completed
            }
            for mission in character.missions
        ]
    })


@app.route('/character', methods=['POST'])
def create_character():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Missing name"}), 400

    if Character.query.filter_by(name=name).first():
        return jsonify({"error": "Character name already exists"}), 400

    try:
        character = Character(name=name)
        attributes = CharacterAttribute(character=character)
        
        db.session.add(character)
        db.session.add(attributes)
        db.session.commit()
        
        return jsonify({
            "message": "Character created",
            "character_id": character.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


############################################
##                                        ##
##          🟨 MISSION ENDPOINTS          ##
##                                        ##
############################################

@app.route('/character/<string:name>/mission', methods=['POST'])
def add_mission(name):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")
    xp_reward = data.get("xp_reward", 0)
    related_attributes = data.get("related_attributes", [])

    if not title:
        return jsonify({"error": "Missing mission title"}), 400

    character = Character.query.filter_by(name=name).first()
    if not character:
        return jsonify({"error": "Character not found"}), 404

    try:
        mission = CharacterMission(
            character=character,
            title=title,
            description=description,
            xp_reward=xp_reward,
            strength="Força" in related_attributes,
            discipline="Disciplina" in related_attributes,
            charisma="Carisma" in related_attributes,
            intelligence="Inteligência" in related_attributes
        )
        
        db.session.add(mission)
        db.session.commit()
        
        return jsonify({"message": "Mission added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/character/<string:name>/complete_mission', methods=['POST'])
def complete_mission(name):
    data = request.get_json()
    mission_title = data.get("mission_title")

    if not mission_title:
        return jsonify({"error": "Missing mission_title"}), 400

    character = Character.query.filter_by(name=name).first()
    if not character:
        return jsonify({"error": "Character not found"}), 404

    mission = CharacterMission.query.filter(
        CharacterMission.character_id == character.id,
        func.lower(CharacterMission.title) == func.lower(mission_title),
        CharacterMission.completed == False
    ).first()

    if not mission:
        return jsonify({"error": "Mission not found or already completed"}), 404

    try:
        attributes = character.attributes
        xp = mission.xp_reward

        response_data = {
            "message": f"Missão '{mission.title}' completada!",
            "attribute_progress": {}
        }

        def update_attribute(attr_name):
            attr_xp = getattr(attributes, f"{attr_name}_xp")
            attr_xp += xp
            setattr(attributes, f"{attr_name}_xp", attr_xp)

            level, next_threshold, xp_to_next = calculate_level_and_next(attr_xp)

            response_data["attribute_progress"][attr_name] = {
                "xp": attr_xp,
                "level": level,
                "xp_to_next_level": xp_to_next,
                "next_level_at": next_threshold
            }

        if mission.strength:
            update_attribute("strength")
        if mission.discipline:
            update_attribute("discipline")
        if mission.charisma:
            update_attribute("charisma")
        if mission.intelligence:
            update_attribute("intelligence")

        mission.completed = True
        db.session.commit()

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@app.route('/reset_missions', methods=['POST'])
def reset_all_missions():
    try:
        # Atualiza todas as missões completadas para incompletas
        updated_count = db.session.query(CharacterMission).filter_by(completed=True).update(
            {'completed': False},
            synchronize_session=False
        )
        
        db.session.commit()
        
        return jsonify({
            "message": f"Missões resetadas com sucesso! {updated_count} missões foram reiniciadas.",
            "reset_count": updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/daily-update', methods=['POST'])
def check_missions():
    base_xp = 30
    xp_growth = 0.5  # crescimento lento por streak
    
    missions = CharacterMission.query.all()
    results = []

    for mission in missions:
        if mission.completed:
            mission.streak += 1

            # XP reward aumenta de forma linear e lenta
            mission.xp_reward = round(base_xp + (mission.streak - 1) * xp_growth)

        else:
            mission.streak = 0
            mission.xp_reward = base_xp

        mission.completed = False

        results.append({
            'mission_id': mission.id,
            'mission_title': mission.title,
            'xp_reward': mission.xp_reward,
            'current_streak': mission.streak
        })

    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Missions checked, streaks and XP updated',
        'missions': results
    }), 200




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True)
