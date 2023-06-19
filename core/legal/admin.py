from django.contrib import admin

from .models import LegalRequirement, LegalRequirementEvent

admin.site.register(LegalRequirement)
admin.site.register(LegalRequirementEvent)
