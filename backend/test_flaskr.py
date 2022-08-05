import os
import unittest

from flask import json

from flask_sqlalchemy import SQLAlchemy

from backend.flaskr.app import create_app
from backend.flaskr.models import setup_db, Question, Category





class TriviaTestCase(unittest.TestCase):
    
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 1, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
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


    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/delete/55500")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    
    def test_get_paginated_questions(self):
        res = self.client().get("/question")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))


    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=2300")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")



    def test_delete_question(self):
        res = self.client().delete("/questions/delete/1")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["total_questionss"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)



    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["create"], 1)


    def test_Search_for_question(self):
        res = self.client().post('/question/search',json={"searchTerm": "What"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['search_count'], 2)

    # Test Search Failure
    def test_404_No_Search_result(self):
        res = self.client().post('/questions/search',{'searchTerm':''})
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")



    def test_422_if_book_creation_fails(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()