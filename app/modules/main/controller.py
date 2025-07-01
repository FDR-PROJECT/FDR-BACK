import io
from openpyxl import Workbook
from sqlalchemy.orm import joinedload
from app.db.db import db
from app.db.models.payment import Payment
from app.db.models.registration import Registration
from app.db.models.event import Event

class MainController:
    def generate_excel(self, event_id, category_id=None):
        query = (
            db.session.query(Registration)
            .options(
                joinedload(Registration.athlete),
                joinedload(Registration.partner),
                joinedload(Registration.category),
                joinedload(Registration.event),
            )
            .filter(Registration.event_id == event_id)
        )

        if category_id:
            query = query.filter(Registration.category_id == category_id)

        registrations = query.all()
        event = db.session.query(Event).filter_by(id=event_id).first()

        wb = Workbook()
        ws = wb.active
        ws.title = "Inscrições"

        headers = [
            "Evento", "Categoria",
            "Nome Atleta", "CPF Atleta", "E-mail Atleta", "Telefone Atleta", "Apelido Atleta", "Nascimento Atleta",
            "Gênero Atleta", "Tam. Uniforme Atleta", "Time Atleta", "Endereço Atleta", "Bairro Atleta", "Cidade Atleta", "Estado Atleta",
            "Nome Parceiro", "CPF Parceiro", "E-mail Parceiro", "Telefone Parceiro", "Apelido Parceiro", "Nascimento Parceiro",
            "Gênero Parceiro", "Tam. Uniforme Parceiro", "Time Parceiro", "Endereço Parceiro", "Bairro Parceiro", "Cidade Parceiro", "Status Pagamento", "Cupom Usado"
        ]
        ws.append(headers)

        for reg in registrations:
            athlete = reg.athlete
            partner = reg.partner
            category = reg.category
            
            payment = db.session.query(Payment).filter_by(
                user_id=athlete.id,
                event_id=reg.event_id,
                category_id=reg.category_id
            ).first()

            ws.append([
                event.title if event else "",
                category.name if category else "",

                athlete.name, athlete.cpf, athlete.email, athlete.phone, athlete.nickname, str(athlete.birth_date or ""),
                athlete.gender, athlete.uniform_size, athlete.team, athlete.address_full,
                athlete.district, athlete.city, athlete.state,

                partner.name if partner else "",
                partner.cpf if partner else "",
                partner.email if partner else "",
                partner.phone if partner else "",
                partner.nickname if partner else "",
                str(partner.birth_date or "") if partner else "",
                partner.gender if partner else "",
                partner.uniform_size if partner else "",
                partner.team if partner else "",
                partner.address_full if partner else "",
                partner.district if partner else "",
                partner.city if partner else "",
                payment.status if payment else "NÃO ENCONTRADO",
                payment.coupon.code if payment and payment.coupon else "—"
            ])

        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        filename = f"inscricoes_{event.title.replace(' ', '_')}.xlsx" if event else "inscricoes.xlsx"
        return file_stream, filename
