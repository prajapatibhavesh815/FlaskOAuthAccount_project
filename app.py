from flask import Flask, render_template, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SERVER_NAME'] = 'localhost:5004'
oauth = OAuth(app)

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/google')
def google():
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['user'] = user
    return redirect('/')

@app.route('/twitter/')
def twitter():
    TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
    TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
    oauth.register(
        name='twitter',
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authenticate',
        api_base_url='https://api.twitter.com/1.1/',
    )
    redirect_uri = url_for('twitter_auth', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)

@app.route('/twitter/auth/')
def twitter_auth():
    token = oauth.twitter.authorize_access_token()
    resp = oauth.twitter.get('account/verify_credentials.json')
    profile = resp.json()
    session['user'] = profile
    return redirect('/')

@app.route('/facebook/')
def facebook():
    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
    oauth.register(
        name='facebook',
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get(
        'https://graph.facebook.com/me?fields=id,name,email,picture{url}'
    )
    profile = resp.json()
    session['user'] = profile
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
