from django.contrib import admin

from ads.models import User, Categories, Location, Ads

admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Location)
admin.site.register(Ads)


