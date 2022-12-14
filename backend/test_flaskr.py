import os
import unittest

from flask import json

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):

    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "question": "What movie earned Tom Hanks his ..test"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_category_questions(self):
        """test success of getting questions by categories"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        # check status code, success message, num of questions and current category ------------------------------
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/delete/55500")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=2300")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_paginate_questions(self):
        """Tests question pagination success"""
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_question(self):
        """ Tests question delete success """
        # create a new question which will be deleted
        question = Question(question="question to test?",
                            answer='yes', category=2, difficulty=2)
        question.insert()
        q_id = question.id

        questions_before = Question.query.all()

        response = self.client().delete('/questions/delete/{}'.format(q_id))
        data = json.loads(response.data)

        questions_after = Question.query.all()
        question = Question.query.filter(Question.id == 1).one_or_none()

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], q_id)
        self.assertTrue(len(questions_before) - len(questions_after) == 1)
        self.assertEqual(question, None)

    def test_create_question(self):
        """Tests question creation"""

        # get questions before post. Create question, load response data     and get num questions after
        questions_before = len(Question.query.all())

        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        questions_after = len(Question.query.all())

        # check status code, success message & compare length before & after to check if questions increased in database
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(questions_after, questions_before + 1)

    def test_422_create_question(self):
        """test failure of question creation error 400"""
        # get num of questions before post, create question without json data --------------------------
        questions_before = Question.query.all()

        response = self.client().post('/questions', json={})
        data = json.loads(response.data)
        questions_after = Question.query.all()

        # check status code, false success message  and compare length before & after -----------------------------
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(questions_before) == len(questions_after))

    def test_get_allcategories(self):
        """ Tests success of loading categories"""
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        # chech if key success is true
        self.assertEqual(data['success'], True)

    def test_search_question(self):
        """test success fo searchin questions"""
        # send post request for searching question
        # new_search = {'searchTerm': 'a'}
        response = self.client().post('/questions/search', json={
            'searchTerm': 'what'})
        data = json.loads(response.data)

        # check status code, success message, that there are questions in the search results ----------------------------
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    # Test Search Failure
    def test_404_search_questions(self):
        """test for no search results 404"""
        response = self.client().post('/questions/search', json={
            'searchTerm': ''})
        data = json.loads(response.data)

        # check status code, false success message  ----------------------------------------------------
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_404_get_category_questions(self):
        """test for 404 error with no questions from category"""
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

        # check status code, false success message when category id not found to get question------------------------------
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_422_if_book_creation_fails(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quiz(self):
        """testing success of playing quiz"""
        quiz_round = {'previous_questions': [], 'quiz_category': {
            'type': 'Geography', 'id': 15}}
        response = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(response.data)

        # chech status code on response succeed-------------------------------------------------------------------
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_get_quiz(self):
        """testing 422 error if quiz game fails"""
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
