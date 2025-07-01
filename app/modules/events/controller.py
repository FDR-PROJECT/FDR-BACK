from datetime import datetime, time
from app.db.db import db
from app.db.models.event import Event

class EventsController:
    def create_event(self, data, organizer_id):
        event = Event(
            organizer_id=organizer_id,
            title=data['title'],
            description=data.get('description'),
            location=data.get('location'),
            date=datetime.combine(datetime.strptime(data['date'], '%Y-%m-%d').date(), time(12, 0)),
            end_date=datetime.combine(datetime.strptime(data['end_date'], '%Y-%m-%d').date(), time(12, 0)) if data.get('end_date') else None,
            image_url=data.get('image_url')
        )
        db.session.add(event)
        db.session.commit()
        return event

    def get_all_events(self):
        return Event.query.all()
    
    @staticmethod
    def get_event_by_id(event_id):
        return Event.query.get(event_id)

    def update_event(self, event_id, data):
        event = self.get_event_by_id(event_id)
        if not event:
            raise ValueError("Evento não encontrado")

        for key, value in data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        db.session.commit()
        return event

    def delete_event(self, event_id):
        event = self.get_event_by_id(event_id)
        if event:
            db.session.delete(event)
            db.session.commit()
        return True
