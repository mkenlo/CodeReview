from sqlalchemy import (Column, Integer,
                        String, Date, DateTime, Text, Boolean, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import psycopg2
import datetime

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    fullname = Column(String(250), nullable=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    social_id = Column(String(250), nullable=True)
    joined_on = Column(DateTime, default=datetime.datetime.now)
    user_level = Column(Integer)
    aboutme = Column(Text)
    location = Column(String(250))
    skills = Column(Text)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag = Column(String(250))
    description = Column(String(250))
    slug = Column(String(250))


class Problem(Base):
    __tablename__ = 'problem'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    isSolved = Column(Boolean)
    solution_desc = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)
    solution_lang = Column(String(250), nullable=True)
    created_by = Column(ForeignKey('users.id'))
    author = relationship(Users)
    category_id = Column(ForeignKey('category.id'))
    category = relationship(Category)


class CodeReview(Base):
    __tablename__ = 'codeReview'
    id = Column(Integer, primary_key=True)
    code = Column(Text, nullable=False)
    code_lang = Column(String(250), nullable=False)
    submitted_by = Column(ForeignKey('users.id'))
    problem_id = Column(ForeignKey('problem.id'), nullable=False)
    problem = relationship(Problem)
    author = relationship(Users)
    is_reviewed = Column(Boolean, default=False)
    submitted_on = Column(DateTime, default=datetime.datetime.now)
    reviewed_on = Column(DateTime)


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    submitted_by = Column(ForeignKey('users.id'))
    author = relationship(Users)
    review_id = Column(ForeignKey('codeReview.id'))
    review = relationship(CodeReview)
    posted = Column(DateTime, default=datetime.datetime.now)


class Language(Base):
    __tablename__ = "language"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(100))


engine = create_engine(
    'postgresql://postgres:admin@localhost/codereview')
Base.metadata.create_all(engine)
