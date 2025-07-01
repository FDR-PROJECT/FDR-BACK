import unittest
import json

from app.modules.registrations.controller import RegistrationsController


def test_index():
    registrations_controller = RegistrationsController()
    result = registrations_controller.index()
    assert result == {'message': 'Hello, World!'}
