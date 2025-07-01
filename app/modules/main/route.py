import io
from flask import Blueprint, request, send_file
from sqlalchemy.orm import joinedload
from app.db.db import db
from app.db.models.payment import Payment
from app.db.models.registration import Registration
from app.db.models.event import Event
from openpyxl import Workbook
from .controller import MainController

main_bp = Blueprint('main', __name__)
main_controller = MainController()

@main_bp.route("/export/excel", methods=["GET"])
def export_registrations_excel():
    event_id = request.args.get("event_id", type=int)
    category_id = request.args.get("category_id", type=int)

    if not event_id:
        return {"error": "Parâmetro 'event_id' é obrigatório."}, 400

    file_stream, filename = main_controller.generate_excel(event_id, category_id)
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
