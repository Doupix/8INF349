from Errors import MissingFieldsError, NoFoundError, OutOfInventoryError


class FakeDB:
	'''
		Classe de substitution
	'''
	def __init__(self) -> None:
		pass

	def registryOrder(self, order) -> None:
		try :
			order["product"]["id"] # On regarde s'il y a un id
		except KeyError:
			raise MissingFieldsError("La création d'une commande nécessite un produit")
		if order["product"]["id"] == 1:
			raise OutOfInventoryError # Le produit 1 est toujours en rupture de stock...

	def queryOrder(self, id) -> dict:
		if id == 2:
			raise NoFoundError # Le produit 2 n'existe pas en stock
		return {}

	def queryProducts(self) -> dict:
		return {}

	def editOrder(self, id, json) -> None:
		pass
