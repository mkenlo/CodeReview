from database_setup import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import utils.utils


# connect with the database
engine = create_engine(
    'postgresql+psycopg2://postgres:admin@localhost/codereview')
# create a connection between the database and the class from database_setup
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()
PER_PAGE = 12

# CRUD functions for Users Table


def addUser(username, email, password, social_id=''):

    password = utils.secure_password(password)
    newUser = Users(username=username,
                    email=email, password=password,
                    social_id=social_id,
                    user_level=5)
    # if first User, Set him admin
    if not getAllUsers():
        newUser.user_level = 10
    session.add(newUser)
    session.commit()


def editUser(email, userinfo):
    user = getUserByEmail(email)
    if 'fullname' in userinfo:
        user.fullname = userinfo['fullname']
    if 'aboutme' in userinfo:
        user.aboutme = userinfo['aboutme']
    if 'location' in userinfo:
        user.location = userinfo['location']
    if 'skills' in userinfo:
        user.skills = userinfo['skills']

    session.add(user)
    session.commit()


def deleteAllUsers():
    print "-------Deleting all users from DB"
    session.query(Users).delete()
    session.commit()


def deleteUser(user_id):
    user = session.query(Users).get(user_id)
    if user:
        session.delete(user)
        session.commit()


def getAllUsers():
    return session.query(Users).all()


def getUserByEmail(emailAdr):
    return session.query(Users).filter_by(email=emailAdr).first()


def getUserBySocialId(social_id, username):
    return session.query(Users).filter_by(social_id=social_id,
                                          username=username).first()


def addProblem(problem, author_email):
    author = getUserByEmail(author_email)
    new_problem = Problem(title=problem["title"],
                          description=problem["desc"],
                          solution_desc=" ",
                          solution_lang=problem["lang"],
                          solution_code=problem["solution"],
                          category_id=problem['cat_id'],
                          created_by=author.id,
                          author=author
                          )
    session.add(new_problem)
    session.commit()


def editProblem(pb_id, solution, language):
    problem = session.query(Problem).get(pb_id)
    problem.solution_code = solution
    problem.solution_lang = language
    session.add(problem)
    session.commit()


def getAllProblems(total=False, offset=1):
    query = session.query(Problem)
    if total:
        return query.count()
    else:
        query = query.limit(PER_PAGE)
        query = query.offset((PER_PAGE * offset) - PER_PAGE)
    return query.all()


def getProblemByID(pb_id):
    return session.query(Problem).get(pb_id)


def getCategories():
    return session.query(Category).all()


def getLanguages():
    return session.query(Language).all()


def getAllReviews():
    return session.query(CodeReview)


def addCodeToReview(code, language, problem_id, coder_id):
    code_to_review = CodeReview(code=code,
                                code_lang=language,
                                problem_id=problem_id,
                                submitted_by=coder_id)
    session.add(code_to_review)
    session.commit()


def getCodeReview(review_id):
    return session.query(CodeReview).get(review_id)


def getUserCodeToReview(user_id, count=False, offset=1):
    query = session.query(CodeReview).filter_by(submitted_by=user_id)
    if count:
        return query.count()
    else:
        query = query.limit(PER_PAGE).offset((PER_PAGE * offset) - PER_PAGE)
        return query


def getComments(review_id):
    return session.query(Comments).filter_by(review_id=review_id).all()


def commentReview(review_id, comment, reviewer_email):
    author = getUserByEmail(reviewer_email)
    comment = Comments(message=comment,
                       review_id=review_id,
                       submitted_by=author.id)
    code_to_review = getCodeReview(review_id)
    if not code_to_review.is_reviewed:
        code_to_review.is_reviewed = True
        session.add(code_to_review)
    session.add(comment)
    session.commit()
