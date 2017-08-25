"""
    Copyright
    Jose Salinas & Jasper Refuerzo
    08/19/201
"""

import os
import csv
from keys import SESSION_SECRET_KEY
from datetime import datetime

from flask import Flask, render_template, jsonify
from flask import session, request, redirect, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

#############
#  CONFIGS  #
#############

app = Flask(__name__)

database = SQLAlchemy(app)
marshmallow = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
app.secret_key = SESSION_SECRET_KEY

database.drop_all()
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

#LOAD DATABASE
ballots =[]
with open("ballotlist.csv") as ballot_csv:
    ballot_list = csv.reader(ballot_csv)
    for row in ballot_list:
        ballots.append(Ballot(
        ballotID = row[0],
        ballotBatch = row[1],
        ballotLName = row[2],
        ballotFName = row[3],
        ballotPresident = 0,
        ballotVicePresident = 0,
        ballotSecretary = 0,
        ballotTreasurer = 0,
        ballotAuditor = 0,
        ballotTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
        candidateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))


securitys = []
with open("securitylist.csv") as security_csv:
    security_list = csv.reader(security_csv)
    for row in security_list:
        securitys.append(Security(
        securityID = row[0],
        securityUName = row[1],
        securityPassword = row[2]
        ))

database.create_all()
for ballot in ballots:
    database.session.add(ballot)
for candidate in candidates:
    database.session.add(candidate)
for security in securitys:
    database.session.add(security)
database.session.commit()

#LOAD SCHEMAS
ballot_schema = BallotSchema()
candidate_schema = CandidateSchema()
security_schema = SecuritySchema()

#########
#  APP  #
#########

def validate_session():
    try:
        if session['username'] == None or session['username']:
            return True
    except:
        return False

def validate_login(username, password):
    user = Security.query.filter_by(securityUName=username).first()
    if user == None:
        return False
    if username == user.securityUName:
        if password == user.securityPassword:
            session['userID'] = user.securityID
            session['username'] = user.securityUName
            user = Ballot.query.filter_by(ballotID=session['userID']).first()
            session['userBatch'] = user.ballotBatch
            session['userLName'] = user.ballotLName
            session['userFName'] = user.ballotFName
            session['userTime'] = user.ballotTime
            session['userPresident'] = user.ballotPresident
            session['userVicePresident'] = user.ballotVicePresident
            session['userSecretary'] = user.ballotSecretary
            session['userTreasurer'] = user.ballotTreasurer
            session['userAuditor'] = user.ballotAuditor
            return True
    return False

@app.route('/')
def main_page():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    #SKIP LOG IN PAGE IF A USER IS ALREADY LOGGED IN
    if validate_session():
        if session['username']:
            return redirect(url_for('vote_page'))
    #PROCESS LOGIN REQUESTS
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_login(username=username, password=password):
            return redirect(url_for('vote_page'))
    #SHOW LOGIN PAGE
    return render_template('login.html')

def validate_choice(query, parameter):
    result = query.filter_by(candidateID=parameter).first()
    if not result == None:
        return True
    return False

@app.route('/vote', methods=['GET', 'POST'])
def vote_page():
    #PROCESS VOTE REQUESTS
    if request.method == 'POST':
        session['userTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['userPresident'] = int(request.form['presidentForm'])
        session['userVicePresident'] = int(request.form['vicePresidentForm'])
        session['userSecretary'] = int(request.form['secretaryForm'])
        session['userTreasurer'] = int(request.form['treasurerForm'])
        session['userAuditor'] = int(request.form['auditorForm'])
#        if validate_choice(query=presidentList, parameter=session['userPresident']) and validate_choice(query=vicePresidentList, parameter=session['userVicePresident']) and validate_choice(query=secretaryList, parameter=session['userSecretary']) and validate_choice(query=treasurerList, parameter=session['userTreasurer']) and validate_choice(query=auditorList, parameter=session['userAuditor']):
        return redirect(url_for('verify_page'))

    #SHOW VOTE PAGE IF LOGGED IN
    if validate_session():
        if session['username']:
            presidentList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2000)
            vicePresidentList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2001)
            secretaryList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2002)
            treasurerList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2003)
            auditorList = Candidate.query.filter_by(candidateBatch=session['userBatch']).filter_by(candidatePosition=2004)
            return render_template('vote.html', presidentList=presidentList, vicePresidentList=vicePresidentList, secretaryList=secretaryList, treasurerList=treasurerList, auditorList=auditorList)

    return redirect(url_for('login_page'))

@app.route('/verify', methods=['GET', 'POST'])
def verify_page():
    #SAVE VOTES
    if request.method == 'POST':
        #choicePresident = Candidate.query.filter_by(candidateID=session['userPresident']).first()
        #choiceVicePresident = Candidate.query.filter_by(candidateID=session['userVicePresident']).first()
        #choiceSecretary = Candidate.query.filter_by(candidateID=session['userSecretary']).first()
        #choiceTreasurer = Candidate.query.filter_by(candidateID=session['userTreasurer']).first()
        #choiceAuditor = Candidate.query.filter_by(candidateID=session['userAuditor']).first()

        #choicePresident.candidateTotalVotes = choicePresident.candidateTotalVotes + 1
        #choicePresident.candidateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #choiceVicePresident.candidateTotalVotes = choiceVicePresident.candidateTotalVotes + 1
        #choiceVicePresident.candidateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #choiceSecretary.candidateTotalVotes = choicePresident.candidateTotalVotes + 1
        #choiceSecretary.candidateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #choiceTreasurer.candidateTotalVotes = choiceTreasurer.candidateTotalVotes + 1
        #choiceTreasurer.candidateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #choiceAuditor.candidateTotalVotes = choiceAuditor.candidateTotalVotes + 1
        #choiceAuditor.candidateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        database.session.commit()
        return redirect(url_for('logout_page'))

    if validate_session():
        if session['username']:
            choicePresident = Candidate.query.filter_by(candidateID=session['userPresident']).first()
            choiceVicePresident = Candidate.query.filter_by(candidateID=session['userVicePresident']).first()
            choiceSecretary = Candidate.query.filter_by(candidateID=session['userSecretary']).first()
            choiceTreasurer = Candidate.query.filter_by(candidateID=session['userTreasurer']).first()
            choiceAuditor = Candidate.query.filter_by(candidateID=session['userAuditor']).first()
            return render_template('verify.html', choicePresident=choicePresident, choiceVicePresident=choiceVicePresident, choiceSecretary=choiceSecretary, choiceTreasurer=choiceTreasurer, choiceAuditor=choiceAuditor)
    return redirect(url_for('login_page'))

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

@app.route('/logout')
def logout_page():
    clear_session()
    return render_template('logout.html')

if __name__ == "__main__":
    app.run()
