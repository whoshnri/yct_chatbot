from flask import Flask
from flask_cors import CORS
import os
from ai_bot import  make_graph_and_compile
import json
from flask import request

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    cookie = request.args.get('cookie')
    response = make_graph_and_compile(json.loads(cookie))
    print("Response:", response['response'])
    return json.dumps(response), 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(debug=True,port=4000)