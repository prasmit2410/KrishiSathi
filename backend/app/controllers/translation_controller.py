from flask import Blueprint, request, jsonify

from backend.app.services.translation_service import TranslationService

translation_controller = Blueprint('translation_controller', __name__)

@translation_controller.route('/api/v1/translate', methods=['POST'])
def translate_text():
    """Translate given text to target language (hi, mr, en)."""
    data = request.get_json(force=True) or {}
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'en')
    result = TranslationService.translate(text, target_lang)
    return jsonify({
        'translated': result.get('translated', ''),
        'model': result.get('model'),
        'tokens': result.get('tokens')
    })
