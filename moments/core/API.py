from flask import jsonify, redirect, url_for, flash, abort, current_app
import requests
from flask_login import login_required, current_user
from .models import Photo
from . import db
import os

# Configuración de la API de Azure
AZURE_ENDPOINT = 'https://maestriayachay.cognitiveservices.azure.com/'
AZURE_SUBSCRIPTION_KEY = '2F54M87YQt6vNtfBKP1EUTIqByV71csVGSlb2mVQ37SZEapPwOu9JQQJ99BCACYeBjFXJ3w3AAAFACOG6XhS'

@app.route('/auto_description/<int:photo_id>', methods=['GET'])
@login_required
def auto_description(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)
    
    # Ruta de la imagen local
    image_path = os.path.join(current_app.root_path, 'static', 'uploads', photo.filename)
    
    # Llama a la API de Azure Computer Vision
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SUBSCRIPTION_KEY,
        'Content-Type': 'application/octet-stream'
    }
    
    with open(image_path, 'rb') as image_file:
        response = requests.post(AZURE_ENDPOINT, headers=headers, data=image_file)
    
    response.raise_for_status()
    analysis = response.json()
    
    # Obtiene la descripción de la respuesta
    description = analysis['description']['captions'][0]['text'] if analysis['description']['captions'] else 'No description available'
    
    # Actualiza la descripción de la foto
    photo.description = description
    db.session.commit()
    
    flash('Descripción actualizada automáticamente.', 'success')
    return redirect(url_for('.edit_description', photo_id=photo.id))