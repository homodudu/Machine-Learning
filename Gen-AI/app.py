from flask import Flask, render_template, request
from chatbot import respond_to_question

# Create instance of the app class
app = Flask(__name__)


@app.route("/") # Use the route() decorator to bind function to the "base" url endpoint
def home():
    return render_template("index.html")

@app.route("/get") # Use the route() decorator to bind function to the "get" URL endpoint
def response():
    userText = request.args.get('msg')
    response = respond_to_question(userText)
    #return str(bot.get_response(userText))
    return response

if __name__ == "__main__":
  app.run(debug=True)
