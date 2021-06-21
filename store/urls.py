from . import views
from django.urls import path,include

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('signup',views.signup,name="signup"),
    path('login',views.handlelogin,name="handlelogin"),
    path('logout',views.handlelogout,name="handlelogout"),
	path('updateItem/<int:id>/<str:action>', views.updateItem, name="updateItem"),
	path("handlerequest/", views.handlerequest, name="handlerequest"),
	path('processorder',views.processorder,name="processorder"),
	path('usertransactions',views.usertransactions,name="usertransactions"),
	path('adminorders',views.adminorders,name="adminorders"),
	path('viewproduct/<str:id>/',views.viewproduct,name="viewproduct")
]