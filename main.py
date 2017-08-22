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
    candidateAffiliation = database.Column(database.Integer)
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

@app.route('/vote')
def vote_page():
    #SHOW VOTE PAGE IF LOGGED IN
    if validate_session():
        if session['username']:
            return render_template('vote.html')
    #PROCESS VOTE REQUESTS
    return redirect(url_for('login_page'))

@app.route('/verify')
def verify_page():
    if validate_session():
        if session['username']:
            return render_template('verify.html')
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_page():
    session['username'] = None
    return render_template('logout.html')

if __name__ == "__main__":
    app.run()
