
from app.db.db import db
from app.db.models.category import Category
from app.db.models.event import Event
from app.db.models.registration import Registration


class CategoriesController:
    def create_category(self, data, event_id):

        category = Category(
            event_id=event_id,
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            participant_limit=data.get('participant_limit'),
            
        )
        db.session.add(category)
        db.session.commit()
        return category

    def get_categories_by_event(self, event_id):
        categories = Category.query.filter_by(event_id=event_id).all()
        result = []
        for c in categories:
            total_duplas = Registration.query.filter_by(category_id=c.id).count()
            vagas_restantes = max(0, c.participant_limit - total_duplas) if c.participant_limit else None

            result.append({
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "price": float(c.price),
                "participant_limit": c.participant_limit,
                "vagas_restantes": vagas_restantes,
                
            })
        return result
    
    def get_all_categories_grouped_by_event(self):
        events = Event.query.all()
        result = []

        for event in events:
            categories = Category.query.filter_by(event_id=event.id).all()
            category_list = []

            for cat in categories:
                total_duplas = Registration.query.filter_by(category_id=cat.id).count()
                vagas_restantes = max(0, cat.participant_limit - total_duplas) if cat.participant_limit is not None else None

                category_list.append({
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description,
                    "price": float(cat.price),
                    "participant_limit": cat.participant_limit,
                    "inscritos": total_duplas,
                    "vagas_restantes": vagas_restantes,
                    
                })

            result.append({
                "event_id": event.id,
                "title": event.title,
                "location": event.location,
                "categories": category_list
            })

        return result
    
    def update_category(self, category_id, data):
        category = Category.query.get(category_id)
        if not category:
            return None

        
        category.description = data.get('description', category.description)
        category.price = data.get('price', category.price)
        category.participant_limit = data.get('participant_limit', category.participant_limit)
        
        

        db.session.commit()
        return category
    
    def delete_category(self, category_id):
        category = Category.query.get(category_id)

        if not category:
            return False, "Categoria não encontrada."

        # Verifica se tem inscrições vinculadas
        registrations = Registration.query.filter_by(category_id=category_id).first()
        if registrations:
            return False, "Não é possível deletar categorias com inscrições vinculadas."

        db.session.delete(category)
        db.session.commit()
        return True, "Categoria deletada com sucesso."






