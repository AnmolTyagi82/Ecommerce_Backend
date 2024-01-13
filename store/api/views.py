from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    CartItemSerializer,
    ShippingAddressSerializer,
    OrderSerializer,
)
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from store.models import Category, Product, CartItem, Order, OrderItem, ShippingAddress
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    # CartSerializer,
)


class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    ##
    def post(self, request):
        data = request.data
        assert validate_email(data)
        assert validate_password(data)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (SessionAuthentication,)

    ##
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "/api/token",
        "/api/token/refresh",
    ]

    return Response(routes)


class Categories(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class AllProducts(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class CartItemListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {"message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def post(self, request):
        data = request.data
        product_id = data.get("product")
        user = request.user
        try:
            cart_item = CartItem.objects.get(product=product_id, user=user)
            # If the cart item already exists, update the quantity
            cart_item.quantity += int(data["quantity"])
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            # If the cart item does not exist, create a new one
            serializer = CartItemSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            cart_item_id = request.data.get("cart_item_id")
            cart_item = CartItem.objects.get(id=cart_item_id)
            print(cart_item)
            cart_item.delete()
            return Response({"message": "Item removed from cart successfully"})

        except CartItem.DoesNotExist:
            return Response({"message": "Failed to remove item from cart"}, status=400)

    def patch(self, request):
        try:
            cart_item_id = request.data.get("cart_item_id")
            cart_item = CartItem.objects.get(id=cart_item_id)
            data = request.data
            type = data.get("type")
            if type == "inc":
                cart_item.quantity += 1
            elif type == "dec":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {"message": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {"message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def post(self, request):
        user = request.user
        data = request.data
        shipping_address_data = data.get("shipping_address_data")
        amount = data.get("amount")
        payment_id = data.get("razorpay_payment_id")
        print("Shipping Address Data:", shipping_address_data)
        print("Amount:", amount)
        serializer = ShippingAddressSerializer(data=shipping_address_data)
        if serializer.is_valid():
            shipping_address = serializer.save(user=user)
            print("Saved Shipping Address:", shipping_address)
            print(shipping_address)
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                subtotal=amount,
                payment_id=payment_id,
            )
            cart_items = CartItem.objects.filter(user=user)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                )
            cart_items.delete()
            return Response(
                {"message": "Order placed successfully."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
