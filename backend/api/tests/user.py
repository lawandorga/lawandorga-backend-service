from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from backend.api.models import UserProfile, RlcUser, Rlc
from backend.api.views import UserViewSet
from django.test import TestCase


class UserViewSetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserProfile.objects.create(email='test@test.de', name='Dummy 1')
        self.user.set_password('test')
        self.user.save()
        self.new_user = UserProfile.objects.create(email='test_new@test.de', name='Dummy 2')
        self.new_user.set_password('test')
        self.new_user.save()
        self.rlc = Rlc.objects.create(name="Test RLC")

    def test_everybody_can_post_to_user_create(self):
        view = UserViewSet.as_view(actions={'post': 'create'})
        request = self.factory.post('/api/users/')
        response = view(request)
        self.assertNotEqual(response.status_code, 403)

    def test_everybody_can_post_to_email_confirmation_token(self):
        view = UserViewSet.as_view({'post': 'create'})
        request = self.factory.post('/api/users/{}/confirm_email/'.format(99))
        response = view(request, pk=99)
        self.assertNotEqual(response.status_code, 403)

    def test_post_to_create_user_works(self):
        view = UserViewSet.as_view(actions={'post': 'create'})
        data = {
            'email': 'test2@test.de',
            'password': 'test',
            'password_confirm': 'test',
            'rlc': 1
        }
        request = self.factory.post('/api/users/', data)
        response = view(request)
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RlcUser.objects.exists())

    def test_email_confirmation_token_works(self):
        view = UserViewSet.as_view({'post': 'confirm_email'})
        shopping_user = ShoppingUser.objects.create(user=self.user)
        context = shopping_user.send_email_confirmation_email()
        data = {
            'token': context['token']
        }
        url = '/api/users/{}/confirm_email/'.format(context['user'].pk)
        request = self.factory.post(url, data)
        response = view(request, pk=context['user'].pk)
        self.assertEqual(response.status_code, 200)

    def test_register_passwords_returns_correct_error_message_on_different_passwords(self):
        view = UserViewSet.as_view({'post': 'create'})
        data = {
            'email': 'test2@test.de',
            'password': 'test1',
            'password_confirm': 'test2'
        }
        request = self.factory.post('/api/users/', data)
        response: Response = view(request)
        self.assertContains(response, 'non_field_errors', status_code=400)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ShoppingUser.objects.exists())

    def test_everybody_can_access_login(self):
        view = UserViewSet.as_view({'post': 'login'})
        request = self.factory.post('/api/users/login/')
        response = view(request)
        self.assertNotEqual(response.status_code, 403)

    def test_login_works(self):
        ShoppingUser.objects.create(user=self.user, email_confirmed=True)
        view = UserViewSet.as_view({'post': 'login'})
        data = {
            'email': 'test@test.de',
            'password': 'test',
        }
        request = self.factory.post('/api/users/login/', data)
        response = view(request)
        self.assertContains(response, 'token')
        self.assertContains(response, 'user')
        self.assertContains(response, 'email')
        self.assertEqual(response.status_code, 200)

    def test_login_returns_correct_password_wrong_error(self):
        view = UserViewSet.as_view({'post': 'login'})
        data = {
            'email': 'test@test.de',
            'password': 'falsch',
        }
        request = self.factory.post('/api/users/login/', data)
        response = view(request)
        self.assertContains(response, 'non_field_errors', status_code=400)

    def test_login_returns_correct_email_wrong_message(self):
        view = UserViewSet.as_view({'post': 'login'})
        data = {
            'email': 'falsch',
            'password': 'falsch',
        }
        request = self.factory.post('/api/users/login/', data)
        response = view(request)
        self.assertContains(response, 'non_field_errors', status_code=400)

    def test_everybody_can_hit_password_forgotten(self):
        view = UserViewSet.as_view({'post': 'password_forgotten'})
        request = self.factory.post('/api/users/password_forgotten/')
        response = view(request)
        self.assertNotEqual(response.status_code, 403)

    def test_password_forgotten_works(self):
        view = UserViewSet.as_view({'post': 'password_forgotten'})
        data = {
            'email': 'test@test.de'
        }
        request = self.factory.post('/api/users/password_forgotten/', data)
        response = view(request)
        self.assertNotEqual(response.status_code, 403)

    def test_everybody_can_hit_reset_password(self):
        view = UserViewSet.as_view({'post': 'reset_password'})
        shopping_user = ShoppingUser.objects.create(user=self.user)
        request = self.factory.post('/api/users/{}/reset_password/'.format(shopping_user.pk))
        response = view(request, pk=shopping_user.pk)
        self.assertNotEqual(response.status_code, 403)

    def test_reset_password_works(self):
        view = UserViewSet.as_view({'post': 'reset_password'})
        shopping_user = ShoppingUser.objects.create(user=self.user)
        context = shopping_user.send_password_reset_email()
        data = {
            'token': context['token'],
            'new_password': 'test1234',
            'password_confirm': 'test1234'
        }
        url = '/api/users/{}/reset_password/'.format(context['user'].pk)
        request = self.factory.post(url, data)
        response = view(request, pk=context['user'].pk)
        self.assertEqual(response.status_code, 200)

    def test_password_forgotten_fails_on_wrong_token(self):
        view = UserViewSet.as_view({'post': 'reset_password'})
        shopping_user = ShoppingUser.objects.create(user=self.user)
        context = shopping_user.send_password_reset_email()
        data = {
            'token': 'ar9qt9-1606b5f4f0ee279d23863eb22c34f0b3',
            'new_password': 'test1234',
            'password_confirm': 'test1234'
        }
        url = '/api/users/{}/reset_password/'.format(context['user'].pk)
        request = self.factory.post(url, data)
        response = view(request, pk=context['user'].pk)
        self.assertNotEqual(response.status_code, 200)

    def test_only_logged_in_user_can_change_email(self):
        view = UserViewSet.as_view({'post': 'change_email'})
        shopping_user = ShoppingUser.objects.create(user=self.user)
        data = {
            'new_email': 'neu@test.de',
        }
        url = '/api/users/{}/change_email/'.format(shopping_user.pk)
        request = self.factory.post(url, data)
        response = view(request, pk=shopping_user.pk)
        self.assertEqual(response.status_code, 401)

    def set_new_email_on_user(self):
        view = UserViewSet.as_view({'post': 'change_email'})
        shopping_user = ShoppingUser.objects.create(user=self.user)
        data = {
            'password': 'test',
            'new_email': 'neu@test.de',
        }
        url = '/api/users/{}/change_email/'.format(shopping_user.pk)
        request = self.factory.post(url, data)
        force_authenticate(request, self.user)
        response = view(request, pk=shopping_user.pk)
        self.assertEqual(response.status_code, 200)
        return shopping_user

    def test_logged_in_user_can_change_email(self):
        self.set_new_email_on_user()

    def confirm_email_change(self, shopping_user):
        context = shopping_user.send_email_change_email()
        view = UserViewSet.as_view({'post': 'confirm_email_change'})
        url = '/api/users/{}/confirm_email_change/'.format(context['user'].pk)
        data = {
            'token': context['token']
        }
        request = self.factory.post(url, data)
        response = view(request, pk=context['user'].pk)
        return response

    def test_email_change_can_be_confirmed(self):
        shopping_user = self.set_new_email_on_user()
        response = self.confirm_email_change(shopping_user)
        self.assertEqual(response.status_code, 200)

    def test_email_change_is_blocked_on_existing_email(self):
        User.objects.create(email='neu@test.de', password='test', name='Neuer Dummy')
        shopping_user = self.set_new_email_on_user()
        response = self.confirm_email_change(shopping_user)
        self.assertEqual(response.status_code, 400)

    def test_login_is_blocked_if_email_is_unconfirmed(self):
        ShoppingUser.objects.create(user=self.user, email_confirmed=False)
        view = UserViewSet.as_view({'post': 'login'})
        data = {
            'email': 'test@test.de',
            'password': 'test',
        }
        request = self.factory.post('/api/users/login/', data)
        response = view(request)
        self.assertContains(response, 'non_field_errors', status_code=400)

    def test_user_can_change_information(self):
        ShoppingUser.objects.create(user=self.user, pk=1)
        view = UserViewSet.as_view({'patch': 'partial_update'})
        data = {
            'street': 'abc',
        }
        request = self.factory.patch('/api/users/1/', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertContains(response, 'street', status_code=200)

    def test_user_can_only_change_own_information(self):
        ShoppingUser.objects.create(user=self.user, pk=1)
        ShoppingUser.objects.create(user=self.new_user, pk=2)
        view = UserViewSet.as_view({'patch': 'partial_update'})
        data = {
            'street': 'abc',
        }
        request = self.factory.patch('/api/users/2/', data)
        force_authenticate(request, self.user)
        response = view(request, pk=2)
        self.assertEqual(response.status_code, 404)

    def test_user_can_not_simply_change_email(self):
        ShoppingUser.objects.create(user=self.user, pk=1)
        view = UserViewSet.as_view({'patch': 'partial_update'})
        data = {
            'email': 'abc@test.de',
        }
        request = self.factory.patch('/api/users/1/', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertNotContains(response, 'abc@test.de', status_code=200)
