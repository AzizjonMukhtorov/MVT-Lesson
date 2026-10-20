from django.contrib import admin

from .models import Category, Flower, Likes


admin.site.register([Category, Flower, Likes])