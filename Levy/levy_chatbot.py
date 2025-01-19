from openai import OpenAI
from pinecone import Pinecone

# Here we're using dotenv (pip install python-dotenv) to manage environment vars
from dotenv import load_dotenv
from _retrieve_chunks import retrieve_chunks
import os
import re

load_dotenv()

oa = OpenAI()  # alternatively self.client = OpenAI(api_key=<<your OPENAI_API_KEY>>)
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# In this function we will create the system message and include the relevant context
def inject_context_data(context):
    # Edit this system message
    system_message = f"""
        You are a chat bot named 'Levy' and you will answer any VAT related queries based on the resource provided as context.

        Your personality is friendly and professional.

        You will introduce yourself before answering each question.

        You will conclude the conversation in a polite manner, directing the conversation to https://www.gov.uk/guidance/partial-exemption-vat-notice-706

        Here is the relevant resource:

    {context}
    """
    # print("+++++++++++++++++++++++++++++++++++++++++++++++")
    # print("Your system message is: ")
    # print("------------------------------------------------")
    # print(system_message)
    # print("+++++++++++++++++++++++++++++++++++++++++++++++")

    return system_message


def respond_to_question(question):
    context_data = retrieve_chunks(question)
    system_message = inject_context_data(context_data)

    # Call the OpenAI API with your systems message and question
    response = oa.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ]
    )

    # Parse the response to an answer and return it
    return response.choices[0].message.content

def bold_str(s):
    return f"\033[1m{s}\033[0m"



# Call the chatbot to respond to a question and get the answer based on the static injected context
# Example question: If the earth is flat, why do you only see the top half of a ship

question = 'What is the partial exemption method?'
answer = respond_to_question(question)

tax_query = f"""
{bold_str("Question")}:

{question}

{bold_str("Answer")}:

{answer}
"""

print(tax_query)
