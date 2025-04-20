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
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    searchText = db.Column(db.String(255))
    source = db.Column(db.String(255))
    
    def init(self, name, img, url, price, searchText, source):
        self.name = name
        self.url = url
        self.img = img
        self.price = price
        self.searchText = searchText
        self.source = source

class TrackedProducts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(1000))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    tracked = db.Column(db.Boolean, default = True)
    
    def init(self, name, tracked = True):
        self.name = name
        self.tracked = tracked

#send post request to results, submits results, then gets added to database
@app.route('/results', methods=['POST'])
def submitResults():
    results = request.json.get('data')
    searchText = request.json.get('searchText')
    source = request.json.get('source')

    for result in results:
        productResult = ProductResult(
            name = result['name'],
            url = result['url'],
            img = result['img'],
            price = result['price'],
            searchText = searchText,
            source = source)
        
        db.session.add(productResult)
        
    db.session.commit()
    return jsonify({'message': 'Received Data Successfully'}), 200


@app.route('/uniqueSearchTexts', methods=['GET']) #gives all the unique searches for product names
def getUniqueSearchTexts():
    uniqueSearchTexts = db.session.query(ProductResult.search_text).distinct().all()
    uniqueSearchTexts = [text[0] for text in uniqueSearchTexts]
    return jsonify(uniqueSearchTexts)


@app.route('/results') #gets all the results for a specific product name
def getProductResults():
    searchText = request.args.get('searchText')
    results = ProductResult.query.filter_by(searchText = searchText).order_by(ProductResult.createdAt.desc()).all()
    
    productDict = {}
    for result in results:
        url = result.url
        if url not in productDict:
            productDict[url] = {
                'name' : result.name,
                'url' : result.url,
                'img' : result.img,
                'source' : result.source,
                'createdAt' : result.createdAt,
                'priceHistory': []
            }
            
        productDict[url]['priceHistory'].append({
            'price' : result.price,
            'date' : result.createdAt
        })
        
    return jsonify(list(productDict.values()))

@app.route('/allResults', methods=['GET']) #gets all results for all products in our database
def getResults():
    results = ProductResult.query.all()
    productResults = []
    for result in results:
        productResults.append({
            'name' : result.name,
            'url' : result.url,
            'img' : result.img,
            'date' : result.date
            'source' : result.source,
            'createdAt' : result.createdAt,
            'searchText': result.searchText
        })
    
    return jsonify(productResults)

@app.route('/startScraper', methods=['POST']) #starts web scraper based on the url
def startScraper():
    url = request.json.get('url')
    searchText = request.json.get('searchText')
    
    command = f"python ./scraper/init.py {url} \"{searchText}\" /results"
    subprocess.Popen(command, shell=True)
    
    return jsonify({'message': 'Scraper started successfully'}), 200

@app.route('-add-tracked-product', methods = ['POST']) #adds tracked product
def add_tracked_product():
    name = request.json.get('name')
    trackedProduct = TrackedProducts(name = name);
    db.session.add(trackedProduct);
    db.session.commit()
    
    return jsonify({'message': 'Tracked product added successfully'}), 200

@app.route('/tracked-product/<int:product_id>', methods = ['PUT']) #toggling tracking and untracking
def toggleTrackedProduct(productId):
    trackedProduct = TrackedProducts.query.get(productId)
    if trackedProduct is None:
        return jsonify({'message': 'Tracked product not found'}), 404
    
    trackedProduct.tracked = not trackedProduct.tracked
    db.session.commit()
    
    return jsonify({'message': 'Tracked product tracked successfully'}), 200


    
    