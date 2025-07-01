import unittest
import json

from app.modules.auth.controller import AuthController


def test_index():
    auth_controller = AuthController()
    result = auth_controller.index()
    assert result == {'message': 'Hello, World!'}
