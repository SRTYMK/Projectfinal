from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
from flask_pymongo import PyMongo
import pyscrypt
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# ตั้งค่าเชื่อมต่อกับ MongoDB
app.config["MONGO_URI"] = "mongodb+srv://saruttaya:1234@shop-news.fjh15tu.mongodb.net/mydata?retryWrites=true&w=majority&appName=shop-news"
mongo = PyMongo(app)

# เลือกหรือสร้างคอลเลคชัน
users_collection = mongo.db.shop_data
product_collection = mongo.db.product

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data["username"]
    email = data["email"]
    password = generate_password_hash(data["password"])

    try:
        users_collection.insert_one({"username": username, "email": email, "password": password})
        return jsonify({"message": "User registered successfully", "redirect": "/login"})
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to register user: {str(e)}"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    try:
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            return jsonify({"message": "Login successful", "user_id": str(user["_id"])})
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to login: {str(e)}"}), 500

@app.route("/scrypt", methods=["POST"])
def scrypt_hash():
    data = request.get_json()
    password = data["password"].encode("utf-8")
    salt = data["salt"].encode("utf-8")

    try:
        key = pyscrypt.hash(password, salt, N=1024, r=1, p=1, dkLen=32)
        return jsonify({"key": key.hex()})
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to generate scrypt hash: {str(e)}"}), 500

@app.route("/add-product", methods=["POST"])
def add_product():
    data = request.get_json()
    name = data["name"]
    type = data["type"]
    price = data["price"]
    index = data.get("index", None)
    image = data.get("image", "")
    stores = data.get("stores", [])

    try:
        product = {"name": name, "type": type, "price": price, "image": image, "stores": stores}
        if index is not None:
            product["index"] = index

        product_collection.insert_one(product)
        return jsonify({"message": "Product added successfully"})
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to add product: {str(e)}"}), 500

@app.route("/search", methods=["GET"])
def search_products():
    search_term = request.args.get("q", "")
    try:
        products = product_collection.find({"name": {"$regex": search_term, "$options": "i"}})
        products_list = [
            {
                "_id": str(product["_id"]),
                "name": product["name"],
                "type": product.get("type", ""),
                "price": product["price"],
                "index": product.get("index", ""),  # ใช้ .get เพื่อป้องกัน KeyError
                "image": product.get("image", ""),
                "stores": product.get("stores", [])
            }
            for product in products
        ]
        return jsonify(products_list)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to search products: {str(e)}"}), 500

@app.route("/product/<product_id>", methods=["GET"])
def get_product(product_id):
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({"message": "Invalid product ID"}), 400

        product = product_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            product["_id"] = str(product["_id"])
            return jsonify(product)
        else:
            return jsonify({"message": "Product not found"}), 404 
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    result = product_collection.update_one({'index': product_id}, {'$set': data})

    if result.matched_count > 0:
        return jsonify({'message': 'Product updated successfully'}), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route("/seedType/<type>", methods=["GET"])
def get_seed_type(type):
    try:
        seeds = product_collection.find({"type": type})
        seeds_list = [
            {
                "name": seed.get("name", ""),
                "type": seed.get("type", ""),
                "price": seed.get("price", 0.0),
                "index": seed.get("index", 0),
                "image": seed.get("image", ""),
                "stores": [
                    {
                        "name": store.get("name", ""),
                        "url": store.get("url", ""),
                        "price": store.get("price", 0.0)
                    }
                    for store in seed.get("stores", [])
                ]
            }
            for seed in seeds
        ]
        return jsonify(seeds_list)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to fetch seeds: {str(e)}"}), 500

# Endpoint สำหรับดึงข้อมูลโปรไฟล์ผู้ใช้
@app.route("/user/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            return jsonify(user)
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Endpoint สำหรับอัปเดตข้อมูลโปรไฟล์ผู้ใช้
@app.route("/user/<user_id>", methods=["PUT"])
def update_user_profile(user_id):
    data = request.json
    try:
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        if result.matched_count > 0:
            return jsonify({"message": "User profile updated successfully"})
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to update user profile: {str(e)}"}), 500

@app.route("/product-view", methods=["POST"])
def product_view():
    data = request.get_json()
    user_id = data["user_id"]
    product_id = data["product_id"]
    product_name = data["product_name"]
    product_image = data["product_image"]
    product_price = data["product_price"]

    try:
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$push": {
                    "productHistory": {
                        "product_id": product_id,
                        "name": product_name,
                        "imageUrl": product_image,
                        "price": product_price
                    }
                }
            }
        )
        return jsonify({"message": "Product view recorded successfully"})
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to record product view: {str(e)}"}), 500

@app.route('/data', methods=['GET'])
def get_data():
    data = mongo.db.mydata.find()
    data_list = []
    for item in data:
        item['_id'] = str(item['_id'])
        data_list.append(item)
    return jsonify(data_list)

@app.route("/test-connection", methods=["GET"])
def test_connection():
    try:
        mongo.db.command("ping")
        return jsonify({"message": "Connection successful"})
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Failed to connect: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
