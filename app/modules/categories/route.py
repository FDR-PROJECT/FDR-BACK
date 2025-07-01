from flask import Blueprint, request, jsonify
from .controller import CategoriesController


categories_bp = Blueprint('categories', __name__)
categories_controller = CategoriesController()
@categories_bp.route('/<int:event_id>', methods=['POST'])
def create(event_id):
    data = request.json
    category = categories_controller.create_category(data, event_id)
    return jsonify(category.id), 201

@categories_bp.route('/<int:event_id>', methods=['GET'])
def list_by_event(event_id):
    categories = categories_controller.get_categories_by_event(event_id)
    return jsonify(categories)


@categories_bp.route('/grouped', methods=['GET'])
def list_grouped():
    grouped = categories_controller.get_all_categories_grouped_by_event()
    return jsonify(grouped), 200


@categories_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.json
    updated = categories_controller.update_category(category_id, data)
    if updated:
        return jsonify({"message": "Categoria atualizada com sucesso"}), 200
    else:
        return jsonify({"error": "Categoria não encontrada"}), 404
    
