from database_setup import Base, Users, Problem, Category, Language, Tags, CodeReview
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2
import utils
import datetime


# connect with the database
engine = create_engine(
    'postgresql+psycopg2://postgres:admin@localhost/codereview')
# create a connection between the database and the class from database_setup
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


# CRUD functions for Users Table
def addUser(username, email, password, social_id=''):

    password = utils.secure_password(password)
    newUser = Users(username=username,
                    email=email, password=password,
                    social_id=social_id,
                    joined_on=datetime.date.today())
    session.add(newUser)
    session.commit()


def editUser(user_id, name):
    user = session.query(Users).get(user_id)


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


def getAllProblems():
    return session.query(Problem).all()


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


def editReview(review_id, comments, reviewer):
    code_to_review = getCodeReview(review_id)
    code_to_review.comments = comments
    code_to_review.reviewed_by = reviewer
    code_to_review.hasbeen_reviewed = True
    session.add(code_to_review)
    session.commit()


def getCodeReview(review_id):
    return session.query(CodeReview).get(review_id)
