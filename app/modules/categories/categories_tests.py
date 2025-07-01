import unittest
import json

from app.modules.categories.controller import CategoriesController


def test_index():
    categories_controller = CategoriesController()
    result = categories_controller.index()
    assert result == {'message': 'Hello, World!'}
