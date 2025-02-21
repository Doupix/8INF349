from itertools import product
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
				"total_price" : 18.18*2,
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
				"total_price_tax" : (18.18*2)*1.15,
				"id" : 1,
				"total_price" : 18.18*2,
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


def test_editOrderError():
	products, storage = initDB("./tests/json/products_light.json")
	orders = [
		storage.registeryOrder({ "product": { "id": 1, "quantity": 2 }}),
		storage.registeryOrder({ "product": { "id": 1, "quantity": 1 }}),
		storage.registeryOrder({ "product": { "id": 1, "quantity": 4 }})
	]

	storage.editCustomer(orders[0], { "order" : {
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
		storage.editCustomer(orders[1], { "order" : {
			"shipping_information" : {
				"country" : "Canada",
				"address" : "201, rue Président-Kennedy",
				"postal_code" : "G7X 3Y7",
				"city" : "Chicoutimi",
				"province" : "QC"}}})

	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orders[2], {
			"order" : {
				"email" : "jgnault@uqac.ca",
				"shipping_information" : {
					"country" : "Canada",
					"postal_code" : "G7X 3Y7",
					"city" : "Chicoutimi",
					"province" : "QC"}}}
		)
	with pytest.raises(MissingFieldsError):
		storage.editCustomer(orders[2], {
			"order" : {
				"email" : "jgnault@uqac.ca",}}
		)
