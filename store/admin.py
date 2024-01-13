from django.contrib import admin
from .models import (
    NewUser,
    Category,
    Product,
    CartItem,
    ShippingAddress,
    Order,
    OrderItem,
)
from django.contrib.auth.admin import UserAdmin
from django.forms import Textarea


class UserAdminConfig(UserAdmin):
    model = NewUser
    search_fields = (
        "email",
        "username",
    )
    list_filter = ("email", "username", "is_active", "is_staff")
    ordering = ("-start_date",)
    list_display = ("email", "username", "is_active", "is_staff")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "username",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
        ("Personal", {"fields": ("about",)}),
    )
    formfield_overrides = {
        NewUser.about: {"widget": Textarea(attrs={"rows": 10, "cols": 40})},
    }
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


admin.site.register(NewUser, UserAdminConfig)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
