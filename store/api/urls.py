from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("", views.getRoutes),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.UserRegister.as_view(), name="register"),
    path("login/", views.UserLogin.as_view(), name="login"),
    path("logout/", views.UserLogout.as_view(), name="logout"),
    path("user/", views.UserView.as_view(), name="user"),
    path("products/", views.AllProducts.as_view(), name="products"),
    path("categories/", views.Categories.as_view(), name="categories"),
    path("cart/", views.CartItemListCreateAPIView.as_view(), name="cart"),
    path("orders/", views.PlaceOrderView.as_view(), name="orders"),
]
