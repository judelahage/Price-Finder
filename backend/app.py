import subprocess
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'

db = SQLAlchemy(app)

#setting up database
class ProductResult(db.Model):
    id = db.Column()
    name = db.Column(db.String(1000))
    img = db.Column(db.String(1000))
    url = db.Column(db.String(1000))
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    search_text = db.Column(db.String(255))
    source = db.Column(db.String(255))
    
    def init(self, name, img, url, price, search_text, source):
        self.name = name
        self.url = url
        self.img = img
        self.price = price
        self.search_text = search_text
        self.source = source

class TrackedProducts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tracked = db.Column(db.Boolean, default = True)
    
    def init(self, name, tracked = True):
        self.name = name
        self.tracked = tracked

#send post request to results
@app.route('/results', methods=['POST'])
def submitResults():
    results = request.json.get('data')
    search_text = request.json.get('search_text')
    source = request.json.get('source')

    for result in results:
        product_result = ProductResult(
            name = result['name']
            url = result['url']
            img = result['img']
            price = result['price']
            search_text = search_text
            source = source
        )
        db.session.add(product_result)
        
    db.session.commit()
    return jsonify({'message': 'Received Data Successfully'}), 200