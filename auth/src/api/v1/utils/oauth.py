import json

from flask import current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from rauth import OAuth2Service


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials["id"]
        self.consumer_secret = credentials["secret"]
        self.get_callback_url = credentials["get_callback_url"]

    def authorize(self):
        pass

    def pre_callback(self):
        def decode_json(payload):
            return json.loads(payload.decode("utf-8"))

        if "code" not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={
                "code": request.args["code"],
                "response_type": "code",
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            },
            decoder=decode_json,
        )
        return oauth_session


    def callback(self):
        pass

    def get_callback_url(self):
        pass

    def create_tokens(self, identity: str):
        access_token = create_access_token(
            identity=identity,
            additional_claims={"is_superuser": False}
        )
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class YandexSignIn(OAuthSignIn):
    def __init__(self):
        super(YandexSignIn, self).__init__("yandex")
        self.service = OAuth2Service(
            name="yandex",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url="https://oauth.yandex.ru/authorize",
            access_token_url="https://oauth.yandex.ru/token",
            base_url="https://oauth.yandex.ru",
        )

    def authorize(self):
        print(self.get_callback_url())
        return redirect(
            self.service.get_authorize_url(
                scope="login:email login:info",
                response_type="code",
                redirect_uri=self.get_callback_url(),
            )
        )

    def get_callback_url(self):
        return self.get_callback_url

    def callback(self):
        oauth_session = self.pre_callback()
        info = oauth_session.get(url="https://login.yandex.ru/info").json()
        social_id = info.get("id")
        login = info.get("login")
        email = info.get("default_email")
        return social_id, login, email


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__("google")
        self.service = OAuth2Service(
            name="google",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            access_token_url="https://oauth2.googleapis.com/token",
            base_url="https://www.googleapis.com/",
        )

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope="email",
                response_type="code",
                redirect_uri=self.get_callback_url(),
            )
        )

    def get_callback_url(self):
        return self.get_callback_url

    def callback(self):
        oauth_session = self.pre_callback()
        info = oauth_session.get("oauth2/v2/userinfo").json()
        social_id = info.get("id")
        login = info.get("email").split("@")[0]
        email = info.get("email")
        return social_id, login, email
