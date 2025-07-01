from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from decimal import Decimal
from app.db.models.coupons import Coupon
from app.db.db import db
from app.utils.services.permission import admin_or_organizer_required
from .controller import PaymentsController

payments_bp = Blueprint("payments", __name__)
payments_controller = PaymentsController()

@payments_bp.route("/payments", methods=["POST"])
@jwt_required()
def create_payment():
    user_id = get_jwt_identity()
    return payments_controller.create_payment_controller(user_id)

@payments_bp.route("/payments-list", methods=["GET"])
def list_payments():
    return jsonify(payments_controller.list_all_payments()), 200

@payments_bp.route("/payments/confirm", methods=["POST"])
@jwt_required()
def confirm_payment():
    user_id = get_jwt_identity()
    data = request.get_json()
    reference_id = data.get("reference_id")
    response, status_code = payments_controller.confirm_payment_service(user_id, reference_id)
    return jsonify(response), status_code

@payments_bp.route("/coupons", methods=["POST"])
@jwt_required()
@admin_or_organizer_required
def create_coupon():
    claims = get_jwt()
    if claims.get("role") not in ["admin", "organizer", "organizer-adm"]:
        return jsonify({"error": "Permissão negada"}), 403

    data = request.get_json()
    code = data.get("code")
    discount_type = data.get("discount_type")
    amount = data.get("amount")
    is_active = data.get("is_active", True)

    if not all([code, discount_type, amount]):
        return jsonify({"error": "Campos obrigatórios faltando"}), 400

    if Coupon.query.filter_by(code=code).first():
        return jsonify({"error": "Código já existe"}), 400

    new_coupon = Coupon(
        code=code.upper(),
        discount_type=discount_type,
        amount=Decimal(str(amount)),
        is_active=is_active
    )
    db.session.add(new_coupon)
    db.session.commit()
    return jsonify({"message": "Cupom criado com sucesso"}), 201

@payments_bp.route("/coupons", methods=["GET"])
def get_all_coupons():
    coupons = Coupon.query.all()
    return jsonify([
        {
            "id": c.id,
            "code": c.code,
            "discount_type": c.discount_type,
            "amount": c.amount,
            "is_active": c.is_active
        } for c in coupons
    ])

@payments_bp.route("/coupons/<int:coupon_id>", methods=["DELETE"])
@jwt_required()
@admin_or_organizer_required
def delete_coupon(coupon_id):
    claims = get_jwt()
    if claims.get("role") not in ["admin", "organizer", "organizer-adm"]:
        return jsonify({"error": "Permissão negada"}), 403

    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({"error": "Cupom não encontrado"}), 404

    db.session.delete(coupon)
    db.session.commit()
    return jsonify({"message": "Cupom deletado com sucesso!"}), 200
