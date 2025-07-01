from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .controller import RegistrationsController

registrations_bp = Blueprint('registrations', __name__)
registrations_controller = RegistrationsController()

@registrations_bp.route('/register', methods=['POST'])
@jwt_required()
def register_to_event():
    user_id = get_jwt_identity()
    data = request.json
    return registrations_controller.register_to_event_controller(user_id, data)


@registrations_bp.route('/payment/status', methods=['PUT'])
def update_payment_status():
    data = request.json
    return registrations_controller.update_payment_status_controller(data)


@registrations_bp.route('/registration', methods=['DELETE'])
def delete_registration():
    athlete_email = request.args.get("athlete_email")
    return registrations_controller.delete_registration_controller(athlete_email)
