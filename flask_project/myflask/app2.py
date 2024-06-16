from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import firebase_admin
from firebase_admin import credentials, firestore, storage
import csv
import requests
import os
import cv2
import base64
from datetime import timedelta

# Firebase 설정
cred = credentials.Certificate('factory-info-a8045-firebase-adminsdk-e52rt-53ce709c19.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'factory-info-a8045.appspot.com'})
firestore_db = firestore.client()
bucket = storage.bucket()

# Flask 설정
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'images'
app.secret_key = 'your_secret_key'

# SQLAlchemy 설정
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class YourModel(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    qc = db.Column(db.String(20), nullable=False)
    img = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"YourModel(id={self.id}, qc={self.qc}, img={self.img}, date_added={self.date_added})"

# 데이터베이스 초기화 및 동기화 함수
def initialize_database():
    with app.app_context():
        db.create_all()
        sync_firestore_to_db()
        download_all_images_from_bucket(app.config['UPLOAD_FOLDER'])

def sync_firestore_to_db():
    docs = firestore_db.collection('factory_info').stream()
    for doc in docs:
        data = doc.to_dict()
        entry = YourModel(
            id=doc.id,
            qc=data.get('QC'),
            img=data.get('img')
        )
        db.session.merge(entry)
    db.session.commit()

# 이미지 다운로드 함수
def download_image(url, local_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image downloaded and saved to {local_path}")
    else:
        print("Failed to download the image")

# 모든 이미지 다운로드 함수
def download_all_images_from_bucket(local_dir):
    blobs = bucket.list_blobs(prefix='images/')
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    for blob in blobs:
        if blob.name.endswith('/'):
            continue
        print(f"Processing {blob.name}")
        public_url = blob.public_url
        local_path = os.path.join(local_dir, os.path.basename(blob.name))
        download_image(public_url, local_path)

# Flask 애플리케이션 라우트
@app.route('/')
def index():
    data = YourModel.query.all()
    return render_template('index2.html', data=data)

@app.route('/api/get_data/')
def get_data():
    data = YourModel.query.all()
    return jsonify([{'id': entry.id, 'qc': entry.qc, 'img': entry.img, 'date_added': entry.date_added} for entry in data])

@app.route('/api/upload_image/', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)
        # 이미지 업로드 후 Firestore에 URL 저장
        blob = bucket.blob(f'images/{filename}')
        blob.upload_from_filename(local_path)
        blob.make_public()
        public_url = blob.public_url
        return jsonify({'filename': public_url}), 200

    return jsonify({'error': 'Failed to upload image'}), 500

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
