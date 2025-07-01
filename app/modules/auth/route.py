from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import send_file
from flask import send_file
from io import BytesIO

from app.db.models.user import User
from app.db.models.user_terms_acceptance import UserTermsAcceptance
from .controller import AuthController

auth_bp = Blueprint('auth', __name__)
auth_controller = AuthController()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    return auth_controller.register_user(data)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    return auth_controller.authenticate_user(data['email'], data['password'])

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    return auth_controller.get_profile()

@auth_bp.route("/users/<int:user_id>/profile-image", methods=["GET"])
def get_profile_image(user_id):
    user = User.query.get(user_id)
    if not user or not user.data_img:
        return {"error": "Imagem não encontrada"}, 404

    return send_file(
        BytesIO(user.data_img),
        mimetype=user.mime_type_img,
        as_attachment=False,
        download_name=user.name_img
    )

@auth_bp.route('/me/update', methods=['POST'])
@jwt_required()
def update_profile():
    return auth_controller.update_profile(request)

@auth_bp.route('/me/search', methods=['GET'])
@jwt_required()
def search_user_by_email_or_cpf():
    return auth_controller.search_user(request.args.get('identifier'))

@auth_bp.route("/terms/accept", methods=["POST"])
@jwt_required()
def accept_terms():
    data = request.get_json()
    return auth_controller.accept_terms(data.get("event_id"))

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return auth_controller.logout()

@auth_bp.route('/users/<int:user_id>/update-full-info', methods=['PUT'])
@jwt_required()
def update_user_full_info(user_id):
    return auth_controller.update_user_full_info(user_id)

@auth_bp.route('/users/full-info', methods=['GET'])
@jwt_required()
def get_all_users_full_info():
    return auth_controller.get_all_users_full_info()


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    return auth_controller.delete_user(user_id)

