import os
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from requests_oauthlib import OAuth2Session

REDIRECT_URI = 'http://127.0.0.1:8080/login_done'

# Get a real consumer key & secret from:
# https://dashboard.dataporten.no
CLIENT_ID = 'dc2ad091-f6de-4205-8c1f-8e7b85cfa675'
CLIENT_SECRET = 'f8fb4196-0be0-4a31-be34-249e56da6731'
AUTHENGINE_BASE = 'https://auth.127.0.0.1.xip.io/'
REQUESTS_CA_BUNDLE = 'dde.pem'
AUTHORIZE_URL = AUTHENGINE_BASE + 'oauth/authorization'
ACCESS_TOKEN_URL = AUTHENGINE_BASE + 'oauth/token'
USERINFO_URL = AUTHENGINE_BASE + 'userinfo'
LOGOUT_URL = AUTHENGINE_BASE + 'logout'
GROUPS_BASE = 'https://groups-api.127.0.0.1.xip.io/'
GROUPS_URL = GROUPS_BASE + 'groups/me/groups'


def login_done(request):
    dpsess = OAuth2Session(CLIENT_ID,
                           redirect_uri=REDIRECT_URI)
    dpsess.fetch_token(ACCESS_TOKEN_URL,
                       client_secret=CLIENT_SECRET,
                       authorization_response=request.url,
                       verify=REQUESTS_CA_BUNDLE)
    response = Response()
    res = dpsess.get(USERINFO_URL, verify=REQUESTS_CA_BUNDLE)
    userinfo = res.json()['user']
    logoutbtn = '[<a href="logout"> logout </a>]'
    response.write(u'<h1>Hi {0}     {1}</h1>\n'.format(
        userinfo.get('name'), logoutbtn))
    response.write(u'<h2>Your id is: {0}</h2>\n'.format(
        userinfo.get('userid')))
    response.write(u'<h2>Your secondary ids are: {0}</h2>\n'.format(
        userinfo.get('userid_sec')))
    response.write(u'<h2>Your email is: {0}</h2>\n'.format(
        userinfo.get('email')))
    res = dpsess.get(GROUPS_URL, verify=REQUESTS_CA_BUNDLE)
    response.write(u'<h2>Your groups:</h2>\n')
    response.write('<pre>\n' + res.content.decode() + '</pre>')
    return response


def login(request):
    dpsess = OAuth2Session(CLIENT_ID)
    auth_url, _ = dpsess.authorization_url(AUTHORIZE_URL)
    raise HTTPFound(auth_url)


def logout(request):
    raise HTTPFound(LOGOUT_URL)


def home(request):
    return Response('''
<!DOCTYPE html>
<html lang="en">
<title>Test Dataporten Login</title>
<body>
        Login with <a href="login">Dataporten</a>.<br />
</body>
</html>
    ''')


if __name__ == '__main__':
    config = Configurator()
    config.add_route('home', '/')
    config.add_view(home, route_name='home')

    config.add_route('login', '/login')
    config.add_view(login, route_name='login')

    config.add_route('login_done', '/login_done')
    config.add_view(login_done, route_name='login_done')

    config.add_route('logout', '/logout')
    config.add_view(logout, route_name='logout')

    # Make example work wihtout ssl
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app = config.make_wsgi_app()
    server = make_server('127.0.0.1', 8080, app)
    server.serve_forever()
