from flask import Flask, abort, redirect, request, Response, send_from_directory
import json
import urllib.request

from peewee import SqliteDatabase
from src.errors import *
from src.store import Store
import click, database, redis
from src.models import db, Product, Customer, Payment, Order
import os

app = Flask(__name__)
app.cli.add_command(database.init_db_command)


storage = Store(
	os.environ.get("DB_NAME"),
	os.environ.get("DB_HOST"),
	os.environ.get("DB_PORT"),
	os.environ.get("DB_USER"),
	os.environ.get("DB_PASSWORD"))

r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)

@app.get('/')
def listProducts():
	return storage.queryProducts()

@app.post('/order')
def newOrder():
	# Crée une commande
	order = json.loads(request.data)
	try :
		if order.get("products"):
			id = storage.registeryOrder(list(order["products"]))
		elif order.get("product"):
			id = storage.registeryLegacyOrder(order["product"])
		else:
			raise MissingFieldsError("La création d'une commande nécessite un produit")

		return redirect("/order/"+str(id))
	except (MissingFieldsError, OutOfInventoryError) as ex:
		abort(Response(str(ex), 422))

@app.get('/order/<int:id>')
def getOrder(id):
	cached = str(r.get(str(id)))
	if cached :
		return cached
	try :
		return storage.queryOrder(int(id))
	except NoFoundError:
		abort(404)

@app.put('/order/<int:id>')
def editOrder(id):
	# Edite une commande (carte de crédit, coordonnées client, etc...)
	data : dict = json.loads(request.data)
	try :
		if data.get("order"):
			storage.editCustomer(id, data)
		elif data.get("credit_card"):
			storage.editCard(id, data)
			r.set(str(id), str(storage.queryOrder(id)))
		else:
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")
	except (MissingFieldsError, AlreadyPaidError, CardDeclinedError) as ex:
		abort(Response(str(ex) , 422))
	except NoFoundError:
		abort(404)
	else :
		return {"message": "Commande complétée", "id": id}, 200

@app.route('/home')
def serve_home():
    return send_from_directory('home', 'index.html')

@app.route('/home/<path:filename>')
def serve_static_file(filename):
    return send_from_directory('home', filename)