from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

pipeline = joblib.load('pipeline_desempenho.joblib')

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar o estado da API.
    Requisito obrigatório da Sprint.
    """
    return jsonify({
        "status": "online",
        "mensagem": "A API de Predição de Desempenho Escolar está a funcionar corretamente!"
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint que recebe os dados do estudante em JSON, realiza a predição da nota
    e retorna uma recomendação com base na regra de negócio (B2B2C).
    """
    try:
        dados = request.get_json()
        
        df_estudante = pd.DataFrame([dados])
        
        predicao = pipeline.predict(df_estudante)
        nota_prevista = round(float(predicao[0]), 2)
        
        recomenda_educativo = False
        gaming_hours = float(dados.get('gaming_hours', 0))
        
        if nota_prevista < 60.0 and gaming_hours > 5.0:
            recomenda_educativo = True
            
        mensagem_conselho = (
            "🚨 ALERTA BRIDGECARE: Sugere-se mitigar o tempo de ecrã recreativo "
            "e direcionar o aluno para a plataforma de Jogos Educativos."
            if recomenda_educativo else 
            "✅ Desempenho dentro da normalidade. Manter a rotina atual de estudos."
        )
        
        return jsonify({
            "nota_prevista": nota_prevista,
            "intervencao_necessaria": recomenda_educativo,
            "conselho": mensagem_conselho
        }), 200

    except Exception as e:
        return jsonify({
            "erro": "Erro ao processar a requisição",
            "detalhes": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)