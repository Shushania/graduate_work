from flask import Blueprint
from flask_jwt_extended import JWTManager
from flask_restful import Api

from src.api.v1.utils.oauth import OAuthSignIn
from src.db.pg import db
from src.models.db_models import SocialAccount, User

oauth = Blueprint("oauth_helper", __name__)
api = Api(oauth)
jwt = JWTManager()


@oauth.route("/authorize/<provider>")
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@oauth.route('/callback/<provider>')
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        return {"msg": "Account not found"}
    social_user = SocialAccount.query.filter_by(social_id=social_id).first()
    if not social_user:
        user = User(login=username, email=email)
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        social = SocialAccount(
            social_id=social_id,
            provider=provider,
            user_id=str(user.id),
        )
        db.session.add(social)
        db.session.commit()

    else:
        user = social_user.user
    return oauth.create_tokens(identity=user.id)

