from itertools import product
import json
from urllib.error import HTTPError

from peewee import *
from playhouse.shortcuts import model_to_dict
from playhouse.db_url import connect
from src.errors import AlreadyPaidError, CardDeclinedError, MissingFieldsError, NoFoundError, OutOfInventoryError
import urllib.request
from src.models import PurchasedProduct, db, Product, Customer, Payment, Order
from src.dbUtils import Utils


class Store:

	def __init__(self, name, host, port, user, password) -> None:
		db.init(name, host=host, port=port, user=user, password=password)
		db.connect()

	def queryProducts(self) -> dict:
		return {"products": [model_to_dict(product) for product in Product.select()]}

	def registeryLegacyOrder(self, product : dict) -> int:
			newOrder = Order.create()
			try:
				Utils().checkProducts(product["product"], newOrder.id).save()
			except Exception as e:
				raise e
			return newOrder.id

	def registeryOrder(self, products : list) -> int:
			newOrder = Order.create()
			try:
				purchasedProducts = list()
				for i in products:
					purchasedProducts.append(Utils().checkProducts(i, newOrder.id))
			except Exception as e:
				raise e
			else :
				for i in purchasedProducts:
					i.save()

			return newOrder.id

#		except KeyError:
#			raise MissingFieldsError("La création d'une commande nécessite un produit")


	def queryOrder(self, id : int) -> dict:
		try :
			order : Order = Order.get(Order.id == id)
		except DoesNotExist:
			raise NoFoundError()


		products = []
		for i in Utils().getPurchasedProductByOrder(id):
			products.append({"id": i.id, "quantity": i.order.quantity})
		price = Utils().calculPrice(id)
		data = {
			"order" : {
				"id" : order.id,
				"total_price" : price["total_price"],
				"total_price_tax" : None,
				"email" : None,
				"credit_card":{},
				"shipping_information" : {},
				"products" : products,
				"paid": False,
				"transaction": {},
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

	def editCard(self, id : int, data : dict) -> None:
		creditCard = data["credit_card"]
		if not all(field in creditCard for field in ["name", "number", "expiration_year", "cvv", "expiration_month"]):
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")

		orderInfo : Order = Order.get(Order.id == id)
		if orderInfo.payment != None:
			raise AlreadyPaidError
		if orderInfo.customer == None:
			raise MissingFieldsError("Les informations du client sont nécessaire avant d'appliquer une carte de crédit")

		response = Utils().pay(id, data)
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
