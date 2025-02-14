from flask import Flask, abort, redirect, request, Response
import json
from src.Database import *
from src.Errors import *

app = Flask(__name__)

'''
# ~~~ Exemple de manipulation de JSON ~~~
jsonVariable = '{"element": {"subElement1": 12,"subElement2": "plouf"}}'
jsonObj = json.loads(jsonVariable)
print(jsonObj["element"]["subElement1"])
'''

db = FakeDB()

@app.get('/')
def listProducts():
	return db.queryProducts()


@app.post('/order')
def newOrder():
	# Crée une commande
	order = json.loads(request.data)
	try :
		db.registryOrder(order)
		return redirect("/order/"+order["product"]["id"])
	except MissingFieldsError | OutOfInventoryError as ex:
		abort(Response(str(ex), 422))


@app.get('/orders/<int:id>')
def getOrder(id):
	# Retourne une commande
	try :
		return db.queryOrder(id)
	except NoFoundError:
		abort(404)


@app.put('/orders/<int:id>')
def editOrder(id):
	# Edite une commande (carte de crédit, coordonnées client, etc...)
	data = json.loads(request.data)
	try :
		db.editOrder(id, data)
		return redirect("/order/"+data["product"]["id"])
	except MissingFieldsError | AlreadyPaidError | CardDeclinedError as ex:
		abort(Response(str(ex), 422))
	except NoFoundError:
		abort(404)
