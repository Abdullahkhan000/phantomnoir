from django.contrib import admin
from .models import Series, Genre, Movie

admin.site.register(Series)
admin.site.register(Movie)
admin.site.register(Genre)
