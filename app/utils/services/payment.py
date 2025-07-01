from flask_restful import Resource, reqparse
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


import mercadopago
from datetime import datetime

# Inicialize o SDK com a sua chave
sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))

def gerar_pagamento_pix_para_cliente(user):
    """
    Gera pagamento Pix via Mercado Pago e retorna os dados do QR Code.
    """
    try:
        payment_data = {
            "transaction_amount": float(user.amount),
            "description": f"Pagamento inscrição evento {user.event_id}",
            "payment_method_id": "pix",
            "payer": {
                "email": user.email,
                "first_name": user.name
            }
        }

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        if payment_response["status"] in [200, 201]:
            return {
                "payment_id": payment["id"],
                "pix_qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
                "pix_qr_code_image_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                "pix_expiration": payment["date_of_expiration"]
            }, None
        else:
            return None, {
                "error": payment.get("message", "Erro ao gerar pagamento via Pix"),
                "details": payment.get("cause", [])
            }

    except Exception as e:
        return None, {
            "error": "Exceção ao gerar pagamento via Pix",
            "details": str(e)
        }
