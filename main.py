"""
    Copyright
    Jose Salinas & Jasper Refuerzo
    08/19/201
"""

from flask import Flask
from flask import render_template

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

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

    ballotTime = database.Column(database.datetime)
    ballotIsComplete = database.Column(database.Boolean)

class BallotSchema(marshmallow.ModelSchema):
        class Meta:
            model = Ballot

class Candidate(database.Model):
    __tablename__ = "candidates"

    candidateID = database.Column(database.Integer, primary_key=True)
    candidatePosition = database.Column(database.Integer)
    candidateBatch = database.Column(database.Integer)
    candidateLName = database.Column(database.String(50))
    candidateFName = database.Column(database.String(50))
    candidateTotalVotes = database.Column(database.Integer)

    candidateTime = database.Column(database.Column)

class CandidateSchema(marshmallow.ModelSchema):
    class Meta:
        model = Candidate

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

if __name__ == "__main__":
    app.run()
