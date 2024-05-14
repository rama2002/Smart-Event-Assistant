from langchain_openai import AzureChatOpenAI
from app.utils.prompt_template import get_chat_template
from app.database.event_db import fetch_all_event_data
from app.utils.chatbot_sessions import ChatbotSessions
from app.config import API_VERSION, AZURE_DEPLOYMENT
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(api_version=API_VERSION, azure_deployment=AZURE_DEPLOYMENT)

def format_event_data(events):
    event_strings = []
    for event in events:
        interests_str = ", ".join(interest for interest in event['interests'] if interest) if event['interests'] else "No specific interests listed"
        
        questions_str = ""
        if event['questions']:
            for question in event['questions']:
                asked_on_str = question['asked_on'] if question['asked_on'] else "Date not available"
                question_text = f"Q: {question['question_text']} (Asked on: {asked_on_str})"
                answers_text = "\n".join(
                    f"A: {answer['answer_text']} (Answered on: {answer['answered_on'] if answer['answered_on'] else 'Date not available'})"
                    for answer in question['answers']
                ) if question.get('answers') else "No answers yet."
                questions_str += f"{question_text}\n{answers_text}\n"
        else:
            questions_str = "No questions have been asked for this event."

        event_str = (
            f"Title: {event['title']}, "
            f"Description: {event['description']}, "
            f"Start Date: {event['start_date']}, "
            f"End Date: {event['end_date']}, "
            f"Location: {event['location']}, "
            f"Interests: {interests_str}, "
            f"Questions and Answers: \n{questions_str}"
        )
        event_strings.append(event_str)
    return "\n\n".join(event_strings)



def send(session_id, input):
    sessions = ChatbotSessions()
    session = sessions.get_session(session_id)
    events = fetch_all_event_data()
    event_info_string = format_event_data(events)
    chat_template = get_chat_template(input, event_info_string, session["conversations"])
    messages = chat_template.format_messages()
    result = llm.invoke(messages)
    sessions.update_session(session_id, input, result.content)
    print("Processed response:", result.content)
    return result.content
