from flask import Flask, abort, redirect, request, Response
import json
import urllib.request

from peewee import SqliteDatabase
from src.errors import *
from src.store import Store, localStore
import click
from src.models import db, Product, Customer, Payment, Order
app = Flask(__name__)
'''
# ~~~ Exemple de manipulation de JSON ~~~
jsonVariable = '{"element": {"subElement1": 12,"subElement2": "plouf"}}'
jsonObj = json.loads(jsonVariable)
print(jsonObj["element"]["subElement1"])
'''




@click.command('init-db')
def init_db_command():
	init_db("database.sqlite", products = json.loads(urllib.request.urlopen("https://dimensweb.uqac.ca/~jgnault/shops/products/").read()))

app.cli.add_command(init_db_command)

def init_db(path : str, products : dict):

	db.init(path)
	db.connect()
	db.create_tables([Product, Customer, Payment, Order], safe=True)
	for p in products.get("products", []):
		Product.get_or_create(
			id=p["id"],
			name=p["name"],
			description=p["description"],
			price=p["price"],
			weight=p["weight"],
			in_stock=p["in_stock"],
			image=p["image"]
		)


database = localStore()

@app.get('/')
def listProducts():
	return database.queryProducts()


@app.post('/order')
def newOrder():
	# Crée une commande
	order = json.loads(request.data)
	try :
		id = Store().registeryOrder(order)
		return redirect("/order/"+str(id))
	except MissingFieldsError | OutOfInventoryError as ex:
		abort(Response(str(ex), 422))


@app.get('/order/<int:id>')
def getOrder(id):
	# Retourne une commande
	try :
		return Store().queryOrder(int(id))
	except NoFoundError:
		abort(404)


@app.put('/order/<int:id>')
def editOrder(id):
	# Edite une commande (carte de crédit, coordonnées client, etc...)
	data : dict = json.loads(request.data)
	try :
		if data.get("order"):
			Store().editCustomer(id, data)
		elif data.get("credit_card"):
			Store().editCard(id, data)
		else:
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")
	except (MissingFieldsError, AlreadyPaidError, CardDeclinedError) as ex:
		abort(Response(str(ex) , 422))
	except NoFoundError:
		abort(404)
	else :
		return redirect("/order/"+str(id))
