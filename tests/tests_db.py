from itertools import product
from _pytest.mark.structures import store_mark
import pytest, json
from src.store import Store
from src.errors import *
import copy
import app

def initDB(path : str) -> tuple[dict, Store]:
	products : dict = json.load(open(path))
	app.init_db(":memory:", products)
	storage = Store()
	return (products, storage)

def test_queryProducts():
	products, storage = initDB("./tests/json/products_light.json")
	assert(products == storage.queryProducts())

def test_registeryOrder():
	products, storage = initDB("./tests/json/products_light.json")
	with pytest.raises(MissingFieldsError):
		storage.registeryOrder({ "product": { "id": 1}})
	with pytest.raises(MissingFieldsError):
		storage.registeryOrder({ "product": {"quantity": 1 }})
	with pytest.raises(MissingFieldsError):
		storage.registeryOrder({ "product": {"quantity": 2 }})
	with pytest.raises(OutOfInventoryError):
		storage.registeryOrder({ "product": { "id": 2, "quantity": 2 }})

def test_queryOrder():
	products, storage = initDB("./tests/json/products_light.json")
	orderId = storage.registeryOrder({ "product": { "id": 1, "quantity": 2 }})
	expectedResponse = {
			"order" : {
				"id" : 1,
				"total_price" : 36.36,
				"total_price_tax" : None,
				"email" : None,
				"credit_card": {},
				"shipping_information" : {},
				"paid": False,
				"transaction": {},
				"product" : {
					"id" : 1,
					"quantity" : 2
				},
				"shipping_price" : 10
			}
		}
	expectedResponseCustomer=  {
			"order" : {
				"credit_card": {},
				"email" : "jgnault@uqac.ca",
				"shipping_information" : {
					"country" : "Canada",
					"address" : "201, rue Président-Kennedy",
					"postal_code" : "G7X 3Y7",
					"city" : "Chicoutimi",
					"province" : "QC"
				},
				"paid": False,
				"transaction": {},
				"product" : {
					"id" : 1,
					"quantity" : 2
				},
				"shipping_price" : 10,
				"total_price_tax" : 41.81,
				"id" : 1,
				"total_price" : 36.36,
			}
		}

	with pytest.raises(NoFoundError):
		storage.queryOrder(orderId+1)

	assert(storage.queryOrder(orderId) == expectedResponse)
	storage.editCustomer(orderId, { "order" : {
		"email" : "jgnault@uqac.ca",
		"shipping_information" : {
			"country" : "Canada",
			"address" : "201, rue Président-Kennedy",
			"postal_code" : "G7X 3Y7",
			"city" : "Chicoutimi",
			"province" : "QC"}}})
	assert(storage.queryOrder(orderId) == expectedResponseCustomer)

def test_editCard():
	products, storage = initDB("./tests/json/products_light.json")
	customer =  {
		"order" : {
			"email" : "jgnault@uqac.ca",
			"shipping_information" : {
			"country" : "Canada",
			"address" : "201, rue Président-Kennedy",
			"postal_code" : "G7X 3Y7",
			"city" : "Chicoutimi",
			"province" : "QC"}}
		}
	card = {
		"credit_card" : {
			"name" : "John Doe",
			"number" : "4242 4242 4242 4242",
			"expiration_year" : 2022,
			"cvv" : "123",
			"expiration_month" : 9}
		}

	orderID = storage.registeryOrder({ "product": { "id": 1, "quantity": 2 }})
	storage.editCustomer(orderID, customer)

	with pytest.raises(CardDeclinedError):
		storage.editCard(orderID, card)

	card["credit_card"]["expiration_year"] = 2025
	storage.editCard(orderID, card)

	with pytest.raises(AlreadyPaidError):
		storage.editCard(orderID, card)

	order = storage.queryOrder(orderID)["order"]
	assert(order["paid"]==True)
	assert(order["transaction"]!=None)
	assert(order["credit_card"]["last_digits"]=="4242")



def test_editOrderError():
	products, storage = initDB("./tests/json/products_light.json")
	orderID = storage.registeryOrder({ "product": { "id": 1, "quantity": 2 }})
	customerInformation = [{
		"order" : {
			"email" : "jgnault@uqac.ca",
			"shipping_information" : {
			"country" : "Canada",
			"address" : "201, rue Président-Kennedy",
			"postal_code" : "G7X 3Y7",
			"city" : "Chicoutimi",
			"province" : "QC"
		}}}]

	for i in range(1, 4):
		customerInformation.append(copy.deepcopy(customerInformation[0]))

	customerInformation[1]["order"].pop("email")
	customerInformation[2]["order"]["shipping_information"].pop("address")
	customerInformation[3]["order"].pop("shipping_information")

	with pytest.raises(NoFoundError):
		storage.editCustomer(42, customerInformation[0])
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, customerInformation[1])
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, customerInformation[2])
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, customerInformation[3])

	storage.editCustomer(orderID , customerInformation[0])
