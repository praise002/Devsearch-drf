from django.contrib import admin

from apps.common.models import Book, Publisher

admin.site.register(Book)
admin.site.register(Publisher)