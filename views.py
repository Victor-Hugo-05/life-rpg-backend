from datetime import datetime
from flask import Flask, request, jsonify
from models import db, Character, CharacterAttribute, CharacterMission, MissionTemplate
from sqlalchemy import func
from services import calculate_level_and_next, _build_cors_preflight_response, get_xp_by_difficulty
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SUPABASE_CONNECTION_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def home():
    return "RPG Habits API is running"

@app.route('/character/<string:name>', methods=['GET', 'OPTIONS'])
def get_character(name):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

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
            "Saúde": {"xp": character.attributes.health_xp},
            "Inteligência": {"xp": character.attributes.intelligence_xp},
        },
        "missions": [
            {
                "title": mission.title,
                "description": mission.description,
                "xp_reward": mission.xp_reward,
                "difficulty": mission.difficulty,
                "related_attributes": [
                    attr for attr, flag in [
                        ("Força", mission.strength),
                        ("Disciplina", mission.discipline),
                        ("Saúde", mission.health),
                        ("Inteligência", mission.intelligence)
                    ] if flag
                ],
                "completed": mission.completed
            }
            for mission in character.missions
        ]
    })

@app.route('/character', methods=['POST', 'OPTIONS'])
def create_character():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

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

@app.route('/missions/templates', methods=['GET'])
def list_mission_templates():
    templates = MissionTemplate.query.all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "xp_reward": t.xp_reward,
            "difficulty": t.difficulty,
            "related_attributes": [
                attr for attr, flag in [
                    ("Força", t.strength),
                    ("Disciplina", t.discipline),
                    ("Saúde", t.health),
                    ("Inteligência", t.intelligence)
                ] if flag
            ]
        }
        for t in templates
    ])

@app.route('/character/<string:name>/mission', methods=['POST'])
def add_mission(name):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")
    difficulty = data.get("difficulty", "Fácil")
    xp_reward = get_xp_by_difficulty(difficulty)
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
            difficulty=difficulty,
            strength="Força" in related_attributes,
            discipline="Disciplina" in related_attributes,
            health="Saúde" in related_attributes,
            intelligence="Inteligência" in related_attributes
        )

        db.session.add(mission)
        db.session.commit()

        return jsonify({"message": "Mission added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/character/<string:name>/mission/template', methods=['POST'])
def add_mission_from_template(name):
    data = request.get_json()
    template_id = data.get("template_id")

    if not template_id:
        return jsonify({"error": "Missing template_id"}), 400

    character = Character.query.filter_by(name=name).first()
    if not character:
        return jsonify({"error": "Character not found"}), 404

    template = MissionTemplate.query.get(template_id)
    if not template:
        return jsonify({"error": "Mission template not found"}), 404

    existing_mission = CharacterMission.query.filter_by(character_id=character.id, title=template.title).first()
    if existing_mission:
        return jsonify({"error": "Character already has this mission"}), 400

    try:
        xp_reward = get_xp_by_difficulty(template.difficulty)

        mission = CharacterMission(
            character=character,
            title=template.title,
            description=template.description,
            xp_reward=xp_reward,
            difficulty=template.difficulty,
            strength=template.strength,
            discipline=template.discipline,
            health=template.health,
            intelligence=template.intelligence
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
            attr_xp = getattr(attributes, f"{attr_name}_xp") or 0  # força 0 se for None
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
        if mission.health:
            update_attribute("health")
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
    missions = CharacterMission.query.all()
    results = []

    for mission in missions:
        if mission.completed:
            mission.streak += 1
        else:
            mission.streak = 0

        mission.xp_reward = get_xp_by_difficulty(mission.difficulty)
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
    app.run(host='0.0.0.0', port=5000, debug=True)
