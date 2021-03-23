#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from backend.static.frontend_links import FrontendLinks
from backend.static.logger import Logger
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template import loader
from django.conf import settings


class EmailSender:
    @staticmethod
    def send_email_notification(email_addresses, subject: str, text: str) -> None:
        """
        Sends emails to all email_addresses with subject and description_text
        :param email_addresses: array with email adresses
        :param subject: subject of the email
        :param text: the email content itself
        :return:
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text, from_email, email_addresses)
        msg.send()
        # send_mail(subject, description_text, 'notification@rlcm.de', email_addresses, fail_silently=False)

    @staticmethod
    def send_html_email(
        email_addresses, subject: str, html_content: str, text_alternative: str
    ) -> None:
        try:
            from_email = settings.DEFAULT_FROM_EMAIL

            send_mail(
                subject=subject,
                html_message=html_content,
                message=text_alternative,
                from_email=from_email,
                recipient_list=email_addresses,
            )
        except Exception as e:
            Logger.error("error at sending email: " + str(e))

    @staticmethod
    def send_user_activation_email(user, link) -> None:
        html_message = loader.render_to_string(
            "email_templates/activate_account.html", {"url": link}
        )
        alternative_text = "Law & Orga - Activate your account here: " + link
        subject = "Law & Orga registration"
        EmailSender.send_html_email(
            [user.email], subject, html_message, alternative_text
        )

    @staticmethod
    def send_record_new_message_notification_email(record) -> None:
        emails = record.get_notification_emails()
        link = FrontendLinks.get_record_link(record)
        html_message = loader.render_to_string(
            "email_templates/new_record_message.html",
            {"url": link, "record_token": record.record_token},
        )
        alternative_text = "Law & Orga - New message in record: " + link
        subject = "Law & Orga - New Message"
        EmailSender.send_html_email(emails, subject, html_message, alternative_text)

    @staticmethod
    def test_send(email) -> None:
        html_message = loader.render_to_string(
            "email_templates/activate_account.html", {"url": "asdasd"}
        )
        alternative_text = "Law & Orga - Activate your account here: "
        subject = "Law & Orga registration"
        EmailSender.send_html_email([email], subject, html_message, alternative_text)

    @staticmethod
    def send_forgot_password(email, link) -> None:
        html_message = loader.render_to_string(
            "email_templates/forgot_password.html", {"link": link,}
        )
        alternative_text = "Law & Orga - Password Reset: " + link
        subject = "Law & Orga - Password Reset"
        EmailSender.send_html_email([email], subject, html_message, alternative_text)

    @staticmethod
    def send_reset_password_complete(email) -> None:
        html_message = loader.render_to_string(
            "email_templates/regenerating_rlc_keys_complete.html"
        )
        alternative_text = "Law & Orga - Reset password complete"
        subject = "Law & Orga - Reset password complete"
        EmailSender.send_html_email([email], subject, html_message, alternative_text)

    @staticmethod
    def send_new_record(email_address: str, url: str) -> None:
        """
        sends email with notification of new record to given email address containing a link to the record
        :param email_address: email address to send the email to
        :param url: link to newly created record
        :return:
        """
        text = (
            "RLC Intranet Notification - Your were assigned as a consultant for a new record. Look here:"
            + url
        )
        EmailSender.send_email_notification([email_address], "New Record", text)
