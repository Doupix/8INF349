from flask import Flask, abort, redirect, request, Response
import json
from src.Database import DB
from src.Errors import *

app = Flask(__name__)

'''
# ~~~ Exemple de manipulation de JSON ~~~
jsonVariable = '{"element": {"subElement1": 12,"subElement2": "plouf"}}'
jsonObj = json.loads(jsonVariable)
print(jsonObj["element"]["subElement1"])
'''

try:
	db = DB("stock.sql",{})
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
	data : dict = json.loads(request.data)
	try :
		orderId = db.editOrder(id, data)
		return redirect("/order/"+id)
	except MissingFieldsError | AlreadyPaidError | CardDeclinedError as ex:
		abort(Response(str(ex), 422))
	except NoFoundError:
		abort(404)
