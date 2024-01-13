from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, username, password, **other_fields)

    def create_user(self, email, username, password, **other_fields):
        if not email:
            raise ValueError(_("You must provide an email address"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user


class NewUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=150, unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    about = models.TextField(_("about"), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


class Category(models.Model):
    title = models.CharField(
        max_length=200,
    )
    image = models.ImageField(upload_to="category", null=True, blank=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="product", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="product", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product.name


class ShippingAddress(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    shipping_address = models.TextField(_("shipping address"))
    mobile_number = models.CharField(_("mobile number"), max_length=15)
    city = models.CharField(_("city"), max_length=100)
    pincode = models.CharField(_("pincode"), max_length=10)

    def __str__(self):
        return f"Shipping Address - {self.user.username}"


class Order(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, null=True
    )
    order_date = models.DateTimeField(default=timezone.now)
    is_ordered = models.BooleanField(default=True)
    subtotal = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    # razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    # razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
    # razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    # paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Order Item - {self.product.name}"


# class Payment(models.Model):
#     user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     amount = models.FloatField()
#     razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
#     razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     paid = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Payment - Order: {self.order} Amount: {self.amount}"
