#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS 
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET', 'POST'])
def all_restaurants():
    if request.method == "GET":
        return jsonify([r.to_dict() for r in Restaurant.query.all()]), 200
    elif request.method == "POST":
        data = request.get_json()
        try:
            new_restaurant = Restaurant(
                name=data.get("name"),
                address=data.get("address")
            )
            db.session.add(new_restaurant)
            db.session.commit()
            return jsonify(new_restaurant.to_dict()), 201
        except ValueError:
            return jsonify({"error": ["validation errors"]}), 400
        

@app.route('/restaurants/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def restaurant_detail(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404

    if request.method == "GET":
        restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
        restaurant_pizzas_data = [
            {
                "id": rp.id,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "price": rp.price,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            }
            for rp in restaurant_pizzas
        ]
        response_data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": restaurant_pizzas_data
        }
        return jsonify(response_data), 200
      
    elif request.method == "PATCH":
        data = request.get_json()
        try:
            if "name" in data:
                restaurant.name = data["name"]
            if "address" in data:
                restaurant.address = data["address"]
            db.session.commit()
            return jsonify(restaurant.to_dict()), 200
        except ValueError:
            return {'error': ['validation errors']}, 200

    elif request.method == "DELETE":
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

@app.route('/pizzas', methods=['GET'])
def all_pizzas():
    return jsonify([p.to_dict() for p in Pizza.query.all()]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data.get("price"),
            pizza_id=data.get("pizza_id"),
            restaurant_id=data.get("restaurant_id")
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
