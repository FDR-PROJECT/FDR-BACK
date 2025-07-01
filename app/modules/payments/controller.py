from decimal import ROUND_HALF_UP, Decimal
import os
from flask import jsonify, request
from sqlalchemy import or_
import mercadopago
import requests
from app.db import db
from app.db.models.category import Category
from app.db.models.coupons import Coupon
from app.db.models.event import Event
from app.db.models.payment import Payment
from app.db.models.registration import Registration
from app.db.models.user import User
from dotenv import load_dotenv

from app.utils.services.payment import gerar_pagamento_pix_para_cliente

load_dotenv()

sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))
class PaymentsController:
    def index(self):
        return {'message': 'Hello, World!'}
      # 👈 Criamos esse utilitário

    def create_payment_controller(self, user_id):
        data = request.get_json()
        category_id = data.get("category_id")
        event_id = data.get("event_id")
        partner_identifier = data.get("partner_email")

        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Categoria inválida"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # Impede duplicidade de inscrição
        already_registered = Registration.query.filter_by(
            athlete_id=user_id,
            event_id=event_id,
            category_id=category_id
        ).first()
        if already_registered:
            return jsonify({"error": "Você já está inscrito nesta categoria para este evento."}), 400

        # Verifica parceiro (se informado)
        partner = None
        if partner_identifier:
            partner = User.query.filter(
                or_(User.email == partner_identifier, User.cpf == partner_identifier)
            ).first()
            if partner:
                partner_registered = Registration.query.filter_by(
                    athlete_id=partner.id,
                    event_id=event_id,
                    category_id=category_id
                ).first()
                if partner_registered:
                    return jsonify({"error": f"O parceiro '{partner.name}' já está inscrito nesta categoria para este evento."}), 400
            else:
                return jsonify({"error": "Parceiro não encontrado"}), 404

        # Verifica limite de vagas
        if category.participant_limit is not None:
            current_registrations = Registration.query.filter_by(
                category_id=category_id,
                event_id=event_id
            ).count()
            if category.participant_limit <= 0:
                return jsonify({"error": "Esta categoria não permite inscrições."}), 400
            if current_registrations >= category.participant_limit:
                return jsonify({"error": "Limite de vagas atingido para esta categoria."}), 400

        coupon_code = data.get("coupon_code")
        discount_applied = None

        if coupon_code:

            coupon = Coupon.query.filter_by(code=coupon_code.upper(), is_active=True).first()
            if not coupon:
                return jsonify({"error": "Cupom inválido"}), 400

            original_price = category.price

            if coupon.discount_type == "percent":
                discount = (original_price * Decimal(coupon.amount)) / Decimal(100)
                amount = original_price - discount
            elif coupon.discount_type == "value":
                amount = max(original_price - Decimal(coupon.amount), Decimal("0"))
            else:
                return jsonify({"error": "Tipo de cupom inválido"}), 400

            discount_applied = {
                "coupon_code": coupon.code,
                "discount_type": coupon.discount_type,
                "discount_amount": coupon.amount,
                "original_price": original_price,
                "final_price": amount
            }
            coupon.is_active = False
            db.session.add(coupon)
        else:
            amount = category.price
            

        reference_id = f"pix-{user_id}-{event_id}-{category_id}"

        # Evita gerar duplicado
        existing_payment = Payment.query.filter_by(reference_id=reference_id).first()
        if existing_payment:
            return jsonify({
                "reference_id": existing_payment.reference_id,
                "pix_qr_code": existing_payment.qr_code_text,
                "pix_qr_code_image_base64": existing_payment.qr_code_image_url
            }), 200

        # 💥 Se o valor for zero, já registra a inscrição diretamente
        if Decimal(amount) <= Decimal("0.00"):
            registration = Registration(
                athlete_id=user_id,
                event_id=event_id,
                category_id=category_id,
                partner_id=partner.id if partner else None
            )
           
            db.session.add(registration)

            payment = Payment(
                user_id=user_id,
                event_id=event_id,
                category_id=category_id,
                partner_id=partner.id if partner else None,
                reference_id=reference_id,
                amount=0,
                payment_id="ZERO_PAYMENT",
                qr_code_text=None,
                qr_code_image_url=None,
                status="APPROVED"
            )
            db.session.add(payment)

            # Marca o cupom como usado
            if coupon_code and coupon:
                coupon.is_active = False
                db.session.add(coupon)

            db.session.commit()

            return jsonify({
                "message": "Inscrição confirmada com sucesso! Nenhum pagamento necessário.",
                "registration_confirmed": True
            }), 201


        # Geração de pagamento Pix via Mercado Pago
        user.amount = amount  # já com desconto
        user.event_id = event_id
        pix_info, error = gerar_pagamento_pix_para_cliente(user)

        if error:
            return jsonify(error), 400
        
        amount_in_cents = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

        payment = Payment(
            user_id=user_id,
            event_id=event_id,
            category_id=category_id,
            payment_id=pix_info["payment_id"],
            partner_id=partner.id if partner else None,
            reference_id=reference_id,
            amount=amount_in_cents,  # assumindo centavos
            qr_code_text=pix_info["pix_qr_code"],
            qr_code_image_url=pix_info["pix_qr_code_image_base64"],
            status="PENDING"
        )

        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "reference_id": reference_id,
            "discount_applied": discount_applied,
            "pix_qr_code": pix_info["pix_qr_code"],
            "pix_qr_code_image_base64": pix_info["pix_qr_code_image_base64"],
            "pix_expiration": pix_info["pix_expiration"]
        }), 201
        
    def list_all_payments(self):
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
        grouped = {}

        for p in payments:
            user = User.query.get(p.user_id)
            partner = User.query.get(p.partner_id) if p.partner_id else None
            category = Category.query.get(p.category_id)
            event = Event.query.get(p.event_id)

            if not category or not user:
                continue

            cat_key = f"{category.id}"
            if cat_key not in grouped:
                grouped[cat_key] = {
                    "category": {
                        "id": category.id,
                        "name": category.name
                    },
                    "event": {
                        "id": event.id,
                        "title": event.title
                    } if event else None,
                    "inscricoes": []
                }

            grouped[cat_key]["inscricoes"].append({
                "payment_id": p.id,
                "status": "PENDENTE" if p.status == "PENDING" else "APROVADO" if p.status == "APPROVED" else p.status,
                "reference_id": p.reference_id,
                "amount": float(p.amount) / 100,
                "created_at": p.created_at.isoformat(),
                "athlete": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "nickname": user.nickname  # 👈 adiciona isso
                },
                "partner": {
                    "id": partner.id,
                    "name": partner.name,
                    "email": partner.email,
                    "nickname": partner.nickname  # 👈 adiciona isso também
                } if partner else None,

            })

        return list(grouped.values())
    
    def confirm_payment_service(self, user_id, reference_id):
        payment = Payment.query.filter_by(reference_id=reference_id, user_id=user_id).first()
        if not payment:
            return {"error": "Pagamento não encontrado"}, 404

        if payment.status == "APPROVED":
            return {"message": "Inscrição já confirmada"}, 200

        # Consulta o Mercado Pago
        payment_response = sdk.payment().get(payment.payment_id)
        if payment_response["status"] != 200:
            return {
                "error": "Erro ao consultar status no Mercado Pago",
                "details": payment_response.get("response", {})
            }, payment_response["status"]

        status = payment_response["response"].get("status")

        if status in ["approved", "authorized"]:
            payment.status = "APPROVED"

            registration = Registration(
                athlete_id=user_id,
                event_id=payment.event_id,
                category_id=payment.category_id,
                partner_id=payment.partner_id
            )

            db.session.add(payment)
            db.session.add(registration)
            db.session.commit()

            return {"message": "Inscrição confirmada com sucesso!"}, 200

        else:
            payment.status = "PENDING"
            db.session.add(payment)
            db.session.commit()

            return {"message": "Pagamento ainda não foi confirmado. Tente novamente mais tarde."}, 202

   