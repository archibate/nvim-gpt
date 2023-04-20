from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route("/")
def chat():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat_api():
    payload = request.get_json()
    messages = payload["messages"]

    # Here you can implement your chatbot logic
    # to generate a response to the user's message
    response = "I received your message: " + messages[-1][1]

    return jsonify({"status": "FINISHED", "reply": response})

if __name__ == "__main__":
    app.run()
