import json
from urllib.error import HTTPError

from peewee import *
from playhouse.shortcuts import model_to_dict
import urllib.request


db = PostgresqlDatabase(None)

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

class PurchasedProduct(BaseModel):
	id = AutoField()
	order = IntegerField()
	product = IntegerField()
	quantity = IntegerField()

class Order(BaseModel):
	id = AutoField()
	customer = IntegerField(null = True)
	payment = CharField(null = True)


# Classe gestion BDD
# Product.id
# Product.price
# Product.weight
# PurchasedProduct.quantity
