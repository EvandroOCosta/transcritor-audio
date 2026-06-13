from flask import Flask, request, jsonify, render_template
import whisper
import tempfile
import os

app = Flask(__name__)

model = None

def get_model():
    global model
    if model is None:
        model = whisper.load_model("base")
    return model

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcrever", methods=["POST"])
def transcrever():
    if "audio" not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado"}), 400

    arquivo = request.files["audio"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo.filename)[1]) as tmp:
        arquivo.save(tmp.name)
        caminho = tmp.name

    try:
        resultado = get_model().transcribe(caminho, language="pt")
        return jsonify({"texto": resultado["text"]})
    finally:
        os.unlink(caminho)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
