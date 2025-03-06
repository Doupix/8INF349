from flask import Flask, abort, redirect, request, Response
import json
import urllib.request
from src.errors import *
from src.store import Store

app = Flask(__name__)


'''
# ~~~ Exemple de manipulation de JSON ~~~
jsonVariable = '{"element": {"subElement1": 12,"subElement2": "plouf"}}'
jsonObj = json.loads(jsonVariable)
print(jsonObj["element"]["subElement1"])
'''

try:
	products = json.loads(urllib.request.urlopen("http://dimensweb.uqac.ca/~jgnault/shops/products/").read())
	db = Store("stock.sql", products)
except :
	exit()

@app.get('/')
def listProducts():
	return db.queryProducts()


@app.post('/order')
def newOrder():
	# Crée une commande
	order = json.loads(request.data)
	try :
		id = db.registeryOrder(order)
		return redirect("/order/"+str(id))
	except MissingFieldsError | OutOfInventoryError as ex:
		abort(Response(str(ex), 422))


@app.get('/order/<int:id>')
def getOrder(id):
	# Retourne une commande
	try :
		return db.queryOrder(int(id))
	except NoFoundError:
		abort(404)


@app.put('/order/<int:id>')
def editOrder(id):
	# Edite une commande (carte de crédit, coordonnées client, etc...)
	data : dict = json.loads(request.data)
	try :
		if data.get("order"):
			db.editCustomer(id, data)
		elif data.get("credit_card"):
			db.editCard(id, data)
		else:
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")
	except (MissingFieldsError, AlreadyPaidError, CardDeclinedError) as ex:
		abort(Response(str(ex) , 422))
	except NoFoundError:
		abort(404)
	else :
		return redirect("/order/"+str(id))
