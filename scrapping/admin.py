from django.contrib import admin
from scrapping.models import UserData
# Register your models here.

class UserDataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'ad_title',
        'reach',
        'created',
    )



admin.site.register(UserData, UserDataAdmin)
