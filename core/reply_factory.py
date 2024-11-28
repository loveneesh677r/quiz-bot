from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id, session)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if not current_question_id:
        return False, "No active question to answer."

    if not answer.strip():
        return False, "Answer cannot be empty."

    user_answers = session.get("user_answers", {})
    user_answers[current_question_id] = answer.strip()
    session["user_answers"] = user_answers
    return True, ""


def get_next_question(current_question_id, session):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # Find the index of the current question
    question_ids = [q['id'] for q in PYTHON_QUESTION_LIST]
    if current_question_id not in question_ids:
        return PYTHON_QUESTION_LIST[0]['question'], PYTHON_QUESTION_LIST[0]['id']  # First question

    current_index = question_ids.index(current_question_id)
    
    # Get the next question if available
    if current_index + 1 < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[current_index + 1]
        return next_question['question'], next_question['id']
    
    # If no more questions, return None
    return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("user_answers", {})
    score = 0

    # Calculate the score
    for question in PYTHON_QUESTION_LIST:
        question_id = question['id']
        correct_answer = question.get('answer')  # Assuming the questions have an 'answer' key
        user_answer = user_answers.get(question_id)

        if user_answer and user_answer.lower() == correct_answer.lower():
            score += 1

    # Generate final response
    total_questions = len(PYTHON_QUESTION_LIST)
    return f"Quiz completed! Your score: {score}/{total_questions}. Thanks for participating!"
