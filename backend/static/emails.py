#  rlcapp - record and organization management software for refugee law clinics
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

from django.core.mail import EmailMultiAlternatives
from django.template import loader
from backend.static.frontend_links import FrontendLinks
from backend.static.env_getter import get_env_variable


class EmailSender:
    @staticmethod
    def send_email_notification(email_addresses, subject: str, text: str):
        """
        Sends emails to all email_addresses with subject and text
        :param email_addresses: array with email adresses
        :param subject: subject of the email
        :param text: the email content itself
        :return:
        """
        from_email = get_env_variable('EMAIL_ADDRESS')
        msg = EmailMultiAlternatives(subject, text, from_email, email_addresses)
        msg.send()
        # send_mail(subject, text, 'notification@rlcm.de', email_addresses, fail_silently=False)

    @staticmethod
    def send_html_email(email_addresses, subject: str, html_content: str, text_alternative: str):
        from_email = get_env_variable('EMAIL_ADDRESS')
        msg = EmailMultiAlternatives(subject, text_alternative, from_email, email_addresses)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    @staticmethod
    def send_user_activation_email(user, link):
        html_message = loader.render_to_string(
            'email_templates/activate_account.html',
            {
                'url': link
            }
        )
        alternative_text = "RLC Intranet - Activate your account here: " + link
        subject = "RLC Intranet registration"
        EmailSender.send_html_email([user.email], subject, html_message, alternative_text)

    @staticmethod
    def send_record_new_message_notification_email(record):
        emails = record.get_notification_emails()
        link = FrontendLinks.get_record_link(record)
        html_message = loader.render_to_string(
            'email_templates/new_record_message.html',
            {
                'url': link,
                'record_token': record.record_token
            }
        )
        alternative_text = "RLC Intranet - New message in record: " + link
        subject = 'RLC Intranet - New Message'
        EmailSender.send_html_email(emails, subject, html_message, alternative_text)

    @staticmethod
    def test_send(email):
        html_message = loader.render_to_string(
            'email_templates/activate_account.html',
            {
                'url': 'asdasd'
            }
        )
        alternative_text = "RLC Intranet - Activate your account here: " + 'asdasd'
        subject = "RLC Intranet registration"
        EmailSender.send_html_email([email], subject, html_message, alternative_text)
