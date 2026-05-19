import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chandni_restaurant.settings')
django.setup()

from django.contrib.auth.models import User
from billing.models import UserProfile

print("🔧 Fixing user profiles...")

# Create profiles for all existing users without profile
users_without_profile = []
for user in User.objects.all():
    if not hasattr(user, 'profile'):
        users_without_profile.append(user.username)
        UserProfile.objects.create(user=user)
        print(f"  ✅ Created profile for: {user.username}")

if users_without_profile:
    print(f"\n✅ Created profiles for {len(users_without_profile)} users")
else:
    print("\n✅ All users already have profiles!")

# Ensure superuser has profile
admin_user = User.objects.filter(is_superuser=True).first()
if admin_user:
    if hasattr(admin_user, 'profile'):
        print(f"\n✅ Admin user '{admin_user.username}' has profile")
    else:
        UserProfile.objects.create(user=admin_user)
        print(f"\n✅ Created profile for admin user '{admin_user.username}'")
else:
    print("\n⚠️ No superuser found. Create one with: python manage.py createsuperuser")