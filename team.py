from models import db, Team, Account, User, Membership
from flask import *
from functions import *
from gatekeeper import *

import pprint

team = Blueprint('team', __name__, template_folder='templates')

@team.route('/dashboard/team')
@team.route('/team')
def teamEndpoint():
    res = checkLogin()
    if res:
        teams = Team.query.filter_by(account_id=session['account_id']).all()
        return render_template("dashboard_team_view.html", teams=teams)
    else:
        return notLoggedIn()

def getAllUsers(account_id):
    users = User.query.filter_by(account_id=account_id).all()
    return users

def getMemberList(team_id):
    members = db.session.query(User).join(Membership, Membership.user_id==User.id).filter(Membership.team_id==team_id).all()
    return members

def getTeamLeaderName(account_id, id):
    teamLeader = User.query.filter_by(account_id=account_id, id=id).first()
    return teamLeader.name

def addLeaderMembership(account_id, id, team_id):
    newMembership = Membership(account_id, id, team_id, is_admin=1)
    db.session.add(newMembership)
    db.session.commit()

def removeAdminMembership(account_id, id, team_id):
    membership = Membership.query.filter_by(account_id=account_id, user_id=id).first()
    membership.is_admin = 0
    db.session.commit()

def addAdminMembership(account_id, id, team_id):
    membership = Membership.query.filter_by(account_id=account_id, user_id=id).first()
    membership.is_admin = 1
    db.session.commit()

def addMembership(account_id, user_id, team_id):
    newMembership = Membership(account_id, user_id, team_id, is_admin=0)
    db.session.add(newMembership)
    db.session.commit()

def getTeamID(team):
    db.session.refresh(team)
    return team.id

@team.route('/dashboard/team/edit/<team_id>', methods=['POST','GET'])
@team.route('/team/edit/<team_id>', methods=['POST','GET'])
@team.route('/dashboard/team/<team_id>', methods=['POST','GET'])
@team.route('/team/<team_id>', methods=['POST','GET'])
def specificTeam(team_id):
    res = checkLogin()
    if res:
        if request.method == "GET":
            gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 4)
            if gatekeeper:
                users = getAllUsers(session['account_id'])
                team = Team.query.filter_by(id=team_id).filter_by(account_id=session['account_id']).first()
                members = getMemberList(team.id)
                membership = Membership.query.filter_by(account_id=session['account_id']).filter_by(team_id=team_id).all()
                return render_template("dashboard_team_edit.html", team=team, users=users, members=members,
                membership=membership)
            else:
                return render_template("permission_denied.html")
        elif request.method == "POST":
            gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 3)
            if gatekeeper:
                # update the stuff
                team = Team.query.filter_by(id=team_id).first()
                team.team_name = request.form['name']
                team.team_leader_id = request.form['leader']
                team.team_leader_name = getTeamLeaderName(session['account_id'], request.form['leader'])
                db.session.commit()
                return redirect('/dashboard/team')
            else:
                return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/create', methods=['POST','GET'])
@team.route('/team/create', methods=['POST','GET'])
def teamCreate():
    res = checkLogin()
    if res:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 1)
        if gatekeeper:
            if request.method == "GET":
                users = getAllUsers(session['account_id'])
                return render_template("dashboard_team_create.html", users=users)
            elif request.method == "POST":
                if request.form['name'] and request.form['leader']:
                    team_leader_name = getTeamLeaderName(session['account_id'], request.form['leader'])
                    newTeam = Team(session['account_id'], request.form['name'], team_leader_name, request.form['leader'])
                    db.session.add(newTeam)
                    db.session.commit()
                    addLeaderMembership(session['account_id'], request.form['leader'], getTeamID(newTeam))
                    return redirect('/dashboard/team')
                else:
                    return render_template('/dashboard/team/create', users=getAllUsers(session['account_id']), error="A team name is required.")
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/delete/<team_id>', methods=['POST','GET'])
@team.route('/team/delete/<team_id>', methods=['POST','GET'])
def teamDelete(team_id):
    res = checkLogin()
    if res:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 2)
        if gatekeeper:
            if request.method == "GET":
                return render_template('dashboard_team_delete.html', team_id=team_id)
            elif request.method == "POST":
                team = Team.query.filter_by(id=team_id).first()
                members = Membership.query.filter_by(team_id=team_id, account_id=session['account_id']).all()
    
                for member in members:
                    db.session.delete(member)
                    db.session.delete(team)
                    db.session.commit()
                    return redirect('/dashboard/team')
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/<team_id>/user/add/<user_id>', methods=['POST','GET'])
@team.route('/team/<team_id>/user/add/<user_id>', methods=['POST','GET'])
def teamAddSpecificUser(team_id, user_id):
    res = checkLogin()
    if res:
        gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 3)
        if gatekeeper:
            team = Team.query.filter_by(id=team_id).first()
            user = User.query.filter_by(id=user_id).first()
            addMembership(session['account_id'], user.id, team.id)
            return redirect('/dashboard/team/%s' % str(team.id))
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/<team_id>/user/add', methods=['GET'])
def teamAddUser(team_id):
    res = checkLogin()
    if res:
        gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 3)
        if gatekeeper:
            if team_id:
                team = Team.query.filter_by(id=team_id).first()
                users = getAllUsers(session['account_id'])
                return render_template("dashboard_team_add_user.html", team=team, users=users)
            else:
                team = Team.query.filter_by(id=team_id).first()
                return render_template('/dashboard/team/%s' % str(team_id), team=team)
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()
    

@team.route('/dashboard/team/<team_id>/user/delete/<user_id>', methods=['POST','GET'])
@team.route('/team/<team_id>/user/delete/<user_id>', methods=['POST','GET'])
def teamDeleteUser(user_id, team_id):
    res = checkLogin()
    if res:
        gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 3)
        if gatekeeper:
            if team_id and user_id:
                if request.method == "GET":
                    return render_template('dashboard_team_user_delete.html', user_id=user_id, team_id=team_id)
                elif request.method == "POST":
                    membership = Membership.query.filter_by(account_id=session['account_id'], user_id=user_id, team_id=team_id).first()
                    db.session.delete(membership)
                    db.session.commit()
                    return redirect('/dashboard/team/%s' % str(team_id))
            else:
                return redirect('/dashboard/team/%s' % str(team_id))
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/<team_id>/user/promote/<user_id>')
def teamPromoteUser(user_id, team_id):
    res = checkLogin()
    if res:
        gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 3)
        if gatekeeper:
            if team_id and user_id:
                user = User.query.filter_by(id=user_id).first()
                addAdminMembership(session['account_id'], user.id, team_id)
                return redirect('/dashboard/team/%s' % str(team_id))
            else:
                return redirect('/dashboard/team/%s' % str(team_id))
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/<team_id>/user/demote/<user_id>')
def teamDemoteUser(user_id, team_id):
    res = checkLogin()
    if res:
        gatekeeper = teamGatekeeper(session['user_id'], team_id, session['account_id'], 3)
        if gatekeeper:
            if team_id and user_id:
                user = User.query.filter_by(id=user_id).first()
                removeAdminMembership(session['account_id'], user.id, team_id)
                return redirect('/dashboard/team/%s' % str(team_id))
            else:
                return redirect('/dashboard/team/%s' % str(team_id))
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

