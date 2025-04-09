from flask import Flask, request
from flask_restful import reqparse, Resource, Api
from openai import OpenAI
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("user_message", type=str, help="Message user wishes to send to chatbot")



class ChatBot(Resource):
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.auth_token = os.getenv("AUTH_TOKEN")
        with open(os.environ.get("CONTEXT_FILE"), "r", encoding="utf-8") as file:
            self.file_content = file.read()
    def post(self):
        auth_header = request.headers.get("Authorization", "")
        if auth_header != f"Bearer {self.auth_token}":
            return {"Error 401": "Unauthorized"}

        args = parser.parse_args()
        try:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                    "role": "system",
                    "content": f"You are a helpful assistant for a small business, you will use the following information to answer questions related to the business: {self.file_content}"     
                    },
                    {
                    "role": "user",
                    "content": args["user_message"]
                }
            ]
        )
            return response.choices[0].message.content
        except Exception as e:
            return {"Error 500":str(e)}

api.add_resource(ChatBot,"/chat")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
