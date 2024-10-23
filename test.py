from flask import Flask, Response

app = Flask(__name__)

@app.after_request
def apply_csp(response: Response):
    csp_policy = "default-src 'self'"
    response.headers['Content-Security-Policy'] = csp_policy
    print("CSP applied:", response.headers.get('Content-Security-Policy'))
    return response

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(port=5001)