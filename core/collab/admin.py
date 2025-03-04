from django.contrib import admin

from core.collab.models.collab import Collab
from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead
from core.collab.models.template import Template

admin.site.register(Collab)
admin.site.register(Letterhead)
admin.site.register(Footer)
admin.site.register(Template)
