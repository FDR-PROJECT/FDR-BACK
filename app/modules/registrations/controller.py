from flask import jsonify
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.db.db import db
from app.db.models.category import Category
from app.db.models.event import Event
from app.db.models.registration import Registration
from app.db.models.user import User
from app.db.models.payment import Payment


class RegistrationsController:

    def register_to_event_controller(self, user_id, data):
        try:
            event = Event.query.get(data["event_id"])
            category = Category.query.get(data["category_id"])
            if not event or not category:
                return jsonify({"error": "Evento ou categoria inválida"}), 400

            partner_email = data.get("partner_email")
            if not partner_email:
                return jsonify({"error": "O e-mail do parceiro é obrigatório."}), 400

            partner_user = User.query.filter_by(email=partner_email).first()
            if not partner_user:
                return jsonify({"error": "Parceiro não encontrado. Ele precisa se cadastrar antes."}), 400

            # Verifica se qualquer dos dois já está inscrito nesta categoria e evento
            dupla_ja_inscrita = Registration.query.filter_by(
                event_id=event.id,
                category_id=category.id
            ).filter(
                (Registration.athlete_id.in_([user_id, partner_user.id])) |
                (Registration.partner_id.in_([user_id, partner_user.id]))
            ).first()

            if dupla_ja_inscrita:
                return jsonify({
                    "error": "Você ou o parceiro já está inscrito nesta categoria do evento."
                }), 400

            # Verifica se a categoria ainda tem vagas
            if category.participant_limit is not None:
                duplas_inscritas = Registration.query.filter_by(
                    event_id=event.id,
                    category_id=category.id
                ).count()

                if category.participant_limit <= 0:
                    return jsonify({"error": "Esta categoria não está disponível para inscrições."}), 400

                if duplas_inscritas >= category.participant_limit:
                    return jsonify({"error": "Limite de vagas atingido para esta categoria."}), 400

            # Cria nova inscrição
            new_registration = Registration(
                event_id=event.id,
                category_id=category.id,
                athlete_id=user_id,
                partner_id=partner_user.id,
            )

            db.session.add(new_registration)
            db.session.commit()
            return jsonify({"message": "Inscrição realizada com sucesso!"}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def update_payment_status_controller(self, data):
        athlete_email = data.get("athlete_email")
        new_status = data.get("status")

        if not athlete_email or not new_status:
            return {"error": "Parâmetros 'athlete_email' e 'status' são obrigatórios."}, 400

        payment = (
            Payment.query
            .join(User, Payment.user_id == User.id)
            .filter(User.email == athlete_email)
            .first()
        )

        if not payment:
            return {"error": "Pagamento não encontrado para o e-mail informado."}, 404

        payment.status = new_status.upper()
        # 💥 Se o novo status for aprovado, criar a inscrição (se ainda não existir)
        if payment.status == "APPROVED":
            existing_registration = Registration.query.filter_by(
                athlete_id=payment.user_id,
                event_id=payment.event_id,
                category_id=payment.category_id
            ).first()

            if not existing_registration:
                registration = Registration(
                    athlete_id=payment.user_id,
                    event_id=payment.event_id,
                    category_id=payment.category_id,
                    partner_id=payment.partner_id
                )
                db.session.add(registration)
        db.session.commit()
        return {"message": "Status do pagamento atualizado com sucesso."}, 200

    def delete_registration_controller(self, athlete_email):
        if not athlete_email:
            return {"error": "Parâmetro 'athlete_email' é obrigatório."}, 400

        user = User.query.filter_by(email=athlete_email).first()
        if not user:
            return {"error": "Usuário não encontrado."}, 404

        # Exclui inscrição
        registration = Registration.query.filter_by(athlete_id=user.id).first()
        if registration:
            db.session.delete(registration)

        # Exclui pagamento associado
        payment = Payment.query.filter_by(user_id=user.id).first()
        if payment:
            db.session.delete(payment)

        db.session.commit()
        return {"message": "Inscrição e pagamento removidos com sucesso."}, 200
