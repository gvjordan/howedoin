import md5
from datetime import *

# INPUT: team id, user id, account id (all ints), item (string)
# OUTPUT: a hash that represents a token for rating auth

def makeToken(team_id, user_id, account_id, item, db):
    try:
        token = md5.new()
        token.update(team_id)
        token.update(user_id)
        token.update(account_id)
        token.update(item)
        token.update(datetime.datetime.now())
        newToken = Token(account_id, user_id, token.hexdigest())
        db.session.add(newToken)
        db.session.commit()
        return True
    except Exception, e:
        error_log(e, "ERROR")
        return False

def makeIdentity(user_hash, db):
    try:
        newIdentity = Rater(user_hash)
        db.session.add(newIdentity)
        db.session.commit()
        return True
    except Exception, e:
        error_log(e, "ERROR")
        return False

def makeIdentityHash(ip):
    try:
        user_hash = md5.new()
        user_hash.update(ip)
        user_hash.update(datetime.datetime.now())
        return user_hash.hexdigest()
    except Exception, e:
        error_log(e, "ERROR")
        return 0
    
def checkIdentity(user_hash, db):
    try:
        identity = Rater.query.filter_by(user_hash=user_hash).all()
        if identity:
            return True
        else:
            return False
    except Exception, e:
        error_log(e, "ERROR")
        return 0

def checkCookie(request, user_hash):
    try:
        if request.cookies.get('howedoin_%s' % user_hash):
            return True
        else:
            return False
    except Exception, e:
        error_log(e, "ERROR")
        return 0

def error_log(error, level):
    try:
        error_log = open('howedoin.log', 'w+')
        date = datetime.datetime.now()
        error_string = "[%s] [%s] - %s" % (str(date), level, error)
        error_log.write(error_string)
        error_log.close()
    except:
        pass

