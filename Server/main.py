from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/Live")
def Home():
    return jsonify({"Server Status": "HTTP 1.1", "Status Code": 200})

# Opcional: para rodar com 'python main.py' em modo de teste
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)