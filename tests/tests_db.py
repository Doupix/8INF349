from itertools import product
import pytest, json
import database
from src.store import Store
from src.errors import *
import copy
from src.dbUtils import Utils
import os

def initDB() -> tuple[dict, Store]:
	products : dict = json.load(open("./tests/json/products.json"))
	for i in products["products"]:
		i.pop("height")
		i.pop("type")
	storage = Store(
		os.environ.get("DB_NAME"),
		os.environ.get("DB_HOST"),
		os.environ.get("DB_PORT"),
		os.environ.get("DB_USER"),
		os.environ.get("DB_PASSWORD"))
	return (products, storage)

def test_queryProducts():
	products, storage = initDB()
	assert(products == storage.queryProducts())


def test_registeryLegacyOrder():
	products, storage = initDB()
	with pytest.raises(MissingFieldsError):
		storage.registeryLegacyOrder({ "product": { "id": 1}})
	with pytest.raises(MissingFieldsError):
		storage.registeryLegacyOrder({ "product": {"quantity": 1 }})
	with pytest.raises(MissingFieldsError):
		storage.registeryLegacyOrder({ "product": {"quantity": 2 }})
	with pytest.raises(OutOfInventoryError):
		storage.registeryLegacyOrder({ "product": { "id": 4, "quantity": 2 }})

def test_registeryOrder():
	products, storage = initDB()
	with pytest.raises(MissingFieldsError):
		storage.registeryOrder([{ "id": 1, "quantity": 0 }, { "id": 3, "quantity": 2 }])
	with pytest.raises(MissingFieldsError):
		storage.registeryOrder([{ "id": 1, "quantity": 2 }, { "id": 3 }])
	with pytest.raises(MissingFieldsError):
		storage.registeryOrder([{"quantity": 2 }, { "id": 2, "quantity": 3 }])
	with pytest.raises(OutOfInventoryError):
		storage.registeryOrder([{ "id": 1, "quantity": 2 }, { "id": 4, "quantity": 2 }])


def test_queryOrder():
	products, storage = initDB()

	orderId = storage.registeryLegacyOrder({ "product": { "id": 1, "quantity": 2 }})

	expectedResponse = {
			"order" : {
				"id" : orderId,
				"total_price" : 56.2,
				"total_price_tax" : None,
				"email" : None,
				"credit_card": {},
				"shipping_information" : {},
				"paid": False,
				"transaction": {},
				"products" : [
					{"id" : 1, "quantity" : 2}
				],
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
				"products" : [
					{"id" : 1, "quantity" : 2}
				],
				"shipping_price" : 10,
				"total_price_tax" : 64.63,
				"id" : orderId,
				"total_price" : 56.2,
			}
		}

	with pytest.raises(NoFoundError):
		storage.queryOrder(orderId+100)

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
	products, storage = initDB()
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

	orderID = storage.registeryLegacyOrder({ "product": { "id": 1, "quantity": 2 }})
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
	products, storage = initDB()
	orderID = storage.registeryLegacyOrder({ "product": { "id": 1, "quantity": 2 }})
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
		storage.editCustomer(9999, customerInformation[0])
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, customerInformation[1])
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, customerInformation[2])
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, customerInformation[3])

	storage.editCustomer(orderID , customerInformation[0])
