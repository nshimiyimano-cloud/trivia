

from crypt import methods
import string
from sqlalchemy import cast, String
import json
from operator import or_
import os
from unicodedata import category

from flask import Flask, request, abort, jsonify, request,render_template


from flask_cors import CORS, cross_origin


from models import setup_db, Question, Category, db


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # to allow  Cross Origin Resource Sharing

    # or to use @cross_origin() decorator under @app.route  or resouce={r"/api/*""} and index's route will be @app.route('/apiz')
    CORS(app, resources={r"*": {"origins": "*"}})
    setup_db(app)
    return app


app = create_app()


# logging.getLogger('flask_cors').level = logging.DEBUG   # here if things aren't going as you expected enable logging like this to know what is going under the hood


@app.route('/categories')
@cross_origin()
def getallcategories():
    cat = Category.query.all()
    cat_format = [category.format() for category in cat]
    # if  len(cat) == 0:
    if len(cat_format) == 0:
        return ("Category is empty")
    else:
        return jsonify({
            'message': True,
            'categories': cat_format

        })


@app.route('/questions/page/<int:p>', methods=["GET"])
@cross_origin()
def getallquestions(p):

    question = Question.query.limit(p).all() 
    category = Category.query.all()
    cat_format = [cat.format() for cat in category]

    quest_format = [cat.format() for cat in question]

    if len(quest_format) == 0:
        return ("Question not asked is empty")
    else:
        print(quest_format)
        return jsonify({
            'questions': quest_format,
            'total_questions': len(question),
            'categories': cat_format,
            'current_category': cat_format


        })


@app.route('/categories/<int:id>/questions')
@cross_origin()
def show_question(id):

    question = db.session.query(Question, Category).join(
        Category, Question.category == id).all()

    if question is not None:
        for quest in question:
            category = Category.query.all()
            cat_format = [cat.format() for cat in category]

            return jsonify({
                'questions': {
                    'answer': quest[0].answer,
                    'id': quest[0].id,
                    'question': quest[0].question,
                    'difficult': quest[0].difficulty

                },
                'total_questions': len(question),
                'current_category': quest[0].category,
                'categories': cat_format
            })
    else:
        return {
            'message': f"please data with id {id} is not found",
            'success': False
        }


@app.route('/questions',methods=["GET"])
@cross_origin()
def getallquestion():
    quest = Question.query.all()
    quest_format = [question.format() for question in quest]

    if len(quest_format) == 0:
        return {
            'message': f"fetch data error",
            'success': False
        }
    else:
        return jsonify({
            'message': True,
            'questions': quest_format

        })


@app.route('/questions/<int:id>',methods=["DELETE"])
@cross_origin()
def deletequestion(id):
    quest=Question.query.get_or_404(id)   
    Question.delete(quest)
    return jsonify({
            "message":f"question {quest.id} already deleted",
            "question":quest.question
        })


@app.route('/questions/<int:id>', methods=['GET'])
@cross_origin()
def getquestionbyId(id):
    question=Question.query.get_or_404(id)   
    
    return jsonify({
            "id":question.id,
            "answer":question.answer,
            "difficulty":question.difficulty,
            "question":question.question
            
    })



   



@app.route('/questions', methods=['POST'])
@cross_origin()
def addQuestion():
    data = request.get_json()
    question= data.get('question','')
    answer = data.get('answer','')
    difficulty = str(data.get('difficulty',''))
    category = str(data.get('category',''))
   
    
    new_question=Question(question=question,answer=answer,difficulty=difficulty,category=category)
    insert=Question.insert(new_question)
    return jsonify({
          "message":"new question added Successfully",
          "new question":question

    })




    #  Create a POST endpoint to get questions based on a search term.

@app.route('/questions/search', methods=['POST'])
@cross_origin()

def searchquestion(): 


    search=request.get_json()['searchTerm']
    
    results = Question.query.filter(Question.question.like(f"%{search}%")).all()
    question_format = [quest.format() for quest in results]



    if len(question_format) != 0: 
        print( f" result from search are: {results}" )
        return jsonify({
                'questions': question_format,
                'total_questions': len(results)
                #'categories':results.category,
                 #'current_category': results.category                
            })



    else:
        print("no result")
        return jsonify({
              'message': f"please question with provided search term is not found",
              'success': False
            })
    


    
    
    

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

  

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(422)
def server_error(error):
    return render_template('errors/422.html'), 422

    return app
