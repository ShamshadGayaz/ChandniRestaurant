#!/usr/bin/env python
import os
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chandni_restaurant.settings')
django.setup()

from billing.models import Category, MenuItem, CarouselImage
from django.core.files.base import ContentFile

def create_sample_data():
    print("🌙 Creating sample data for Chandni Restaurant...")
    
    # Create Categories
    categories_data = [
        {'name': 'Mandi & Rice', 'cuisine_type': 'ARABIC', 'icon': 'fa-utensils', 'is_active': True},
        {'name': 'Arabic Appetizers', 'cuisine_type': 'ARABIC', 'icon': 'fa-carrot', 'is_active': True},
        {'name': 'Biryani & Curry', 'cuisine_type': 'INDIAN', 'icon': 'fa-pepper-hot', 'is_active': True},
        {'name': 'Indian Breads', 'cuisine_type': 'INDIAN', 'icon': 'fa-bread-slice', 'is_active': True},
        {'name': 'Desserts', 'cuisine_type': 'INDIAN', 'icon': 'fa-ice-cream', 'is_active': True},
        {'name': 'Beverages', 'cuisine_type': 'ARABIC', 'icon': 'fa-mug-hot', 'is_active': True},
    ]
    
    created_categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
        created_categories[category.name] = category
        if created:
            print(f"  ✅ Created category: {category.name}")
    
    # Create Menu Items
    menu_items_data = [
        # Arabic Dishes
        {'name': 'Chicken Mandi', 'category': 'Mandi & Rice', 'price': 35, 'description': 'Fragrant basmati rice with tender chicken, slow-cooked with Arabian spices', 'color_code': '#FF6B6B', 'is_popular': True},
        {'name': 'Lamb Mandi', 'category': 'Mandi & Rice', 'price': 55, 'description': 'Succulent lamb leg cooked to perfection with aromatic rice', 'color_code': '#E74C3C', 'is_popular': True},
        {'name': 'Madhbi Chicken', 'category': 'Mandi & Rice', 'price': 40, 'description': 'Grilled chicken on spiced rice with special sauce', 'color_code': '#FF8E53'},
        {'name': 'Faham Chicken', 'category': 'Mandi & Rice', 'price': 38, 'description': 'BBQ grilled chicken with mandi rice', 'color_code': '#FF9F43'},
        {'name': 'Hummus', 'category': 'Arabic Appetizers', 'price': 12, 'description': 'Creamy chickpea dip with olive oil and paprika', 'color_code': '#F4D03F'},
        {'name': 'Falafel (6pcs)', 'category': 'Arabic Appetizers', 'price': 10, 'description': 'Crispy chickpea patties with tahini sauce', 'color_code': '#27AE60', 'is_popular': True},
        {'name': 'Tabbouleh', 'category': 'Arabic Appetizers', 'price': 15, 'description': 'Fresh parsley, mint, and bulgur wheat salad', 'color_code': '#2ECC71'},
        {'name': 'Muttabal', 'category': 'Arabic Appetizers', 'price': 14, 'description': 'Smoky eggplant dip with pomegranate', 'color_code': '#9B59B6'},
        {'name': 'Shawarma Chicken', 'category': 'Arabic Appetizers', 'price': 18, 'description': 'Grilled chicken wrapped in pita with garlic sauce', 'color_code': '#F39C12', 'is_popular': True},
        
        # Indian Dishes
        {'name': 'Chicken Biryani', 'category': 'Biryani & Curry', 'price': 32, 'description': 'Aromatic basmati rice layered with spicy chicken and caramelized onions', 'color_code': '#F39C12', 'is_popular': True},
        {'name': 'Mutton Rogan Josh', 'category': 'Biryani & Curry', 'price': 48, 'description': 'Kashmiri style lamb curry with aromatic spices', 'color_code': '#D35400'},
        {'name': 'Butter Chicken', 'category': 'Biryani & Curry', 'price': 38, 'description': 'Creamy tomato-based chicken curry with butter', 'color_code': '#E67E22', 'is_popular': True},
        {'name': 'Paneer Tikka Masala', 'category': 'Biryani & Curry', 'price': 30, 'description': 'Grilled cottage cheese in rich creamy gravy', 'color_code': '#9B59B6'},
        {'name': 'Dal Makhani', 'category': 'Biryani & Curry', 'price': 22, 'description': 'Creamy black lentils slow-cooked overnight', 'color_code': '#8E44AD'},
        {'name': 'Palak Paneer', 'category': 'Biryani & Curry', 'price': 28, 'description': 'Cottage cheese in spinach gravy', 'color_code': '#27AE60'},
        {'name': 'Garlic Naan', 'category': 'Indian Breads', 'price': 8, 'description': 'Soft bread with fresh garlic and coriander', 'color_code': '#F1C40F'},
        {'name': 'Butter Naan', 'category': 'Indian Breads', 'price': 7, 'description': 'Classic butter naan bread', 'color_code': '#F39C12'},
        {'name': 'Tandoori Roti', 'category': 'Indian Breads', 'price': 6, 'description': 'Whole wheat bread baked in tandoor', 'color_code': '#E67E22'},
        {'name': 'Cheese Naan', 'category': 'Indian Breads', 'price': 12, 'description': 'Naan stuffed with melted cheese', 'color_code': '#FF6B6B', 'is_popular': True},
        {'name': 'Samosa (2pcs)', 'category': 'Indian Breads', 'price': 9, 'description': 'Crispy pastry with spiced potato and pea filling', 'color_code': '#E67E22', 'is_popular': True},
        
        # Desserts
        {'name': 'Gulab Jamun', 'category': 'Desserts', 'price': 10, 'description': 'Soft milk dumplings in sugar syrup', 'color_code': '#D35400', 'is_popular': True},
        {'name': 'Rasmalai', 'category': 'Desserts', 'price': 12, 'description': 'Cottage cheese patties in creamy milk', 'color_code': '#F4D03F'},
        {'name': 'Kunafa', 'category': 'Desserts', 'price': 18, 'description': 'Crispy shredded pastry with cheese and syrup', 'color_code': '#FF8E53', 'is_popular': True},
        {'name': 'Kheer', 'category': 'Desserts', 'price': 9, 'description': 'Indian rice pudding with nuts', 'color_code': '#F39C12'},
        
        # Beverages
        {'name': 'Mango Lassi', 'category': 'Beverages', 'price': 8, 'description': 'Sweet yogurt drink with mango', 'color_code': '#FFB347', 'is_popular': True},
        {'name': 'Masala Chai', 'category': 'Beverages', 'price': 5, 'description': 'Spiced Indian tea', 'color_code': '#D35400'},
        {'name': 'Ayran', 'category': 'Beverages', 'price': 6, 'description': 'Traditional yogurt drink', 'color_code': '#BDC3C7'},
        {'name': 'Fresh Lime Soda', 'category': 'Beverages', 'price': 7, 'description': 'Refreshing lime soda', 'color_code': '#2ECC71'},
    ]
    
    for item_data in menu_items_data:
        category = created_categories.get(item_data['category'])
        if category:
            MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'category': category,
                    'price': item_data['price'],
                    'description': item_data['description'],
                    'color_code': item_data['color_code'],
                    'is_popular': item_data.get('is_popular', False),
                    'is_available': True
                }
            )
    
    print(f"  ✅ Created {MenuItem.objects.count()} menu items")
    
    # Create Carousel Images (Colorful Placeholders)
    carousel_data = [
        {'title': 'Authentic Arabic Cuisine', 'color': '#FF6B6B'},
        {'title': 'Flavorful Indian Dishes', 'color': '#4ECDC4'},
        {'title': 'Family Dining Experience', 'color': '#45B7D1'},
        {'title': 'Fresh Ingredients Daily', 'color': '#96CEB4'},
        {'title': 'Fast Delivery Service', 'color': '#FFEAA7'},
    ]
    
    for i, data in enumerate(carousel_data):
        # Create a colorful image
        img = Image.new('RGB', (1200, 500), color=data['color'])
        draw = ImageDraw.Draw(img)
        
        # Draw some decorative elements
        for j in range(10):
            x1 = j * 120
            y1 = 0
            x2 = x1 + 60
            y2 = 500
            draw.rectangle([x1, y1, x2, y2], fill=(255,255,255,30))
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        draw.text((600, 250), data['title'], fill='white', anchor='mm', font=font)
        draw.text((600, 320), "Chandni Restaurant", fill='rgba(255,255,255,0.8)', anchor='mm', font=font)
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=85)
        
        carousel, created = CarouselImage.objects.get_or_create(
            title=data['title'],
            defaults={'order': i, 'is_active': True}
        )
        
        if created:
            carousel.image.save(f'carousel_{i}.jpg', ContentFile(img_io.getvalue()), save=True)
            print(f"  ✅ Created carousel image: {data['title']}")
    
    print("\n" + "="*50)
    print("🎉 Sample data created successfully!")
    print("="*50)
    print(f"📊 Summary:")
    print(f"   - Categories: {Category.objects.count()}")
    print(f"   - Menu Items: {MenuItem.objects.count()}")
    print(f"   - Carousel Images: {CarouselImage.objects.count()}")
    print("\n🔧 Next steps:")
    print("   1. Run: python manage.py runserver")
    print("   2. Visit: http://127.0.0.1:8000")
    print("   3. Admin: http://127.0.0.1:8000/admin")
    print("="*50)

if __name__ == '__main__':
    create_sample_data()