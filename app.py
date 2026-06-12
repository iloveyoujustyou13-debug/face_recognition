import os
import numpy as np
from flask import Flask, request, jsonify, render_template
import face_recognition

app = Flask(__name__)

# Folder path setup
UPLOAD_FOLDER = 'static/group_photos'
TEMP_FOLDER = 'static/temp_selfies'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

# 1. Group Photos Upload Endpoint
@app.route('/upload_group', methods=['POST'])
def upload_group():
    if 'photos' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    files = request.files.getlist('photos')
    for file in files:
        if file.filename != '':
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            
    return jsonify({"message": f"Successfully uploaded {len(files)} group photos!"})

# 2. Selfie Match & Search Endpoint
@app.route('/search_by_selfie', methods=['POST'])
def search_by_selfie():
    if 'selfie' not in request.files:
        return jsonify({"error": "No selfie uploaded"}), 400
        
    selfie_file = request.files['selfie']
    if selfie_file.filename == '':
        return jsonify({"error": "Empty file"}), 400
        
    # Selfie save and load
    selfie_path = os.path.join(TEMP_FOLDER, 'current_selfie.jpg')
    selfie_file.save(selfie_path)
    
    try:
        # Selfie-r face encoding ber kora
        selfie_image = face_recognition.load_image_file(selfie_path)
        selfie_encodings = face_recognition.face_encodings(selfie_image)
        
        if not selfie_encodings:
            return jsonify({"error": "Selfie-te kono mukh khunje paoya jayni!"}), 400
            
        target_encoding = selfie_encodings[0]
        matched_photos = []
        
        # Group photos folder scan kora
        for group_photo_name in os.listdir(UPLOAD_FOLDER):
            group_photo_path = os.path.join(UPLOAD_FOLDER, group_photo_name)
            
            # Group photo load kora
            group_image = face_recognition.load_image_file(group_photo_path)
            # Chobir shob mukh khunje ber kora
            group_encodings = face_recognition.face_encodings(group_image)
            
            # Check kora selfie-r sathe kono mukh match korche kina
            matches = face_recognition.compare_faces(group_encodings, target_encoding, tolerance=0.6)
            
            if True in matches:
                # Match eche, tai path list-e add kora holo
                matched_photos.append(f"/static/group_photos/{group_photo_name}")
                
        return jsonify({"matched_photos": matched_photos})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
  
