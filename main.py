import os
import openai
from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo

# Load sensitive information from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)

def generate_story(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a creative storyteller."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    myChats = [chat for chat in chats]
    return render_template("index.html", myChats=myChats)

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        data = request.json
        question = data.get("question")
        if not question:
            return jsonify({"error": "No question provided"}), 400

        chat = mongo.db.chats.find_one({"question": question})
        if chat:
            return jsonify({"question": question, "answer": chat["answer"]})
        
        story_prompt = f"Write a story based on this: {question}"
        answer = generate_story(story_prompt)
        
        mongo.db.chats.insert_one({"question": question, "answer": answer})
        return jsonify({"question": question, "answer": answer})
    
    return jsonify({"result": "Welcome! Ask me anything."})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
