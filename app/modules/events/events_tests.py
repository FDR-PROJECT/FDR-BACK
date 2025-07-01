import unittest
import json

from app.modules.events.controller import EventsController


def test_index():
    events_controller = EventsController()
    result = events_controller.index()
    assert result == {'message': 'Hello, World!'}
