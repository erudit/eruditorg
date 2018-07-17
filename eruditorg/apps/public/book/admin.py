from django.contrib import admin
from .models import Book, BookCollection, BookAdmin

admin.site.register(BookCollection)
admin.site.register(Book, BookAdmin)
