from itertools import product
from _pytest.mark.structures import store_mark
import pytest, json
from src.Database import *

def initDB(path : str) -> tuple[dict, DB]:
	products : dict = json.load(open(path))
	storage = DB(":memory:", products)
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
	orderID = storage.registeryOrder({ "product": { "id": 1, "quantity": 2 }})
	storage.editCustomer(orderID, { "order" : {
		"email" : "jgnault@uqac.ca",
		"shipping_information" : {
			"country" : "Canada",
			"address" : "201, rue Président-Kennedy",
			"postal_code" : "G7X 3Y7",
			"city" : "Chicoutimi",
			"province" : "QC"}}})

	with pytest.raises(CardDeclinedError):
		storage.editCard(orderID, {
			"credit_card" : {
				"name" : "John Doe",
				"number" : "4242 4242 4242 4242",
				"expiration_year" : 2022,
				"cvv" : "123",
				"expiration_month" : 9
			}})

	storage.editCard(orderID, {
		"credit_card" : {
			"name" : "John Doe",
			"number" : "4242 4242 4242 4242",
			"expiration_year" : 2025,
			"cvv" : "123",
			"expiration_month" : 9
		}})

	with pytest.raises(AlreadyPaidError):
		storage.editCard(orderID, {
			"credit_card" : {
				"name" : "John Doe",
				"number" : "4242 4242 4242 4242",
				"expiration_year" : 2025,
				"cvv" : "123",
				"expiration_month" : 9
			}})

	order = storage.queryOrder(orderID)["order"]
	assert(order["paid"]==True)
	assert(order["transaction"]!=None)
	assert(order["credit_card"]["last_digits"]=="4242")



def test_editOrderError():
	products, storage = initDB("./tests/json/products_light.json")
	orderID = storage.registeryOrder({ "product": { "id": 1, "quantity": 2 }})

	storage.editCustomer(orderID , { "order" : {
		"email" : "jgnault@uqac.ca",
		"shipping_information" : {
			"country" : "Canada",
			"address" : "201, rue Président-Kennedy",
			"postal_code" : "G7X 3Y7",
			"city" : "Chicoutimi",
			"province" : "QC"}}})

	with pytest.raises(NoFoundError):
		storage.editCustomer(42, {"order" : {
			"email" : "jgnault@uqac.ca",
			"shipping_information" : {
				"country" : "Canada",
				"address" : "201, rue Président-Kennedy",
				"postal_code" : "G7X 3Y7",
				"city" : "Chicoutimi",
				"province" : "QC"}}})

	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, { "order" : {
			"shipping_information" : {
				"country" : "Canada",
				"address" : "201, rue Président-Kennedy",
				"postal_code" : "G7X 3Y7",
				"city" : "Chicoutimi",
				"province" : "QC"}}})

	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, {
			"order" : {
				"email" : "jgnault@uqac.ca",
				"shipping_information" : {
					"country" : "Canada",
					"postal_code" : "G7X 3Y7",
					"city" : "Chicoutimi",
					"province" : "QC"}}}
		)
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orderID, {
			"order" : {
				"email" : "jgnault@uqac.ca",}}
		)
