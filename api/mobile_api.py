# Мобильное API для Dental Academy
# Вставьте сюда код мобильного API

from flask import Blueprint, jsonify, request
# from app.models import User, Lesson, Test

mobile_api = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# Вставьте сюда API эндпоинты 