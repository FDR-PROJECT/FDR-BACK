from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.db.db import db
from app.db.models.user import User
from werkzeug.utils import secure_filename
from app.db.models.user_terms_acceptance import UserTermsAcceptance
from app.utils.services.security import create_jwt_token, hash_password, verify_password


# Simples, substitua isso por Redis no futuro
jwt_blocklist = set()

class AuthController:

    def register_user(self, data):
        user = User(
            name=data['name'],
            email=data['email'],
            cpf=data['cpf'],
            phone=data['phone'],
            password_hash=hash_password(data['password']),
            role='athlete',
            birth_date=data.get('birth_date'),
            gender=data.get('gender'),
            uniform_size=data.get('uniform_size'),
            category=data.get('category'),
            nickname=data.get('nickname'),
            address_full=data.get('address_full'),
            district=data.get('district'),
            city=data.get('city'),
            state=data.get('state'),
            team=data.get('team'),
        )
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"message": "User registered!"}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Email already in use."}), 400

    def authenticate_user(self, email, password):
        user = User.query.filter_by(email=email).first()
        
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Credenciais inválidas"}), 401

        token = create_jwt_token(user)
        return jsonify({
            "access_token": token,
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value
        }), 200

    def get_profile(self):
        user_id = get_jwt_identity()
        claims = get_jwt()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "phone": user.phone,
            "role": claims.get("role"),
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "gender": user.gender,
            "uniform_size": user.uniform_size,
            "category": user.category,
            "nickname": user.nickname,
            "address_full": user.address_full,
            "district": user.district,
            "city": user.city,
            "state": user.state,
            "team": user.team,
            "has_image": bool(user.data_img),
            "name_img": user.name_img,
            "mime_type_img": user.mime_type_img,
            "image_url": f"/users/{user.id}/profile-image" if user.data_img else None
        }

        return jsonify(user_data), 200


    def update_profile(self, request):
        user_id = get_jwt_identity()
        claims = get_jwt()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # multipart ou json
        data = request.form if request.content_type.startswith('multipart/form-data') else request.get_json()

        editable_fields = [
            'gender', 'uniform_size', 'category', 'nickname', 'cpf',
            'address_full', 'district', 'city', 'state', 'team', 'phone'
        ]

        if claims["role"] in ["admin", "organizer", "organizer-adm"]:
            editable_fields += ['email', 'category', 'cpf']

        if data and 'birth_date' in data:
            try:
                user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Data de nascimento inválida"}), 400

        for field in editable_fields:
            if field in data:
                setattr(user, field, data[field])

        # Upload de imagem
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = secure_filename(file.filename)
                user.data_img = file.read()
                user.mime_type_img = file.mimetype
                user.name_img = filename

        db.session.commit()

        return jsonify({
            "message": "Perfil atualizado com sucesso!",
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "birth_date": user.birth_date,
                "gender": user.gender,
                "category": user.category,
                "uniform_size": user.uniform_size,
                "cpf": user.cpf,
                "address_full": user.address_full,
                "district": user.district,
                "city": user.city,
                "state": user.state,
                "team": user.team,
                "image_url": f"/users/{user.id}/profile-image" if user.data_img else None
            }
        }), 200


    def search_user(self, identifier):
        if not identifier:
            return jsonify({"error": "Identificador (email ou CPF) não informado"}), 400

        user = User.query.filter(
            (User.email == identifier) | (User.cpf == identifier)
        ).first()

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "phone": user.phone,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "gender": user.gender,
            "uniform_size": user.uniform_size,
            "nickname": user.nickname,
            "address_full": user.address_full,
            "district": user.district,
            "city": user.city,
            "state": user.state,
            "team": user.team
        }), 200

    def accept_terms(self, event_id):
        user_id = get_jwt_identity()

        if not event_id:
            return jsonify({"error": "ID do evento é obrigatório"}), 400

        existing = UserTermsAcceptance.query.filter_by(user_id=user_id, event_id=event_id).first()
        if existing:
            return jsonify({"message": "Termos já aceitos anteriormente"}), 200

        acceptance = UserTermsAcceptance(user_id=user_id, event_id=event_id)
        db.session.add(acceptance)
        db.session.commit()

        return jsonify({"message": "Termos aceitos com sucesso!"}), 201

    def logout(self):
        jti = get_jwt()["jti"]
        jwt_blocklist.add(jti)
        return jsonify({"message": "Logout realizado com sucesso!"}), 200


    def get_full_user_info(self, user_id):
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # Dados de inscrições (como atleta e como parceiro)
        registrations = []
        for reg in user.registrations_as_athlete + user.registrations_as_partner:
            registrations.append({
                "registration_id": reg.id,
                "event_id": reg.event_id,
                "event_name": reg.event.title if reg.event else None,
                "category_id": reg.category_id,
                "category_name": reg.category.name if reg.category else None,
                "as_role": "athlete" if reg.athlete_id == user.id else "partner",
                "created_at": reg.created_at.isoformat()
            })

        # Pagamentos
        payments = []
        for payment in user.payments:
            payments.append({
                "payment_id": payment.payment_id,
                "reference_id": payment.reference_id,
                "amount": payment.amount,
                "status": payment.status,
                "event_id": payment.event_id,
                "category_id": payment.category_id,
                "coupon": payment.coupon.code if payment.coupon else None,
                "created_at": payment.created_at.isoformat()
            })

        # Termos aceitos
        accepted_terms = UserTermsAcceptance.query.filter_by(user_id=user_id).all()
        terms = [
            {"event_id": t.event_id, "accepted_at": t.accepted_at.isoformat()}
            for t in accepted_terms
        ]

        # Dados principais
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "phone": user.phone,
            "role": user.role.value,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "gender": user.gender,
            "uniform_size": user.uniform_size,
            "category": user.category,
            "nickname": user.nickname,
            "address_full": user.address_full,
            "district": user.district,
            "city": user.city,
            "state": user.state,
            "team": user.team,
            "has_image": bool(user.data_img),
            "image_url": f"/users/{user.id}/profile-image" if user.data_img else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

        return jsonify({
            "user": user_data,
            "registrations": registrations,
            "payments": payments,
            "terms": terms
        }), 200
        
    def get_all_users_full_info(self):
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=6, type=int)

            # Filtros
        name = request.args.get("name", type=str)
        cpf = request.args.get("cpf", type=str)
        email = request.args.get("email", type=str)
        category = request.args.get("category", type=str)

        query = User.query

        if name:
            query = query.filter(User.name.ilike(f"%{name}%"))
        if cpf:
            query = query.filter(User.cpf.ilike(f"%{cpf}%"))
        if email:
            query = query.filter(User.email.ilike(f"%{email}%"))
        if category:
            query = query.filter(User.category.ilike(f"%{category}%"))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items
        result = []

        for user in users:
            registrations = []
            for reg in user.registrations_as_athlete + user.registrations_as_partner:
                registrations.append({
                    "registration_id": reg.id,
                    "event_id": reg.event_id,
                    "event_name": reg.event.title if reg.event else None,
                    "category_id": reg.category_id,
                    "category_name": reg.category.name if reg.category else None,
                    "as_role": "athlete" if reg.athlete_id == user.id else "partner",
                    "created_at": reg.created_at.isoformat()
                })

            payments = []
            for payment in user.payments:
                payments.append({
                    "payment_id": payment.payment_id,
                    "reference_id": payment.reference_id,
                    "amount": payment.amount,
                    "status": payment.status,
                    "event_id": payment.event_id,
                    "category_id": payment.category_id,
                    "coupon": payment.coupon.code if payment.coupon else None,
                    "created_at": payment.created_at.isoformat()
                })

            terms = UserTermsAcceptance.query.filter_by(user_id=user.id).all()
            accepted_terms = [
                {"event_id": t.event_id, "accepted_at": t.accepted_at.isoformat()}
                for t in terms
            ]

            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "cpf": user.cpf,
                "phone": user.phone,
                "role": user.role.value,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "gender": user.gender,
                "uniform_size": user.uniform_size,
                "category": user.category,
                "nickname": user.nickname,
                "address_full": user.address_full,
                "district": user.district,
                "city": user.city,
                "state": user.state,
                "team": user.team,
                "has_image": bool(user.data_img),
                "image_url": f"/users/{user.id}/profile-image" if user.data_img else None,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }

            result.append({
                "user": user_data,
                "registrations": registrations,
                "payments": payments,
                "terms": accepted_terms
            })

        return jsonify({
                "data": result,
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }), 200
        
    def update_user_full_info(self, user_id):
        data = request.get_json()

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # Campos atualizáveis
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        user.cpf = data.get("cpf", user.cpf)
        user.phone = data.get("phone", user.phone)
        user.birth_date = data.get("birth_date", user.birth_date)
        user.gender = data.get("gender", user.gender)
        user.uniform_size = data.get("uniform_size", user.uniform_size)
        user.category = data.get("category", user.category)
        user.nickname = data.get("nickname", user.nickname)
        user.address_full = data.get("address_full", user.address_full)
        user.district = data.get("district", user.district)
        user.city = data.get("city", user.city)
        user.state = data.get("state", user.state)
        user.team = data.get("team", user.team)

        db.session.commit()

        return jsonify({"message": "Dados do usuário atualizados com sucesso!"}), 200
    
    def delete_user(self, user_id):
        
        claims = get_jwt()
        if claims.get("role") not in ["admin", "organizer", "organizer-adm"]:
            return jsonify({"error": "Acesso negado"}), 403
        
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "Usuário deletado com sucesso!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Erro ao deletar usuário", "details": str(e)}), 500