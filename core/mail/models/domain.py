import re
from typing import Literal, TypedDict, Union
from uuid import uuid4

from django.conf import settings
from django.db import models

from core.mail.models.org import MailOrg


class DnsSetting(TypedDict):
    type: str
    host: str
    check: str


class DnsSettings(TypedDict):
    MX: DnsSetting
    DKIM: DnsSetting
    DMARC: DnsSetting
    SPF: DnsSetting


class DnsResults(TypedDict):
    MX: Union[str, list[str]]
    DKIM: Union[str, list[str]]
    DMARC: Union[str, list[str]]
    SPF: Union[str, list[str]]


class MailDomain(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    org = models.ForeignKey(
        MailOrg, related_name="domains", on_delete=models.CASCADE, null=True
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "MailDomain"
        verbose_name_plural = "MailDomains"

    def __str__(self):
        return "mailDomain: {};".format(self.pk)

    @staticmethod
    def check_domain(domain: str):
        if domain == settings.MAIL_MX_RECORD:
            raise ValueError(
                "You are not allowed to use '{}' as your domain.".format(
                    settings.MAIL_MX_RECORD
                )
            )

        if not isinstance(domain, str):
            raise TypeError(
                "The domain should be of type 'str' but is '{}'.".format(type(domain))
            )

        if len(domain) < 1:
            raise ValueError("The domain is too short.")

        if len(domain) > 64:
            raise ValueError("The domain is too long.")

        regex = "^((?!-)[a-z0-9-]+(?<!-)\\.)+(?!-)[a-z-]{2,20}(?<!-)$"
        pattern = re.compile(regex)
        if not pattern.match(domain):
            raise ValueError(
                "The domain contains illegal characters or does not conform to the correct structure."
            )

    def set_name(self, name):
        self.check_domain(name)
        self.name = name
        self.deactivate()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def __check_setting(
        self, setting: DnsSetting, dns_results: list[str]
    ) -> tuple[bool, str]:

        p = re.compile(setting["check"])

        for result in dns_results:
            match = p.match(result)
            if match is not None:
                return True, ""

        return (
            False,
            "'{}' setting should pass the regex check '{}' but did not. Your setting is: '{}'.".format(
                setting["type"], setting["check"], ", ".join(dns_results)
            ),
        )

    def check_settings(self, dns_results: DnsResults) -> tuple[bool, None | str]:
        dns_settings = self.get_settings()

        for key in dns_settings.keys():
            k: Literal["MX", "DKIM", "DMARC", "SPF"] = key  # type: ignore
            results: str | list[str] = dns_results[k]

            if isinstance(results, str):
                self.deactivate()
                return (
                    False,
                    "While checking the '{}' setting the following error happened: '{}'.".format(
                        k, results
                    ),
                )

            result, error = self.__check_setting(dns_settings[k], results)

            if not result:
                self.deactivate()
                return False, error

        self.activate()
        return True, None

    def get_settings(self) -> DnsSettings:
        ret: DnsSettings = {
            "MX": {
                "type": "MX",
                "host": self.name,
                "check": r"^\d\d? {}.$".format(settings.MAIL_MX_RECORD),
            },
            "SPF": {
                "type": "TXT",
                "host": self.name,
                "check": r"^v=spf1 +(.+ +)?include:{} +(.+ +)?-all$".format(
                    settings.MAIL_SPF_RECORD
                ),
            },
            "DMARC": {
                "type": "CNAME",
                "host": f"_dmarc.{self.name}",
                "check": r"^{}\.$".format(settings.MAIL_DMARC_RECORD),
            },
            "DKIM": {
                "type": "CNAME",
                "host": f"2022-12._domainkey.{self.name}",
                "check": r"^{}\.$".format(settings.MAIL_DKIM_RECORD),
            },
        }
        return ret
