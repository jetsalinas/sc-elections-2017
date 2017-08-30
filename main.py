"""
Election platform for PSHS-MC Student/Batch Council elections.

:Author:     Jose Salinas
:Author:     Jasper Refuerzo
:Author:     Maded Batara III
:Version:    v20170827
"""

import csv
import os

from datetime import datetime
from keys import SESSION_SECRET_KEY

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from flask_heroku import Heroku
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

#############
#  CONFIGS  #
#############

app = Flask(__name__)

if 'DYNO' in os.environ:
    import psycopg2
    hr = Heroku(app)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'

database = SQLAlchemy(app)
marshmallow = Marshmallow(app)
app.secret_key = SESSION_SECRET_KEY

#############
#  SCHEMAS  #
#############

class Ballot(database.Model):
    __tablename__ = "ballots"

    ballotID = database.Column(database.Integer, primary_key=True)
    ballotBatch = database.Column(database.Integer)
    ballotLName = database.Column(database.String(50))
    ballotFName = database.Column(database.String(50))

    ballotPresident = database.Column(database.Integer)
    ballotVicePresident = database.Column(database.Integer)
    ballotSecretary = database.Column(database.Integer)
    ballotTreasurer = database.Column(database.Integer)
    ballotAuditor = database.Column(database.Integer)

    ballotTime = database.Column(database.String)
    ballotIsComplete = database.Column(database.Boolean)

class BallotSchema(marshmallow.ModelSchema):
    class Meta:
        model = Ballot

class Candidate(database.Model):
    __tablename__ = "candidates"

    candidateID = database.Column(database.Integer, primary_key=True)
    candidatePosition = database.Column(database.Integer)
    candidateAffiliation = database.Column(database.String(50))
    candidateBatch = database.Column(database.Integer)
    candidateLName = database.Column(database.String(50))
    candidateFName = database.Column(database.String(50))
    candidateTotalVotes = database.Column(database.Integer)

    candidateTime = database.Column(database.String)

class CandidateSchema(marshmallow.ModelSchema):
    class Meta:
        model = Candidate

class Security(database.Model):
    __tablename__ = "security"

    securityID = database.Column(database.Integer, primary_key=True)
    securityUName = database.Column(database.String(50))
    securityPassword = database.Column(database.String(50))

class SecuritySchema(marshmallow.ModelSchema):
    class Meta:
        model = Security

# LOAD DATABASE
ballots =[]
with open("ballotlist.csv") as ballot_csv:
    ballot_list = csv.reader(ballot_csv)
    for row in ballot_list:
        ballots.append(Ballot(
            ballotID = row[0],
            ballotBatch = row[1],
            ballotLName = row[2],
            ballotFName = row[3],
            ballotPresident = None,
            ballotVicePresident = None,
            ballotSecretary = None,
            ballotTreasurer = None,
            ballotAuditor = None,
            ballotTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            ballotIsComplete = False
        ))

candidates = []
with open("candidatelist.csv") as candidate_csv:
    candidate_list = csv.reader(candidate_csv)
    for row in candidate_list:
        candidates.append(Candidate(
            candidateID = row[0],
            candidatePosition = row[1],
            candidateAffiliation = row[2],
            candidateBatch = row[3],
            candidateLName = row[4],
            candidateFName = row[5],
            candidateTotalVotes = 0,
            candidateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        ))

credentials = []
with open("securitylist.csv") as security_csv:
    security_list = csv.reader(security_csv)
    for row in security_list:
        credentials.append(Security(
            securityID = row[0],
            securityUName = row[1],
            securityPassword = row[2]
        ))

def clear_database():
    database.reflect()
    database.drop_all()

def start_database():
    database.create_all()
    for ballot in ballots:
        database.session.add(ballot)
    for candidate in candidates:
        database.session.add(candidate)
    for security in credentials:
        database.session.add(security)
    database.session.commit()

try:
    start_database()
except:
    None

#LOAD SCHEMAS
ballot_schema = BallotSchema()
candidate_schema = CandidateSchema()
security_schema = SecuritySchema()

#########
#  APP  #
#########

def validate_session():
    try:
        if session['userID']:
            return True
        return False
    except:
        return False

def validate_login(username, password):
    user = Security.query.filter_by(securityUName=username).first()
    if user == None:
        return False
    if username == user.securityUName:
        if password == user.securityPassword:
            load_session_data(userID=user.securityID)
            return True
    return False

def load_session_data(userID):
    user = Ballot.query.filter_by(ballotID=userID).first()
    if user == None:
        return None
    session['userID'] = user.ballotID
    session['userBatch'] = user.ballotBatch
    session['userLName'] = user.ballotLName
    session['userFName'] = user.ballotFName
    session['userTime'] = user.ballotTime
    session['userPresident'] = user.ballotPresident
    session['userVicePresident'] = user.ballotVicePresident
    session['userSecretary'] = user.ballotSecretary
    session['userTreasurer'] = user.ballotTreasurer
    session['userAuditor'] = user.ballotAuditor
    session['userIsComplete'] = user.ballotIsComplete
    result = [
        ballot_schema.dump(user)
    ]
    return jsonify(result)

@app.route('/')
def main_page():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = False
    #SKIP LOG IN PAGE IF A USER IS ALREADY LOGGED IN
    if validate_session():
        load_session_data(userID=session['userID'])
        return redirect(url_for('vote_page'))
    #PROCESS LOGIN REQUESTS
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_login(username=username, password=password):
            load_session_data(userID=session['userID'])
            session['fromVote'] = False
            return redirect(url_for('vote_page'))
        else:
            error = True
    #SHOW LOGIN PAGE
    try:
        fromVote = session['fromVote']
    except:
        session['fromVote'] = False
        fromVote = session['fromVote']
    clear_session()
    return render_template('login.html', error=error, fromVote=fromVote)

def validate_choices(requestform):
    isValid = True
    choicePresident = int(requestform['presidentForm'])
    choiceVicePresident = int(requestform['vicePresidentForm'])
    choiceSecretary = int(requestform['secretaryForm'])
    choiceTreasurer = int(requestform['treasurerForm'])
    choiceAuditor = int(requestform['auditorForm'])

    if Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2000).filter_by(candidateID=choicePresident).first():
        session['userPresident'] = choicePresident
    else:
        isValid = False
    if Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2001).filter_by(candidateID=choiceVicePresident).first():
        session['userVicePresident'] = choiceVicePresident
    else:
        isValid = False
    if Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2002).filter_by(candidateID=choiceSecretary).first():
        session['userSecretary'] = choiceSecretary
    else:
        isValid = False
    if Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2003).filter_by(candidateID=choiceTreasurer).first():
        session['userTreasurer'] = choiceTreasurer
    else:
        isValid = False
    if Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2004).filter_by(candidateID=choiceAuditor).first():
        session['userAuditor'] = choiceAuditor
    else:
        isValid = False
    return isValid

@app.route('/vote', methods=['GET', 'POST'])
def vote_page():
    error = False
    session['formValid'] = False
    #REDIRECT TO VERIFICATION IF VOTING IS COMPLETE
    if session['userIsComplete']:
        return redirect(url_for('verify_page'))
    #PROCESS VOTE REQUESTS
    if request.method == 'POST':
        if validate_choices(requestform=request.form):
            session['formValid'] = True
            return redirect(url_for('verify_page'))
        else:
            error=True

    #SHOW VOTE PAGE IF LOGGED IN
    if validate_session():
        presidentList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2000)
        vicePresidentList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2001)
        secretaryList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2002)
        treasurerList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2003)
        auditorList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2004)
        return render_template('vote.html',
        presidentList=presidentList,
        vicePresidentList=vicePresidentList,
        secretaryList=secretaryList,
        treasurerList=treasurerList,
        auditorList=auditorList,
        error=error)

    return redirect(url_for('login_page'))

def commit_ballot():
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotPresident = session['userPresident']
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotVicePresident = session['userVicePresident']
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotSecretary = session['userSecretary']
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotTreasurer = session['userTreasurer']
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotAuditor = session['userAuditor']
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    Ballot.query.filter_by(ballotID=session['userID']).first().ballotIsComplete = True
    session['userIsComplete'] = True
    database.session.commit()

def commit_candidate():
    Candidate.query.filter_by(candidateID=session['userPresident']).first().candidateTotalVotes += 1
    Candidate.query.filter_by(candidateID=session['userVicePresident']).first().candidateTotalVotes += 1
    Candidate.query.filter_by(candidateID=session['userSecretary']).first().candidateTotalVotes += 1
    Candidate.query.filter_by(candidateID=session['userTreasurer']).first().candidateTotalVotes += 1
    Candidate.query.filter_by(candidateID=session['userAuditor']).first().candidateTotalVotes += 1
    Candidate.query.filter_by(candidateID=session['userPresident']).first().candidateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    database.session.commit()

def clear_session():
    session['userID'] = None
    session['username'] = None
    session['userBatch'] = None
    session['userLName'] = None
    session['userFName'] = None
    session['userTime'] = None
    session['userPresident'] = None
    session['userVicePresident'] = None
    session['userSecretary'] = None
    session['userTreasurer'] = None
    session['userAuditor'] = None
    session['userIsComplete'] = False
    session['formValid'] = False

@app.route('/verify', methods=['GET', 'POST'])
def verify_page():
    session['fromVote'] = False
    #SAVE VOTES
    if request.method == 'POST':
        if not session['userIsComplete']:
            if session['formValid']:
                commit_ballot()
                commit_candidate()
                clear_session()
                session['fromVote'] = True
        clear_session()
        return redirect(url_for('login_page'))

    if validate_session():
        if session['formValid'] or session['userIsComplete']:
            choicePresident = Candidate.query.filter_by(candidateID=session['userPresident']).first()
            choiceVicePresident = Candidate.query.filter_by(candidateID=session['userVicePresident']).first()
            choiceSecretary = Candidate.query.filter_by(candidateID=session['userSecretary']).first()
            choiceTreasurer = Candidate.query.filter_by(candidateID=session['userTreasurer']).first()
            choiceAuditor = Candidate.query.filter_by(candidateID=session['userAuditor']).first()
            return render_template('verify.html', choicePresident=choicePresident, choiceVicePresident=choiceVicePresident, choiceSecretary=choiceSecretary, choiceTreasurer=choiceTreasurer, choiceAuditor=choiceAuditor)
        else:
            return redirect(url_for('vote_page'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    clear_session()
    return redirect(url_for('login_page'))

@app.route('/debug/ballots')
def debug():
    result = [
        ballot_schema.dump(ballot).data
        for ballot in Ballot.query.all()
    ]
    return jsonify(result)

@app.route('/debug/candidates')
def debug2():
    result = [
        candidate_schema.dump(candidate).data
        for candidate in Candidate.query.all()
    ]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=False)
