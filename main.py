"""
    Copyright
    Jose Salinas & Jasper Refuerzo
    08/19/201
"""

import os
import csv
from datetime import datetime

from flask import Flask
from flask import render_template

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import jsonify

#############
#  CONFIGS  #
#############

app = Flask(__name__)

database = SQLAlchemy(app)
marshmallow = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'

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

database.create_all()
for ballot in ballots:
    database.session.add(ballot)
for candidate in candidates:
    database.session.add(candidate)
database.session.commit()

#LOAD SCHEMAS
ballot_schema = BallotSchema()
candidate_schema = CandidateSchema()

#########
#  APP  #
#########

@app.route('/')
def main_page():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/vote')
def vote_page():
    return render_template('vote.html')

@app.route('/verify')
def verify_page():
    return render_template('verify.html')

@app.route('/logout')
def logout_page():
    return render_template('logout.html')

@app.route('/debug')
def debug():
    result = [
        candidate_schema.dump(candidate).data
        for candidate in Candidate.query.all()
    ]
    return jsonify(result)

if __name__ == "__main__":
    app.run()
