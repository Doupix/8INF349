import click, json
import urllib.request
from src.models import db, Product, Customer, Payment, Order


@click.command('init-db')
def init_db_command():
	init_db("database.sql", products = json.loads(urllib.request.urlopen("https://dimensweb.uqac.ca/~jgnault/shops/products/").read()))


def init_db(path : str, products : dict):

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
