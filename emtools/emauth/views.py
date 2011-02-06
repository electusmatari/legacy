import datetime
import random

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from emtools import utils
from emtools.ccpeve.models import apiroot
from emtools.emauth.decorators import require_account
from emtools.emauth.forms import APIKeyForm
from emtools.emauth.models import AuthToken
from emtools.emauth import userauth

@require_account
def view_avatar(request):
    if request.method == 'POST':
        return setavatar(request)
    return direct_to_template(request, 'emauth/avatar.html',
                              extra_context={'tab': 'avatar'})

@require_account
def view_token(request):
    try:
        token = request.user.authtoken
    except AuthToken.DoesNotExist:
        AuthToken.objects.create(user=request.user,
                                 token=generate_token())
    if request.method == 'POST':
        request.user.authtoken.token = generate_token()
        request.user.authtoken.save()
        return HttpResponseRedirect('/auth/token/')
    return direct_to_template(request, 'emauth/token.html',
                              extra_context={'tab': 'token'})

def generate_token():
    chars = ([chr(x) for x in range(ord('a'), ord('z')+1)] +
             [str(x) for x in range(10)])
    return "".join([random.choice(chars) for x in range(64)])

@require_account
def view_main(request):
    if request.method == 'POST':
        if request.user.profile.corpid:
            try:
                request.user.profile.active = True
                request.user.profile.save()
                userauth.authenticate_users(request.user)
                messages.add_message(request, messages.INFO,
                                     "Authentication successful.")
            except userauth.AuthenticationError as e:
                messages.add_message(request, messages.ERROR,
                                     str(e))
            return HttpResponseRedirect('/auth/')
        else:
            form = APIKeyForm(request.POST)
            if form.is_valid():
                try:
                    update_user(request.user,
                                form.cleaned_data['userid'],
                                form.cleaned_data['apikey'])
                    messages.add_message(request, messages.INFO,
                                         "Authentication successful.")
                    return HttpResponseRedirect('/auth/')
                except userauth.AuthenticationError as e:
                    messages.add_message(request, messages.ERROR,
                                         str(e))
    else:
        form = APIKeyForm()
    return direct_to_template(request, 'emauth/main.html',
                              extra_context={'form': form,
                                             'tab': 'auth'})

def setavatar(request):
    if request.user.profile.characterid is None:
        messages.add_message(request, messages.ERROR,
                             "Avatar update failed, you are not "
                             "authenticated.")
        return HttpResponseRedirect('/auth/')
    db = utils.connect('emforum')
    c = db.cursor()
    userauth.mybb_setavatar(c, request.user.profile.mybb_uid,
                            ("https://image.eveonline.com/Character/%s_64.jpg"
                             % (request.user.profile.characterid,)),
                            64, 64)
    db.commit()
    messages.add_message(request, messages.INFO,
                         "Avatar successfully updated.")
    return HttpResponseRedirect('/auth/')

def update_user(user, userid, apikey):
    try:
        api = apiroot(userid, apikey)
        characters = api.account.Characters()
    except Exception as e:
        raise userauth.AuthenticationError("Error during API call: %s" % 
                                           (str(e),))

    username = user.profile.mybb_username
    for char in characters.characters:
        if username == char.name:
            user.profile.name = char.name
            user.profile.characterid = char.characterID
            user.profile.corp = char.corporationName
            user.profile.corpid = char.corporationID
            user.profile.active = True
            user.profile.save()
            userauth.authenticate_users(user)
            return
        elif username.lower() == char.name.lower():
            raise userauth.AuthenticationError(
                "Your account name %s differs in case "
                "from your pilot name %s - please ask "
                "a forum administrator to rename your "
                "account." % (username, char.name))
    raise userauth.AuthenticationError(
        "The pilot %s was not found on the provided "
        "account, which lists the pilots %s. Please "
        "make sure this is the correct API key. You "
        "can ask a forum administrator to rename your "
        "account if necessary." % (username,
                                   ", ".join([char.name 
                                              for char
                                              in characters.characters])))
