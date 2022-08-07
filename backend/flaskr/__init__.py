
from sqlalchemy import cast, desc

import os

from flask import Flask, request, abort, jsonify, request, render_template


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


@app.route('/categories')
@cross_origin()
def getallcategories():
    try:
        category = Category.query.all()
        cat_formatted = [cat.format() for cat in category]

        if len(cat_formatted) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'categories': cat_formatted
            })
    except:
        abort(422)


@app.route('/questions/page/<int:p>', methods=["GET"])
@cross_origin()
def getallquestions(p):

    try:
        page = request.args.get('page', p, type=int)
        start = (page - 1) * 10
        end = start + 10
        #question = Question.query.offset(p).limit(10).all()
        # for test deletion on last inserted row
        questions = Question.query.order_by(desc(Question.id)).all()
        category = Category.query.all()
        cat_format = [cat.format() for cat in category]

        quest_formatted = [question.format() for question in questions]

        if questions is None:
            return abort(404)

        else:
            return jsonify({
                'success': True,
                'questions': quest_formatted[start:end],
                'total_questions': len(quest_formatted),
                'categories': cat_format,
                'current_category': cat_format
            })
    except:
        return abort(422)


@app.route('/categories/<int:id>/questions')
@cross_origin()
def show_question(id):
    try:
        question = db.session.query(Question, Category).join(
            Category, Question.category == id).all()

        #  ------------------------------------------------------------------------'total_questions': len(question) instead-----------
        count = db.session.query(Question, Category).join(
            Category, Question.category == id).count()

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
                    'total_questions': count,
                    # ---to get whole category obj end pass in parameter id-1 to get true index-------
                    'current_category': category[id-1].type,
                    'categories': cat_format
                })
        else:
            return abort(404)

    except:
        abort(422)


@app.route('/questions', methods=["GET"])
@cross_origin()
def getallquestion():

    try:
        questions = Question.query.all()
        category = Category.query.all()
        cat_format = [cat.format() for cat in category]

        quest_formatted = [question.format() for question in questions]

        if questions is None:
            return abort(404)

        else:
            return jsonify({
                'success': True,
                'questions': quest_formatted,
                'total_questions': len(questions),
                'categories': cat_format,
                'current_category': cat_format
            })
    except:
        return abort(422)


@app.route('/questions/delete/<int:id>', methods=["DELETE"])
@cross_origin()
def deletequestion(id):
    try:
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        quest = Question.query.get_or_404(id)

        if quest is None:
            abort(404)

        else:
            Question.delete(quest)
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(formatted_questions),
                'deleted': quest.id
            })

    except:
        abort(422)


@app.route('/category/<int:id>', methods=["GET"])
@cross_origin()
def getCategory(id):
    try:
        category = Category.query.get_or_404(id)
        if category is not None:
            return jsonify({
                'category': category.type,
                'id': category.id
            })

        else:
            return abort(404)
    except:
        return abort(422)


@app.route('/questions/<int:id>', methods=['GET'])
@cross_origin()
def getquestionbyId(id):
    try:
        question = Question.query.get_or_404(id)

        if question is not None:
            return jsonify({
                "id": question.id,
                "answer": question.answer,
                "difficulty": question.difficulty,
                "question": question.question
            })

        else:
            return abort(404)
    except:
        return abort(422)


@app.route('/questions', methods=['POST'])
@cross_origin()
def addQuestion():
    try:
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        difficulty = str(data.get('difficulty', ''))
        category = str(data.get('category', ''))
        addQuestion = Question(
            question=question, answer=answer, difficulty=difficulty, category=category)
        Question.insert(addQuestion)

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'created': addQuestion.id
        })

    except:
        return abort(422)


# --------------------  Create a POST endpoint to get questions based on a search term.----------------------------

@app.route('/questions/search', methods=['POST'])
@cross_origin()
def searchquestion():
    try:
        search = request.get_json()['searchTerm']
        results = Question.query.filter(
            Question.question.like(f"%{search}%")).all()
        question_formatted = [quest.format() for quest in results]

        if len(question_formatted) != 0:
            return jsonify({
                'questions': question_formatted,
                'total_questions': len(results),
                'categories': results[0].category,
                'current_category': results[0].category,
                'search_count': len(question_formatted)
            })

        else:
            return jsonify({
                'message': "Resource not found",
                'success': False,
                "status": abort(404)
            })
    except:
        return abort(422)


@app.route('/quizzes', methods=["POST"])
@cross_origin()
def postquiz():

    try:
        current_category = request.get_json()['quiz_category']['type']['id']
        previous_questions = request.get_json()['previous_questions']

        question = Question.query.filter(
            Question.category == current_category and Question.id.not_in(previous_questions)).first()
        formatted_question = question.format()

        if formatted_question is None:
            return abort(404)

        else:
            return jsonify({
                'previous_questions': previous_questions,
                'question': formatted_question

            })
    except:
        abort(422)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


# error will triggered during postman testing in case of the request issues


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request -- the request the client made is incorrect or corrupt, and the server cannot understand it'
    }), 400


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Un processable -- the server understands the content type of the request entity, and the syntax of the request entity is correct, but it was unable to process the contained instructions'
    }), 422


@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed -- that the request method is known by the server but is not supported by the target resource'
    }), 405

    return app
