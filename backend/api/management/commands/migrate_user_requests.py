from django.core.management.base import BaseCommand
from django.db.models import Q
from ...models import RlcUser, NewUserRequest


class Command(BaseCommand):
    def handle(self, *args, **options):
        RlcUser.objects.all().update(accepted=True)
        for r in NewUserRequest.objects.filter(Q(state='re') | Q(state='de')):
            r.request_from.rlc_user.accepted = False
            r.request_from.rlc_user.save()
