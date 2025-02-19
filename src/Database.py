import json
from peewee import *
from src.Errors import MissingFieldsError, NoFoundError, OutOfInventoryError

# Connexion database
db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

# Modele porduits
class Product(BaseModel):
	id = IntegerField(primary_key=True)
	name = CharField()
	description = TextField()
	price = FloatField()
	weight = IntegerField()
	in_stock = BooleanField()
	image = CharField()

# Modele comandes
class Order(BaseModel):
	id = AutoField()
	product = ForeignKeyField(Product, backref='orders')
	quantity = IntegerField()
	total_price = FloatField()
	total_price_tax = FloatField(null=True)
	shipping_price = FloatField(null=True)
	email = CharField(null = True)
	shipping_information = TextField(null = True)
	paid = BooleanField(default=False)

# Classe gestion BDD
class DB:
	def __init__(self, path : str, products : dict):
		db.init(path)
		db.connect()
		db.create_tables([Product, Order], safe=True)
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

	# Retourner liste produits
	def queryProducts(self) -> dict:
		return {"products": [product.__data__ for product in Product.select()]}

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

			total_price = product.price * quantity
			shipping_price = 5 if product.weight * quantity <= 500 else \
							 10 if product.weight * quantity < 2000 else 25

			new_order = Order.create(
				product=product,
				quantity=quantity,
				total_price=total_price,
				shipping_price=shipping_price,
				email=None,
				shipping_information=None
			)
			return new_order.id
		except KeyError:
			raise MissingFieldsError("La création d'une commande nécessite un produit")

	# Recupérer une commande
	def queryOrder(self, id) -> dict:
		order = Order.get_or_none(Order.id == id)
		if not order:
			raise NoFoundError()

		order_data = order.__data__
		order_data["shipping_information"] = json.loads(order_data["shipping_information"]) if order_data["shipping_information"] else None
		return order_data

	# Modifier commande (ajout mail adresse)
	def editOrder(self, id : int, data : dict[str, dict]) -> None:
		order = Order.get_or_none(Order.id == id)
		if not order:
			raise NoFoundError()

		# Verifier la présence des champs obligatoires
		required_fields = ["email", "shipping_information"]
		if not all(field in data["order"] for field in required_fields):
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")

		# Vérifier que 'shipping_information' contient bien les sous champs obligatoires
		shipping_required_fields = ["country", "address", "postal_code", "city", "province"]
		if not all(field in data["order"]["shipping_information"] for field in shipping_required_fields):
			raise MissingFieldsError("Il manque un ou plusieurs champs qui sont obligatoires")

		# Mettre à jour uniquement mail et shipping_information
		order.email = data["order"]["email"]
		order.shipping_information = json.dumps(data["order"]["shipping_information"])
		order.save()
