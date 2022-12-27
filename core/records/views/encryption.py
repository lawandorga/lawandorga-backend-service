# from rest_framework import mixins, status, viewsets
# from rest_framework.exceptions import ParseError, PermissionDenied
# from rest_framework.response import Response
# from core.records.models import RecordEncryptionNew

# from core.records.serializers import RecordEncryptionNewSerializer
# from core.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS


# class RecordEncryptionNewViewSet(
#     mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
# ):
#     queryset = RecordEncryptionNew.objects.none()
#     serializer_class = RecordEncryptionNewSerializer
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         if not RecordEncryptionNew.objects.filter(
#             user=request.user.rlc_user, record=instance.record
#         ).exists():
#             raise PermissionDenied(
#                 "You need access to the record in order to remove access from another person."
#             )
#         if RecordEncryptionNew.objects.filter(record=instance.record).count() <= 2:
#             raise ParseError(
#                 "You can not delete these encryption keys. There need to be at least 2 persons who "
#                 "have access to this record."
#             )
#         if instance.user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS):
#             raise ParseError(
#                 "You can not delete the encryption keys of this person, because he or she has "
#                 "the permission to access all records."
#             )
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def get_queryset(self):
#         queryset = RecordEncryptionNew.objects.filter(
#             record__template__rlc=self.request.user.rlc
#         )
#         record = self.request.query_params.get("record", None)
#         if record:
#             queryset = queryset.filter(record__pk=record)
#         return queryset
