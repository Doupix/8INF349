class MissingFieldsError(Exception):
	def __init__(self, message):
		self.message = {"errors" : { "product": {"code": "missing-fields","name": message}}}
	def __str__(self):
		return str(self.message)

class OutOfInventoryError(Exception):
	def __init__(self):
		self.message = {"errors" : {"product": {"code": "out-of-inventory","name": "Le produit demandé n'est pas en inventaire"}}}
	def __str__(self):
		return str(self.message)

class AlreadyPaidError(Exception):
	def __init__(self):
		self.message = {"errors" : {"order": {"code": "already-paid","name": "La commande a déjà été payée."}}}
	def __str__(self):
		return str(self.message)

class CardDeclinedError(Exception):
	def __init__(self):
		self.message ={"credit_card": {"code": "card-declined","name": "La carte de crédit a été déclinée."}}
	def __str__(self):
		return str(self.message)

class NoFoundError(Exception):
	pass
