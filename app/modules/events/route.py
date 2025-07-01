from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from .controller import EventsController

events_bp = Blueprint('events', __name__)
events_controller = EventsController()

def role_required(required_roles):
    def wrapper():
        jwt_data = get_jwt()
        user_role = jwt_data.get("role")
        if user_role not in required_roles:
            return jsonify({"error": "Unauthorized"}), 403
        return None
    return wrapper

@events_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    unauthorized = role_required(['organizer', 'admin', 'organizer-adm'])()
    if unauthorized: return unauthorized

    data = request.json
    organizer_id = get_jwt_identity()

    if not organizer_id:
        return jsonify({"error": "ID do organizador não encontrado"}), 400

    event = events_controller.create_event(data, organizer_id)
    return jsonify(event.id), 201

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update(event_id):
    unauthorized = role_required(['organizer', 'admin', 'organizer-adm'])()
    if unauthorized: return unauthorized

    data = request.json
    try:
        event = events_controller.update_event(event_id, data)
        return jsonify({
            "message": "Evento atualizado com sucesso",
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "date": event.date,
                "end_date": event.end_date,
                "image_url": event.image_url
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete(event_id):
    unauthorized = role_required(['organizer', 'admin', 'organizer-adm'])()
    if unauthorized: return unauthorized

    events_controller.delete_event(event_id)
    return jsonify({"message": "Evento deletado com sucesso!"})

@events_bp.route('/', methods=['GET'])
def list_all():
    events = events_controller.get_all_events()
    return jsonify([
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "location": e.location,
            "date": e.date.isoformat() if e.date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "image_url": e.image_url
        }
        for e in events
    ])
