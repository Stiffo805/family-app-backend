from django.contrib import admin

from activities.models import FamilyMember, Activity, ActivitiesLog

# Register your models here.

admin.site.register(FamilyMember)
admin.site.register(Activity)
admin.site.register(ActivitiesLog)