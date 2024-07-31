import base64
from uuid import uuid4

from django.core.files.uploadedfile import UploadedFile
from django.db import models

from core.rlc.models.org import Org
from core.seedwork.domain_layer import DomainError


class Letterhead(models.Model):
    @classmethod
    def create(
        cls,
        org_id: int,
        address_line_1: str,
        address_line_2: str,
        address_line_3: str,
        address_line_4: str,
        address_line_5: str,
        text_right: str,
    ):
        return cls(
            org_id=org_id,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            address_line_3=address_line_3,
            address_line_4=address_line_4,
            address_line_5=address_line_5,
            text_right=text_right,
        )

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="letterheads")
    uuid = models.UUIDField(unique=True, default=uuid4)
    address_line_1 = models.CharField(max_length=256)
    address_line_2 = models.CharField(max_length=256, blank=True)
    address_line_3 = models.CharField(max_length=256, blank=True)
    address_line_4 = models.CharField(max_length=256, blank=True)
    address_line_5 = models.CharField(max_length=256, blank=True)
    logo = models.ImageField(upload_to="letterheads", blank=True)

    text_right = models.TextField(blank=True)

    class Meta:
        verbose_name = "Letterhead"
        verbose_name_plural = "Letterheads"

    @property
    def logo_url(self):
        return self.logo.url if self.logo else ""

    @property
    def logo_base64(self):
        if not self.logo:
            return ""
        with self.logo.open("rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded_string}"

    def update_letterhead(
        self,
        address_line_1: str,
        address_line_2: str,
        address_line_3: str,
        address_line_4: str,
        address_line_5: str,
        text_right: str,
    ):
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.address_line_3 = address_line_3
        self.address_line_4 = address_line_4
        self.address_line_5 = address_line_5
        self.text_right = text_right

    def update_logo(self, logo: UploadedFile):
        if not logo.size or logo.size > 1024 * 1024:
            raise DomainError("Logo size should be less than 1MB.")
        if logo.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise DomainError("Logo should be in .jpg, .jpeg or .png format.")
        self.logo: models.ImageField = logo  # type: ignore
