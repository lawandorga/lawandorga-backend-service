from django.contrib import admin

from .models import LegalRequirement, LegalRequirementEvent, LegalRequirementUser

admin.site.register(LegalRequirement)
admin.site.register(LegalRequirementUser)
admin.site.register(LegalRequirementEvent)
