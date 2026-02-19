from django.contrib import admin  # pyright: ignore[reportMissingImports]
from .models import Diary, Comment

admin.site.register(Diary)
admin.site.register(Comment)
