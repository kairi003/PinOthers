#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import re
import logging
from urllib.parse import urljoin
from datetime import timedelta
from flask import Flask, jsonify, session, redirect, render_template, request, url_for
import tweepy
from tweepy.api import payload

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=7)

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

class ExAPI(tweepy.API):
    @payload('json')
    def pin_tweet(self, id, **kwargs):
        return self.request(
            'POST', 'account/pin_tweet', endpoint_parameters=(
                'tweet_mode', 'id'
            ), tweet_mode='extended', id=id, **kwargs
        )


@app.route('/')
def root():
    session.permanent = True
    #print('access_token: ', session.get('access_token'))
    #print('access_token_secret: ', session.get('access_token'))
    #print('request_token: ', session.get('request_token'))
    user = get_user()
    return render_template('index.html', user=user)


def get_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    key = session.get('access_token', None)
    secret = session.get('access_token_secret', None)
    auth.set_access_token(key, secret)
    return ExAPI(auth)


def get_user():
    api = get_api()
    try:
        user = api.verify_credentials()
        return user
    except:
        return None


@app.route('/login', methods=['GET'])
def login():
    callback_url = urljoin(request.host_url, url_for('callback'))
    auth = tweepy.OAuthHandler(
        CONSUMER_KEY, CONSUMER_SECRET, callback=callback_url)
    try:
        redirect_url = auth.get_authorization_url(False)
        session['request_token'] = auth.request_token
        #print("request_token: ", session['request_token'])
        return redirect(redirect_url)
    except Exception as ee:
        logging.error(str(ee))
        return redirect(url_for('root'))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('access_token', None)
    session.pop('access_token_secret', None)
    session.pop('request_token', None)
    return redirect(url_for('root'))


@app.route('/callback', methods=['GET'])
def callback():
    if 'request_token' in session and 'oauth_verifier' in request.args:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.request_token = session.pop('request_token', None)
        verifier = request.args.get('oauth_verifier')
        try:
            auth.get_access_token(verifier)
            session['access_token'] = auth.access_token
            session['access_token_secret'] = auth.access_token_secret
        except Exception as ee:
            logging.error(str(ee))
    return redirect(url_for('root'))


@app.route('/pin_tweet', methods=['POST'])
def pin_tweet():
    auth = tweepy.OAuthHandler(
        CONSUMER_KEY, CONSUMER_SECRET,
        session.get('access_token'), session.get('access_token_secret')
    )
    api = ExAPI(auth)
    try:
        if 'id' in request.form:
            tweet_id = int(request.form['id'])
        elif 'url' in request.form:
            tweet_url = request.form.get('url', '')
            tweet_id = re.match(r'https://twitter.com/\w+/status/(\d+)', tweet_url)[1]
        else:
            raise ValueError
        st = api.get_status(tweet_id)
        if st.user.id != api.verify_credentials().id:
            if st.retweeted:
                api.unretweet(st.id)
            st = st.retweet()
        resp = jsonify(api.pin_tweet(st.id)), 200
    except tweepy.HTTPException as e:
        r = e.response
        resp = jsonify(r.json()), r.status_code
    except Exception as e:
        resp = jsonify({'type': type(e).__name__, 'content': str(e)}), 500
    finally:
        return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
