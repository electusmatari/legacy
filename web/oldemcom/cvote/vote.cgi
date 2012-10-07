#!/usr/bin/env python

import cgitb ; cgitb.enable()

import os
import cgi
import datetime

import MySQLdb

from lib.cgihelper import my_url, dispatch, redirect, tab_menu
from lib.mybb_auth import mybb_auth
from lib.schulze import Schulze

# Configuration

execfile("/home/forcer/Projects/private/old_access.py")
db_name = "emmisc"

urlconf = [
    ("^vote/closed/(?P<voteid>[0-9]+)/edit/", 'edit_vote'),
    ("^vote/closed/(?P<voteid>[0-9]+)/", 'show_vote'),
    ("^vote/closed/", 'list_votes', {"closed": True}),
    ("^vote/create/", 'create_vote'),
    ("^vote/doc/", 'show_docs'),
    ("^vote/(?P<voteid>[0-9]+)/edit/", 'edit_vote'),
    ("^vote/(?P<voteid>[0-9]+)/", 'show_vote'),
    ("^vote/", 'list_votes', {"closed": False}),
]

tabconf = [
    ("/vote/", "Open Votes"),
    ("/vote/closed/", "Closed Votes"),
    ("/vote/create/", "New Vote"),
    ("/vote/doc/", "Documentation")
]

# Globals

db = MySQLdb.connect(host=db_host, user=db_user,
                     passwd=db_pass, db=db_name)
form = cgi.FieldStorage()

# Functions

def main():
    (username, allowed) = mybb_auth()
    if not allowed:
        if username == "Anonymous":
            error = "<p><strong>Please log in to the forums.</strong></p>"
        else:
            error = "<p><strong>You are not allowed to use this script.</strong></p>"
        print html_base % {"content": error,
                           "current_time": eve_time(),
                           "vote_time": "You have not voted yet.",
                           "username": cgi.escape(username),
                           "tabs": ""}
        return
    data = dispatch(urlconf, {"username": username})
    if data is None:
        print "Status: 404 Not Found"
        print "Content-Type: text/html"
        print
        print "<html><body><h1>404 File Not Found</h1></body></html>"
        return
    elif os.getenv("REQUEST_METHOD") == 'POST':
        return redirect(data)
    else:
        vote_time = eve_time(sql_user_last_vote(username))
        if vote_time == "never":
            vote_time = "You have not voted yet."
        else:
            vote_time = "You have last voted on %s." % vote_time
        print html_base % {"content": data,
                           "current_time": eve_time(),
                           "vote_time": vote_time,
                           "username": cgi.escape(username),
                           "tabs": tab_menu(tabconf)}

#############
### Views ###
#############

def list_votes(username, closed=False, **kwargs):
    html = "<ul>"
    for (voteid, title, creator, started, finished) in sql_get_votes(closed):
        html += html_vote_list_entry % {"voteid": voteid,
                                        "title": cgi.escape(title),
                                        "creator": cgi.escape(creator),
                                        "started": eve_time(started)}
    html += "</ul>"
    return html

def show_vote(voteid, username, **kwargs):
    (title, description, creator, started, finished, allowed_voters) = sql_get_vote(voteid)
    user_can_vote = can_vote(username, allowed_voters)
    options = sql_get_options(voteid)
    if os.getenv("REQUEST_METHOD") == 'POST':
        if finished is not None or not user_can_vote:
            return my_url()
        ballot = {}
        for (optid, name) in options:
            value = form.getfirst("opt%i" % optid, None)
            if value is not None and value != "":
                try:
                    ballot[optid] = int(value)
                except:
                    pass
        sql_update_ballot(voteid, username, ballot)
        return my_url()
    if creator == username:
        edit = '<p><a href="edit/">Edit this vote</a></p>'
    else:
        edit = ""
    if finished is None:
        runtime = "since %s" % eve_time(started)
    else:
        runtime = "from %s to %s" % (eve_time(started), eve_time(finished))
    ballot = sql_get_ballot(voteid, username)        
    if user_can_vote and ballot == []:
        result = "<p>Please vote first.</p>"
    else:
        result = format_vote_result(voteid, form.getfirst("verbose", False))
    if finished is not None:
        vote_form = "<p>This vote is closed.</p>"
    elif not user_can_vote:
        vote_form = "<p>You are not allowed to participate in this vote.</p>"
    else:
        vote_form = ballot_form(voteid, options, ballot)
    return html_show_vote % {"title": cgi.escape(title),
                             "description": format(description),
                             "creator": cgi.escape(creator),
                             "runtime": cgi.escape(runtime),
                             "result": result,
                             "vote_form": vote_form,
                             "edit": edit}

def create_vote(username, **kwargs):
    if os.getenv("REQUEST_METHOD") == 'POST':
        title = form.getfirst("title", "Untitled")
        description = form.getfirst("description", "")
        allowed_voters = sanitize_allowed_voters(form.getfirst("allowed_voters", ""))
        voteid = sql_create_vote(username, title, description,
                                 allowed_voters)
        return my_url() + "../%i/edit/" % voteid
    return html_vote_form % {"title": "",
                             "description": "",
                             "allowed_voters": "",
                             "button": "Create Vote"}

def edit_vote(voteid, username, **kwargs):
    (title, description, creator, started, finished, allowed_voters) = sql_get_vote(voteid)
    if os.getenv("REQUEST_METHOD") == 'POST':
        if creator != username:
            return my_url()
        a = form.getfirst("a", None)
        if a is None:
            return my_url()
        elif a == 'update_vote':
            title = form.getfirst("title", None)
            description = form.getfirst("description", "")
            allowed_voters = sanitize_allowed_voters(form.getfirst("allowed_voters", ""))
            if title is not None:
                sql_update_vote(voteid, title, description, allowed_voters)
            return my_url()
        elif a == 'add_option':
            name = form.getfirst("name", None)
            if name is not None:
                sql_add_option(voteid, name)
            return my_url()
        elif a == 'remove_option':
            optid = form.getfirst("optid", None)
            if optid is not None:
                sql_remove_option(voteid, optid)
            return my_url()
        elif a == 'remove_voter':
            voter = form.getfirst("voter", None)
            if voter is not None:
                sql_remove_voter(voteid, voter)
            return my_url()
        elif a == 'toggle_close_vote':
            if finished is None:
                sql_close_vote(voteid)
                return my_url() + "../../closed/%s/edit/" % voteid
            else:
                sql_open_vote(voteid)
                return my_url() + "../../../%s/edit/" % voteid
    if creator != username:
        return "<p>Only the owner may edit a vote.</p>"
    if finished is None:
        html = html_vote_toggle_form % {"button": "Close Vote"}
    else:
        html = html_vote_toggle_form % {"button": "Open Vote"}
    html += "<h2>Vote Data</h2>"
    html += html_vote_form % {"title": cgi.escape(title),
                              "description": cgi.escape(description),
                              "allowed_voters": cgi.escape(allowed_voters),
                              "button": "Update Vote"}
    html += "<h2>Options</h2>"
    html += "<ul>"
    for (optid, name) in sql_get_options(voteid):
        html += html_vote_options_form % {"optid": optid,
                                          "name": cgi.escape(name)}
    html += "</ul>"
    html += html_vote_option_add_form
    html += "<h2>Voters</h2>"
    html += "<ul>"
    for (voter, voted) in sql_get_voter_times(voteid):
        html += html_vote_remove_voter_form % {"voter": cgi.escape(voter),
                                               "last_vote": eve_time(voted)}
    html += "</ul>"
    html += '<p><a href="../">View this vote</a></p>'
    return html

def show_docs(**kwargs):
    return html_documentation

########################
### Helper Functions ###
########################

def format(s):
    s = cgi.escape(s)
    s = s.replace("\n\n", "</p><p>")
    s = s.replace("\n", "<br />")
    return "<p>"+s+"</p"

def eve_time(time=None):
    if time is None:
        time = datetime.datetime.utcnow()
    try:
        t = time.strftime("%m.%d %H:%M:%S")
        y = time.year - 1898
        return "%3i.%s" % (y, t)
    except:
        return "never"

def format_vote_result(voteid, verbose):
    voters = sql_get_voters(voteid)
    results = sql_get_results(voteid)
    options = sql_get_options(voteid)
    last_vote = sql_vote_last_vote(voteid)
    ballots = {}
    for (voter, option, value) in results:
        if voter not in ballots:
            ballots[voter] = {}
        ballots[voter][option] = value
    s = Schulze([b for (a, b) in options])
    for ballot in ballots.values():
        s.addBallot(ballot)
    if len(voters) == 1:
        html = "<p>1 vote, last on %s.</p>" % eve_time(last_vote)
    else:
        html = "<p>%i votes, last on %s.</p>" % (len(voters),
                                                 eve_time(last_vote))
    html += "<ol>"
    for rank in s.tally():
        html += "<li>"
        for item in rank:
            html += "%s<br />" % cgi.escape(item)
        html += "</li>"
    html += "</ol>"
    if verbose:
        html += defeat_matrix(s)
    return html

def defeat_matrix(s):
    ranks = s.tally()
    if len(ranks) == 0:
        return html
    html = "<h3>Pairwise Defeats</h3>"
    html += "<ul>"
    (current, ranks) = (ranks[0][0], ranks[1:])
    while len(ranks) > 0:
        (next, ranks) = (ranks[0][0], ranks[1:])
        html += ('<li>%s %i:%i %s</li>' %
                 (cgi.escape(current),
                  s.defeats[current][next],
                  s.defeats[next][current],
                  cgi.escape(next)))
        current = next
    html += "</ul>"
    html += "<h3>Defeat Matrix</h3>"
    html += "<p>Shows the amount of votes that strictly prefer the option on the left over the option on the top.</p>"
    html += '<table class="matrix"><tr><th></th>'
    for n in range(len(s.options)):
        html += "<th>%i</th>" % (n+1)
    html += "<th></th></tr>"
    even = True
    for n1 in range(len(s.options)):
        if even:
            html += '<tr class="even">'
        else:
            html += '<tr class="odd">'
        even = not even
        html += "<th>%i</th>" % (n1+1)
        for n2 in range(len(s.options)):
            if n1 == n2:
                html += "<td></td>"
            else:
                opt1 = s.options[n1]
                opt2 = s.options[n2]
                defeat = s.defeats[opt1][opt2]
                html += "<td>%i</td>" % defeat
        html += ('<th class="side">(%i)&nbsp;%s</th>' %
                 (n1+1,
                  cgi.escape(s.options[n1]).replace(" ", "&nbsp;")))
        html += "</tr>"
    html += "</table>"
    return html

def ballot_form(voteid, options, ballot=None):
    if ballot is None:
        ballot = {}
    else:
        ballot = dict((optid, value) for (optid, name, value) in ballot)
    fields = []
    for (optid, name) in options:
        fields.append((optid, name, ballot.get(optid, "")))
    fields.sort(lambda a, b: valuecmp(a[2], b[2]))
    html = '<form action="" method="post">'
    html += '<p>Rank the choices with numbers. Low numbers are better, high numbers are worse, gaps between numbers do not matter.</p>'
    html += '<p><em>Most preferable</em></p>'
    html += '<table>'
    for (optid, name, value) in fields:
        html += '<tr><td style="margin:0;padding:0;"><input type="text" name="opt%i" value="%s" size="2" /></td><td>%s</td></tr>' % (optid, value, cgi.escape(name))
    html += '<table>'
    html += '<p><em>Least preferable</em></p>'
    html += '<input type="submit" value="Cast Vote" /></form>'
    return html

def valuecmp(a, b):
    if a == "" and b == "":
        return 0
    elif a == "":
        return 1
    elif b == "":
        return -1
    else:
        return cmp(int(a), int(b))

def can_vote(username, allowed_voters):
    allowed = [x.strip() for x in allowed_voters.split("\n") if x.strip() != '']
    if len(allowed) == 0 or username in allowed:
        return True
    else:
        return False

def sanitize_allowed_voters(voters):
    result = []
    for voter in voters.replace("\r", "\n").split("\n"):
        voter = voter.strip()
        if voter != "":
            result.append(voter)
    return "\n".join(result)

#########
## SQL ##
#########

def sql_user_last_vote(username):
    c = db.cursor()
    c.execute("SELECT MAX(created) FROM vote_ballot WHERE voter = %s",
              (username,))
    time = c.fetchone()[0]
    if time is not None:
        return time
    else:
        return "never"

def sql_vote_last_vote(voteid):
    c = db.cursor()
    c.execute("SELECT MAX(created) FROM vote_ballot WHERE vote_id = %s",
              (voteid,))
    time = c.fetchone()[0]
    if time is not None:
        return time
    else:
        return "never"

def sql_get_votes(closed=False):
    c = db.cursor()
    if closed:
        c.execute("SELECT id, title, creator, started, finished FROM vote WHERE finished != 0 ORDER BY started DESC")
    else:
        c.execute("SELECT id, title, creator, started, finished FROM vote WHERE finished = 0 ORDER BY started DESC")
    return c.fetchall()

def sql_get_vote(voteid):
    c = db.cursor()
    c.execute("SELECT title, description, creator, started, finished, allowed_voters FROM vote WHERE id = %s",
              (voteid,))
    if c.rowcount != 1:
        return None
    else:
        return c.fetchone()

def sql_get_voters(voteid):
    c = db.cursor()
    c.execute("SELECT DISTINCT voter FROM vote_ballot WHERE vote_id = %s ORDER BY voter",
              (voteid,))
    return [x for (x,) in c.fetchall()]

def sql_get_voter_times(voteid):
    c = db.cursor()
    c.execute("SELECT voter, MAX(created) FROM vote_ballot WHERE vote_id = %s GROUP BY voter ORDER BY voter",
              (voteid,))
    return c.fetchall()

def sql_get_results(voteid):
    c = db.cursor()
    c.execute("SELECT vb.voter, vo.name, vb.value FROM vote_ballot AS vb INNER JOIN vote_option AS vo ON vb.option_id = vo.id WHERE vb.vote_id = %s",
              (voteid,))
    return c.fetchall()

def sql_get_options(voteid):
    c = db.cursor()
    c.execute("SELECT id, name FROM vote_option WHERE vote_id = %s ORDER BY id ASC",
              (voteid,))
    return c.fetchall()

def sql_get_ballot(voteid, username):
    c = db.cursor()
    c.execute("SELECT vo.id, vo.name, vb.value FROM vote_ballot AS vb INNER JOIN vote_option AS vo ON vb.option_id = vo.id WHERE vb.vote_id = %s AND vb.voter = %s",
              (voteid, username))
    return c.fetchall()

def sql_update_ballot(voteid, username, ballot):
    c = db.cursor()
    c.execute("DELETE FROM vote_ballot WHERE vote_id = %s AND voter = %s",
              (voteid, username))
    for (optid, value) in ballot.items():
        c.execute("INSERT INTO vote_ballot (voter, vote_id, option_id, value, created) VALUES (%s, %s, %s, %s, UTC_TIMESTAMP())",
                  (username, voteid, optid, value))

def sql_create_vote(username, title, description, allowed_voters):
    c = db.cursor()
    c.execute("INSERT INTO vote (title, description, creator, allowed_voters, started) VALUES (%s, %s, %s, %s, UTC_TIMESTAMP())",
              (title, description, username, allowed_voters))
    c.execute("SELECT MAX(id) FROM vote")
    return c.fetchone()[0]

def sql_update_vote(voteid, title, description, allowed_voters):
    c = db.cursor()
    c.execute("UPDATE vote SET title = %s, description = %s, allowed_voters = %s WHERE id = %s",
              (title, description, allowed_voters, voteid))

def sql_add_option(voteid, name):
    c = db.cursor()
    c.execute("INSERT INTO vote_option (vote_id, name) VALUES (%s, %s)",
              (voteid, name))

def sql_remove_option(voteid, optid):
    c = db.cursor()
    c.execute("DELETE FROM vote_option WHERE id = %s AND vote_id = %s",
              (optid, voteid))

def sql_remove_voter(voteid, voter):
    c = db.cursor()
    c.execute("DELETE FROM vote_ballot WHERE vote_id = %s AND voter = %s",
              (voteid, voter))

def sql_close_vote(voteid):
    c = db.cursor()
    c.execute("UPDATE vote SET finished = UTC_TIMESTAMP() WHERE id = %s",
              (voteid,))

def sql_open_vote(voteid):
    c = db.cursor()
    c.execute("UPDATE vote SET finished = 0 WHERE id = %s",
              (voteid,))

############
### HTML ###
############

html_base = """Content-Type: text/html
Cache-Control: no-cache

<?xml version="1.0"e encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link type="text/css" rel="stylesheet" href="/cvote/vote.css" />
<title>Electus Matari Votes</title>
</head>

<body>
<div id="container">
  <a name="top" id="top"></a>

  <div id="header">
    <div class="logo"><a href="http://www.electusmatari.com/forums/index.php"><img src="http://www.electusmatari.com/forums/images/logo.gif" alt="Electus Matari Forums" title="Electus Matari Forums" /></a></div>
    <div class="menu">
      <ul>
        <li><a href="http://www.electusmatari.com/forums/search.php"><img src="http://www.electusmatari.com/forums/images/toplinks/search.gif" alt="" title="" />Search</a></li>
        <li><a href="/standings.cgi"><img src="http://www.electusmatari.com/forums/images/toplinks/standings.png" alt="" />Standings</a></li>
        <li><a href="/killboard/index.php"><img src="http://www.electusmatari.com/forums/images/toplinks/killboard.png" alt="" />Killboard</a></li>
        <li><a href="/wiki/"><img src="http://www.electusmatari.com//forums/images/toplinks/wiki.png" alt="" />Wiki</a></li>
        <li><a href="/tools/"><img src="http://www.electusmatari.com/forums/images/toplinks/tools.png" alt="" />Tools</a></li>
        <li><a href="/auth/"><img src="http://www.electusmatari.com/forums/images/toplinks/auth.png" alt="" />Auth</a></li>
        <li><a href="http://www.electusmatari.com/forums/misc.php?action=help"><img src="http://www.electusmatari.com/forums/images/toplinks/help.gif" alt="" title="" />Help</a></li>
      </ul>
    </div>
    <div id="panel">
      <span style="float:right;"><strong>Current time:</strong> %(current_time)s</span>
      <strong>Welcome, %(username)s</strong>. %(vote_time)s
    </div>%(tabs)s</div><div id="content">
%(content)s
</div>
</body> </html>
"""

html_vote_list_entry = """
<li><a href="%(voteid)s/">%(title)s</a> (%(creator)s on %(started)s)</li>
"""

html_show_vote = """
<h2>%(title)s</h2>
<small>By %(creator)s, %(runtime)s</small>

%(description)s

<h3>Current Result</h3>
%(result)s

<h3>Your Vote</h3>
%(vote_form)s

%(edit)s
"""

html_vote_form = """
<form action="" method="post">
  <input type="hidden" name="a" value="update_vote" />
  <table>
    <tr><th>Title:</th><td><input type="text" name="title" value="%(title)s" /></td></tr>
    <tr><th>Description:</th><td><textarea name="description" cols="23">%(description)s</textarea><td></tr>
    <tr><th>Allowed Voters:</th><td><textarea name="allowed_voters" cols="23">%(allowed_voters)s</textarea></td></tr>
    <tr><th></th><td><p>Newline-separated list of user names. Leave empty to allow everyone to vote.</p><td></tr>
  </table>
  <input type="submit" value="%(button)s" />
</form>
"""

html_vote_toggle_form = """
<form action="" method="post">
  <input type="hidden" name="a" value="toggle_close_vote" />
  <input type="submit" value="%(button)s" />
</form>
"""

html_vote_options_form = """
<li>%(name)s<form action="" method="post">
  <input type="hidden" name="a" value="remove_option" />
  <input type="hidden" name="optid" value="%(optid)s" />
  <input type="submit" value="Remove Option" />
</form></li>
"""

html_vote_option_add_form = """
<form action="" method="post">
  <input type="hidden" name="a" value="add_option" />
  <input type="text" name="name" />
  <input type="submit" value="Add Option" />
</form>
"""

html_vote_remove_voter_form = """
<li>%(voter)s (%(last_vote)s)
<form action="" method="post">
  <input type="hidden" name="a" value="remove_voter" />
  <input type="hidden" name="voter" value="%(voter)s" />
  <input type="submit" value="Remove" />
</form>
"""

html_documentation = """
<p>This is a <a href="http://en.wikipedia.org/wiki/Condorcet_method">Condorcet</a>-based
voting tool. This means that votes consist of <em>rankings</em> of
options, and the tool will find that option which is preferred over
other options by the most voters.</p>

<p>To cast your vote, simply rank each option with an integer. A lower
integer means &quot;more liked,&quot; a higher integer means
&quot;less liked.&quot; The exact numbers you use are irrelevant, only
the order in which you put the options is. You can also rank multiple
options the same. Any option you leave blank will be considered
less-liked than any other option you have, and equally liked to each
other.</p>
"""

main()
