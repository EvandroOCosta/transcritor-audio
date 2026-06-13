from flask import Flask, request, jsonify, render_template
import whisper
import tempfile
import os
import math

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
    extensao = os.path.splitext(arquivo.filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp:
        arquivo.save(tmp.name)
        caminho = tmp.name

    try:
        import subprocess

        resultado_duracao = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", caminho],
            capture_output=True, text=True
        )
        duracao = float(resultado_duracao.stdout.strip())

        parte_segundos = 600
        num_partes = math.ceil(duracao / parte_segundos)

        transcricao_completa = ""
        modelo = get_model()

        for i in range(num_partes):
            inicio = i * parte_segundos
            arquivo_parte = caminho + f"_parte{i}.wav"

            subprocess.run([
                "ffmpeg", "-y", "-i", caminho,
                "-ss", str(inicio),
                "-t", str(parte_segundos),
                "-ar", "16000", "-ac", "1",
                arquivo_parte
            ], capture_output=True)

            resultado = modelo.transcribe(arquivo_parte, language="pt")
            transcricao_completa += resultado["text"] + " "

            os.unlink(arquivo_parte)

        return jsonify({
            "texto": transcricao_completa.strip(),
            "partes": num_partes
        })

    finally:
        os.unlink(caminho)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
