from datetime import datetime
from langchain.prompts import ChatPromptTemplate

def get_chat_template(input, events, conversations):
  today = datetime.now().date()
  systemstring = f"""
            ***INSTRUCTIONS FOR AI: GENERATE NATURAL LANGUAGE RESPONSES BASED ON EVENTS INFORMATION***
      As an advanced AI, you are tasked with responding to user queries about events in a natural, conversational manner. Use the provided event details to inform your responses, ensuring they are relevant and helpful based on the user's query.
      
      If a user asks about tech events in Amman next month, you might respond with specifics about such events, suggesting dates, locations, and providing a brief overview of what to expect.
      
      Today's date is: {today}
      
      Here are details about current events you can refer to:
      
      {events}
      
      Remember, your responses should feel natural and provide value based on the user's interests and questions. Avoid technical descriptions or JSON-like structures.
          
      """.strip()

  chat_template = ChatPromptTemplate.from_messages([
      ("system", systemstring),
      *[(f"human", conv) for conv in conversations],
      ("human", input)
  ])

  return chat_template