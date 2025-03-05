import json
from urllib.error import HTTPError
from peewee import *
from playhouse.shortcuts import model_to_dict
from src.Errors import AlreadyPaidError, CardDeclinedError, MissingFieldsError, NoFoundError, OutOfInventoryError
import urllib.request


db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
	id = AutoField()
	name = CharField()
	description = TextField()
	price = FloatField()
	weight = IntegerField()
	in_stock = BooleanField()
	image = CharField()

class Customer(BaseModel):
	id = AutoField()
	email = CharField()
	country = CharField()
	address = CharField()
	postal_code = CharField()
	city = CharField()
	province = CharField()

class Payment(BaseModel):
	id = AutoField()
	transaction = CharField()
	amount_charged = FloatField()
	card_name = CharField()
	firstDigits = CharField()
	lastDigits = CharField()
	expirationYear = IntegerField()
	expirationMonth = IntegerField()

class Order(BaseModel):
	id = AutoField()
	product = IntegerField(null = True)
	customer = IntegerField(null = True)
	payment = CharField(null = True)
	quantity = IntegerField()

# Classe gestion BDD
class DB:
	def __init__(self, path : str, products : dict):
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
	def getDB(self):
		return db

	# Retourner liste produits
	def queryProducts(self) -> dict:
		return {"products": [model_to_dict(product) for product in Product.select()]}

	# Creer une commande
	def registeryOrder(self, order) -> int:
		try:
			product_id = order["product"]["id"]
			quantity = order["product"]["quantity"]

			if quantity < 1:
				raise MissingFieldsError("La création d'une commande nécessite un produit")

			product = Product.get_or_none(Product.id == product_id)

			if not product.in_stock or not product:
				raise OutOfInventoryError()

			new_order = Order.create(
				product=product,
				quantity=quantity
			)
			return new_order.id

		except KeyError:
			raise MissingFieldsError("La création d'une commande nécessite un produit")

	# Recupérer une commande
	# TODO
	def queryOrder(self, id : int) -> dict:
		try :
			order : Order = Order.get(Order.id == id)
		except DoesNotExist:
			raise NoFoundError()
		product = Product.get(order.product == Product.id)
		price = self.calculPrice(id)
		data = {
			"order" : {
				"id" : order.id,
				"total_price" : price["total_price"],
				"total_price_tax" : None,
				"email" : None,
				"credit_card":{},
				"shipping_information" : {},
				"paid": False,
				"transaction": {},
				"product" : {
					"id" : order.product,
					"quantity" : order.quantity
				},
				"shipping_price" : price["shipping_price"],
			}
		}

		customer : Customer = Customer.get_or_none(order.customer == Customer.id)
		if customer:
			data["order"].update(
				{
					"shipping_information" : {
						"country" : customer.country,
						"address" : customer.address,
						"postal_code" : customer.postal_code,
						"city" : customer.city,
						"province" : customer.province
					},
					"email" : customer.email,
					"total_price_tax" : price["total_price_tax"],
				}
			)

		payment : Payment = Payment.get_or_none(order.payment == Payment.transaction)
		if payment:
			data["order"].update(
				{
					"credit_card" : {
						"name" : payment.card_name,
						"first_digits" :payment.firstDigits,
						"last_digits": payment.lastDigits,
						"expiration_year" : payment.expirationYear,
						"expiration_month" : payment.expirationMonth
					},
					"transaction": {
						"id": payment.transaction,
						"success": True,
						"amount_charged": payment.amount_charged
					},
					"paid": True,
				}
			)

		return data

	def editCustomer(self, id : int, data : dict) -> None:
		order = data["order"]
		try :
			orderInfo : Order = Order.get(Order.id == id)
			if not all(field in order for field in ["email", "shipping_information"]):
					raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")

			if not all(field in order["shipping_information"] for field in ["country", "address", "postal_code", "city", "province"]):
				raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")
			shippingInfo = order["shipping_information"]
			customer = Customer(
				email = order["email"],
				country = shippingInfo["country"],
				address = shippingInfo["address"],
				postal_code = shippingInfo["postal_code"],
				city = shippingInfo["city"],
				province = shippingInfo["province"]
			)
			customer.save()
			orderInfo.customer = customer.id
			orderInfo.save()

		except DoesNotExist:
			raise NoFoundError()

	def calculPrice(self, id : int) -> dict :
		order = Order.get(Order.id == id)
		product = Product.get(order.product == Product.id)
		total_price = product.price * order.quantity
		shipping_price = 5 if product.weight * order.quantity <= 500 else \
						 10 if product.weight * order.quantity < 2000 else 25
		price = {"total_price" : total_price , "shipping_price": shipping_price}
		customer = Customer.get_or_none(order.customer == Customer.id)
		if customer:
			match customer.province :
				case "QC":
					total_price_tax = 1.15 * total_price
				case "ON":
					total_price_tax = 1.13 * total_price
				case "AB":
					total_price_tax = 1.05 * total_price
				case "BC":
					total_price_tax = 1.12 * total_price
				case "NS":
					total_price_tax = 1.14 * total_price
				case _:
					total_price_tax = 1.15 * total_price
			price.update({"total_price_tax" : total_price_tax, "amount_charged":total_price+shipping_price})
		return price

	def httpPOST(self, url : str, data : dict) -> dict:
		req = urllib.request.Request(url)
		req.add_header('Content-Type', 'application/json; charset=utf-8')
		try:
			response = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'))
		except HTTPError as ex:
			if ex.code==422:
				return json.loads(ex.read())
			else:
				raise ex
		else:
			return json.loads(response.read())



	def pay(self, id : int, data : dict) -> dict:
		request : dict = {"amount_charged" : self.calculPrice(id)["amount_charged"]}
		request.update(data)
		response = self.httpPOST("https://dimensweb.uqac.ca/~jgnault/shops/pay/", request)
		return response

	def editCard(self, id : int, data : dict) -> None:
		creditCard = data["credit_card"]
		if not all(field in creditCard for field in ["name", "number", "expiration_year", "cvv", "expiration_month"]):
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")

		orderInfo : Order = Order.get(Order.id == id)
		if orderInfo.payment != None:
			raise AlreadyPaidError
		if orderInfo.customer == None:
			raise MissingFieldsError("Les informations du client sont nécessaire avant d'appliquer une carte de crédit")

		response = self.pay(id, data)
		if response.get("errors"):
			raise CardDeclinedError()
		else :
			card = response["credit_card"]
			transaction = response["transaction"]
			payment = Payment(
				transaction = transaction["id"],
				amount_charged = transaction["amount_charged"],
				card_name = card["name"],
				firstDigits = card["first_digits"],
				lastDigits = card["last_digits"],
				expirationYear = card["expiration_year"],
				expirationMonth = card["expiration_month"]
			)

			payment.save()
			orderInfo.payment = payment.transaction
			orderInfo.save()
