from account_actions.action_base import AccountActionBase
from account_actions.action_pool import actions
from account_actions.test.factories import AccountActionTokenFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from faker import Factory

from base.test.factories import UserFactory
from base.test.testcases import Client

faker = Factory.create()

consumed = False


class TestAction(AccountActionBase):
    name = "test-register"

    def execute(self, method):
        global consumed
        consumed = True  # noqa


class TestAccountActionRegisterView(TestCase):
    def tearDown(self):
        super().tearDown()
        actions._registry.pop("test-register", None)
        global consumed
        consumed = False

    def test_return_an_http_403_error_if_the_user_is_already_authenticated(self):
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action="test-register")

        user = UserFactory()
        client = Client(logged_user=user)
        url = reverse("public:account_actions:register", kwargs={"key": token.key})

        response = client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_return_an_http_403_error_if_the_token_cannot_be_consumed(self):
        user = UserFactory()
        client = Client()
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action="test-register")
        token.consume(user)

        url = reverse("public:account_actions:register", kwargs={"key": token.key})
        response = client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_can_properly_create_a_new_user(self):
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action="test-register")

        post_data = {
            "username": faker.simple_profile().get("mail"),
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "password1": "not_secret",
            "password2": "not_secret",
        }

        url = reverse("public:account_actions:register", kwargs={"key": token.key})

        response = Client().post(url, post_data, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=post_data["email"]))

    def test_can_properly_consume_a_tokenr(self):
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action="test-register")

        post_data = {
            "username": faker.simple_profile().get("mail"),
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "password1": "not_secret",
            "password2": "not_secret",
        }

        url = reverse("public:account_actions:register", kwargs={"key": token.key})

        response = Client().post(url, post_data, follow=False)

        self.assertEqual(response.status_code, 302)
        global consumed
        self.assertTrue(consumed)
