from itertools import product
import json
from urllib.error import HTTPError

from peewee import ModelSelect
from playhouse.shortcuts import model_to_dict
from playhouse.db_url import connect
from src.errors import AlreadyPaidError, CardDeclinedError, MissingFieldsError, NoFoundError, OutOfInventoryError
import urllib.request
from src.models import PurchasedProduct, db, Product, Customer, Payment, Order



class Utils:
	# Retourner liste produits
	def __init__(self) -> None:
		pass

	def checkProducts(self, order : dict, id : int) -> PurchasedProduct:
		if not all(field in order for field in ["id", "quantity"]):
				raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")
		if order["quantity"] < 1:
			raise MissingFieldsError("La création d'une commande nécessite un produit")

		product = Product.get_or_none(Product.id == order["id"])
		if not product.in_stock or not product:
			raise OutOfInventoryError()

		return PurchasedProduct(
			product=product,
			quantity=order["quantity"],
			order = id
		)

	def getPurchasedProductByOrder(self, id : int) -> ModelSelect:
		return Product.select(Product, PurchasedProduct).join(PurchasedProduct, on=(Product.id == PurchasedProduct.product), attr="order").where(id == PurchasedProduct.order)



#		except KeyError:
#			raise MissingFieldsError("La création d'une commande nécessite un produit")

	# Recupérer une commande
	# TODO




	def calculPrice(self, id : int) -> dict :
		order = Order.get(Order.id == id)
		products = self.getPurchasedProductByOrder(id)
		total_price = 0
		shipping_price = 0

		for i in products:
			total_price += i.price * i.order.quantity
			shipping_price += 5 if i.weight * i.order.quantity <= 500 else \
							 10 if i.weight * i.order.quantity < 2000 else 25

		price = {"total_price" : total_price , "shipping_price": shipping_price}
		customer = Customer.get_or_none(order.customer == Customer.id)
		if customer:
			match customer.province :
				case "QC":
					total_price_tax = round(1.15 * total_price, 2)
				case "ON":
					total_price_tax = round(1.13 * total_price, 2)
				case "AB":
					total_price_tax = round(1.05 * total_price, 2)
				case "BC":
					total_price_tax = round(1.12 * total_price, 2)
				case "NS":
					total_price_tax = round(1.14 * total_price, 2)
				case _:
					total_price_tax = round(1.15 * total_price, 2)
			price.update({"total_price_tax" : total_price_tax, "amount_charged":total_price_tax+shipping_price})
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
