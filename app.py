import model
import utils
import random
import string
from flask import (
    Flask, render_template, request,
    redirect, url_for, jsonify, flash,
    make_response,
    session as login_session)
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
FB_APP_ID = "1136408746406465"
FB_CLIENT_SECRET = "1a11045117bf18370f171600b2bbc436"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isLogged():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/code-review')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/admin/')
@app.route('/admin/dashboard')
def dashboard():
    params = dict()
    if isLogged():
        params["username"] = login_session['username']
    params['problems'] = model.getAllProblems()
    params['codeToreview'] = model.getAllReviews()
    params['users'] = len(model.getAllUsers())
    return render_template('dashboard.html', **params)


@app.route('/start')
@login_required
def start():
    params = dict()
    if isLogged():
        params["username"] = login_session['username']
    params['problems'] = model.getAllProblems()
    return render_template('start.html', **params)


@app.route('/join')
def join():
    if isLogged():
        flash("You are logged as %s" % login_session['username'], "success")
        return redirect(url_for('start'))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if isLogged():
        flash("You are logged as %s" % login_session['username'], "success")
        return redirect(url_for('start'))

    if request.method == "POST":
        user = model.getUserByEmail(request.form["email"])
        if user and utils.check_secure_pass(
                request.form["passwd"], user.password):
            login_session['username'] = user.username
            login_session['email'] = user.email
            login_session['access_token'] = True

            return redirect(url_for('start'))
        else:
            flash("Email or Password incorrect", "danger")
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if isLogged():
        flash("You are logged as %s" % login_session['username'], "success")
        return redirect(url_for('start'))
    if request.method == 'POST':
        error = False
        username = request.form["username"]
        emailAdr = request.form["email"]
        passwd = request.form["passwd"]
        verif_passwd = request.form["verif_passwd"]
        if not utils.valid_email(emailAdr):
            error = True
            flash("Invalid email", "error")
        if not utils.valid_password(passwd):
            error = True
            flash("Invalid password", "error")
        if verif_passwd != passwd:
            error = True
            flash("Password verification failed", "error")
        if model.getUserByEmail(emailAdr):
            error = True
            flash("User Already exist", "warning")

        if error:
            return redirect(url_for('signUp'))

        model.addUser(username, emailAdr, passwd)
        msg = "Welcome %s", str(username)
        flash(msg, "success")
        utils.send_welcome(emailAdr)
        return redirect(url_for('login'))

    else:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        return render_template('signup.html', STATE=state)


@app.route('/gconnect', methods=["POST"])
def gconnect():
        # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # stored_credentials = login_session.get('credentials')
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['social_id'] = gplus_id
    # login_session['credentials'] = credentials

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['social'] = 'gplus'

    output = ''
    output += 'Welcome, '
    output += login_session['username']
    output += '!'
    # Register if new user
    if not model.getUserBySocialId(login_session['social_id'],
                                   login_session['username']):
        model.addUser(login_session['username'], login_session[
                      'email'], "", login_session['social_id'])

        utils.send_welcome(data['email'])

    return output


@app.route('/fconnect', methods=["POST"])
def fconnect():
        # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    base_url = "https://graph.facebook.com"

    url = base_url + "/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (
        FB_APP_ID, FB_CLIENT_SECRET)

    h = httplib2.Http()
    access_token = h.request(url, 'GET')

    url = base_url + "/debug_token?input_token=%s&%s" % (
        request.data, access_token[1])

    result = json.loads(h.request(url, 'GET')[1])
    print result
    if "error" in result:
        response = make_response(json.dumps(
            "Invalid OAuth access token signature."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if not result['data']['is_valid']:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # get user infos
    params = "email,name,first_name,picture"
    url = base_url + \
        "/me?access_token=%s&fields=%s" % (request.data, params)
    fb_user = json.loads(h.request(url, 'GET')[1])

    fb_user_pic = fb_user['picture']['data']
    login_session['access_token'] = request.data
    login_session['social_id'] = fb_user['id']
    login_session['username'] = fb_user['name']
    login_session['picture'] = fb_user_pic[
        'url'] if fb_user_pic['is_silhouette'] else "null"
    login_session['email'] = fb_user['email']
    login_session['social'] = 'fb'

    output = ''
    output += 'Welcome, '
    output += login_session['username']
    output += '!'
    # Register if new user
    if not model.getUserBySocialId(
            login_session['social_id'], login_session['username']):
        model.addUser(login_session['username'], login_session[
                      'email'], "", login_session['social_id'])

        utils.send_welcome(fb_user['email'])

    return output


@app.route('/logout')
@login_required
def logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        flash("User not connected.", "warning")
        return redirect(url_for('start'))
    h = httplib2.Http()
    result = dict()
    result['status'] = '200'
    if "social" in login_session and login_session['social'] == 'gplus':
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        result = h.request(url, 'GET')[0]
        print "logout by google"
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        flash("Logout Error: Failed to revoke token for given user.", "danger")
        return redirect(url_for('start'))
    # Reset the user's session
    # del login_session['credentials']
    print "general logout"
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    # del login_session['picture']
    if "social_id" in login_session:
        del login_session['social_id']
    # del login_session['social']
    return redirect(url_for('login'))


@app.route('/problems')
def allproblems():
    print "search all problems from db and print"


@app.route('/problem/add', methods=['GET', 'POST'])
@login_required
def addProblem():
    if request.method == 'POST':
        solution = json.dumps(request.form["code"])
        if request.form['title'] and request.form['desc'] and solution:
            new_problem = dict()
            new_problem["title"] = request.form['title']
            new_problem["desc"] = request.form["desc"]
            new_problem["lang"] = request.form["code_language"]
            new_problem["solution"] = solution
            new_problem["cat_id"] = request.form["category"]
            model.addProblem(new_problem, login_session.get("email"))
        else:
            flash("Error!! Invalid input data", "danger")
        return redirect(url_for('start'))
    params = dict()
    params['categories'] = model.getCategories()
    params['languages'] = model.getLanguages()
    params['username'] = login_session['username']
    return render_template('addproblem.html', **params)


@app.route('/problem/edit/<int:pb_id>')
@login_required
def editProblem(pb_id):
        # edit a problem
    print " "


@app.route('/problem/<int:pb_id>')
def displayProblem(pb_id):
    params = dict()
    problem = model.getProblemByID(int(pb_id))
    if isLogged():
        params["username"] = login_session['username']
    if problem:
        params['problem'] = problem
        params['languages'] = model.getLanguages()
    else:
        flash("Error!! Items not found", "danger")
        return redirect(url_for('start'))
    return render_template('problem.html', **params)


@app.route('/problem/<int:pb_id>/submit-to-review/', methods=["POST"])
@login_required
def attemptSolution(pb_id):
    # "submit solution to a problem to review". RUN THE CODE WHILE SAVING
    if request.method == "POST":
        language = request.form["code_language"]
        solution = json.dumps(request.form["code"])
        user = model.getUserByEmail(login_session['email'])
        if request.form['action'] == "review_code":
            model.addCodeToReview(solution, language, pb_id, user.id)
            flash("You submitted your code for review", "success")
        if request.form['action'] == "save_code":
            model.editProblem(pb_id, solution, language)
            print "save my code"
        if request.form['action'] == "run_code":
            print "run code"

    return redirect(url_for('displayProblem', pb_id=pb_id))


@app.route('/profile/me')
@login_required
def userProfile():
    params = dict()
    user = model.getUserByEmail(login_session['email'])
    params['user'] = user
    params['username'] = user.username
    params['code_submitted'] = model.getUserCodeToReview(user.id)
    return render_template("profile.html", **params)


@app.route('/profile/activities')
@login_required
def allReviews():
    params = dict()
    user = model.getUserByEmail(login_session['email'])
    params['user'] = user
    params['username'] = user.username
    params['code_submitted'] = model.getUserCodeToReview(user.id)
    return render_template("activity.html", **params)


@app.route('/profile/edit', methods=['POST'])
@login_required
def editProfile():
    if request.method == "POST":
        print request.form['conditions']
        if request.form['conditions'] == "on":
            userinfo = {'fullname': request.form['fullname']}
            if request.form['experience']:
                userinfo['aboutme'] = request.form['experience']
            if request.form['location']:
                userinfo['location'] = request.form['location']
            if request.form['skills']:
                userinfo['skills'] = request.form['skills']
            model.editUser(login_session['email'], userinfo)
            flash("Profile infos saved", "success")
        else:
            flash('Terms and Conditions field.', 'warning')
    return redirect(url_for('userProfile'))


@app.route('/review/code/<int:review_id>', methods=["GET", "POST"])
@login_required
def codeReview(review_id):
    if request.method == "POST":
        if request.form['comments']:
            model.commentReview(review_id, request.form['comments'],
                                login_session['email'])
            return redirect(url_for('codeReview', review_id=review_id))
    else:
        params = dict()
        params["username"] = login_session['username']
        params['codeToreview'] = model.getCodeReview(review_id)
        params['comments'] = model.getComments(review_id)
        return render_template('codereview.html', **params)


@app.errorhandler(404)
def page_not_found(e):
    if isLogged():
        username = login_session['username']
        return render_template("404.html", username=username)
    return render_template("404.html")


def isLogged():
    if login_session.get('access_token') is None:
        return False
    return True


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
