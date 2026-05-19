from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User, Group
from .models import Category, MenuItem, Order, CarouselImage, UserProfile

# Unregister default User admin
try:
    admin.site.unregister(User)
except:
    pass
    
try:
    admin.site.unregister(Group)
except:
    pass

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'has_profile']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def has_profile(self, obj):
        return hasattr(obj, 'profile')
    has_profile.boolean = True
    has_profile.short_description = "Has Profile"
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address_short', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    
    def address_short(self, obj):
        return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
    address_short.short_description = "Address"

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'preview_image']
    list_editable = ['order', 'is_active']
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit:cover; border-radius:8px"/>', obj.image.url)
        return "No Image"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'cuisine_type', 'icon', 'is_active', 'item_count']
    list_editable = ['is_active']
    list_filter = ['cuisine_type']
    
    def item_count(self, obj):
        return obj.items.filter(is_available=True).count()

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_popular', 'color_preview']
    list_editable = ['price', 'is_available', 'is_popular']
    list_filter = ['category', 'is_available']
    search_fields = ['name']
    
    def color_preview(self, obj):
        return format_html('<div style="width:35px;height:35px;background:{};border-radius:8px;"></div>', obj.color_code)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer_name', 'total', 'payment_method', 'payment_status', 'status', 'created_at']
    list_editable = ['status', 'payment_status']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'id']
    readonly_fields = ['subtotal', 'delivery_charge', 'vat_amount', 'total', 'items_json']