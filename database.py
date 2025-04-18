import click, json
import urllib.request
from src.models import PurchasedProduct, db, Product, Customer, Payment, Order
from src.dbUtils import Utils
import os

@click.command('init-db')
def init_db_command():
	db.init(os.environ.get("DB_NAME"),
	host=os.environ.get("DB_HOST"),
	port=os.environ.get("DB_PORT"),
	user=os.environ.get("DB_USER"),
	password=os.environ.get("DB_PASSWORD"))
	db.connect()
	Utils().init_db(products = json.loads(urllib.request.urlopen("https://dimensweb.uqac.ca/~jgnault/shops/products/").read()))
