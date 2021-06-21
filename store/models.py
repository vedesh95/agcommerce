from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
	name = models.CharField(max_length=200)
	price = models.IntegerField()
	image = models.TextField(null=True, blank=True)
	desc=models.TextField(null=True)
	def __str__(self):
		return self.name

class Order(models.Model):
	username = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	address=models.TextField(null=True)

	def __str__(self):
		return str(self.id)

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total