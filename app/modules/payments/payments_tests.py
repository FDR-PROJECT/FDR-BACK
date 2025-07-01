import unittest
import json

from app.modules.payments.controller import PaymentsController


def test_index():
    payments_controller = PaymentsController()
    result = payments_controller.index()
    assert result == {'message': 'Hello, World!'}
