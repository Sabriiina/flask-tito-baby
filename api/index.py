from flask import Flask, render_template, request, jsonify, redirect
import requests
from flasgger import Swagger, swag_from
import os
import json

app = Flask(__name__)

# Inicializa o Swagger
swagger = Swagger(app)

@app.route('/')
def home():
    return render_template("baby.html")

@app.route("/gerarlink", methods=["POST"])
@swag_from({
    "tags": ["Pagamento"],
    "summary": "Gera link de pagamento Asaas",
    "description": "Recebe os dados do formulário e retorna o link de pagamento gerado pelo Asaas.",
    "consumes": ["application/x-www-form-urlencoded"],
    "parameters": [
        {
            "name": "nome",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Nome do produto"
        },
        {
            "name": "quantidade",
            "in": "formData",
            "type": "integer",
            "required": True,
            "description": "Quantidade do produto"
        },
        {
            "name": "valor",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Valor unitário"
        },
        {
            "name": "subtotal",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Subtotal da compra"
        },
        {
            "name": "produtos_json",
            "in": "formData",
            "type": "string",
            "required": False,
            "description": "Lista de produtos em JSON"
        },
        {
            "name": "parcelas",
            "in": "formData",
            "type": "integer",
            "required": True,
            "description": "Quantidade de parcelas"
        }
    ],
    "responses": {
        302: {
            "description": "Redirecionado para o link de pagamento"
        },
        400: {
            "description": "Erro retornado pelo Asaas"
        }
    }
})
def gerarlink():
    nome = request.form.get("nome")
    quantidade = request.form.get("quantidade")
    valor = request.form.get("valor")
    subtotal = request.form.get("subtotal")
    produtos_json = request.form.get("produtos_json")
    parcelas = request.form.get("parcelas")

    # URL do Asaas
    url = "https://api-sandbox.asaas.com/v3/paymentLinks"

    payload = {
        "billingType": "CREDIT_CARD",
        "chargeType": "INSTALLMENT",
        "name": nome,
        "value": subtotal,
        "isAddressRequired": False,
        "maxInstallmentCount": parcelas,
        "description": f"Compra de {quantidade}x {nome}",
        "callback": {
            "successUrl": "https://flask-tito-baby.vercel.app//compracerta"
        }
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": os.environ.get("ASAAS_TOKEN")
    }

    # Faz a requisição
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    # Se der erro
    if "errors" in data:
        erro = data["errors"][0]["description"]
        return render_template("compraerrada.html", erro=erro)
        #return render_template("compraerrada.html")
        #return redirect("/compraerrada")


    # Pega o link de pagamento
    link_pagamento = data.get("url")

    # 🔥 REDIRECIONA PARA O LINK NA MESMA ABA
    return redirect(link_pagamento)

@swag_from({
    "tags": ["Sucesso"],
    "summary": "Redireciona para a tela inicial em casa de Pagamento",
    "description": "Redireciona para a tela inicial em casa de Pagamento.",
    "consumes": ["application/x-www-form-urlencoded"],
    "responses": {
        200: {
            "description": "Redirecionado para o link de pagamento"
        },
        400: {
            "description": "Erro retornado pelo Asaas"
        }
    }
})
@app.route("/compracerta")
def compra_certa():
    """Tela de compra realizada com sucesso."""
    return render_template("compracerta.html")

@swag_from({
    "tags": ["Erro"],
    "summary": "Mostra tela de erro ao gerar o link de pagamento",
    "description": "Mostra o erro retornado pelo Asaas.",
    "consumes": ["application/x-www-form-urlencoded"],
    "responses": {
        200: {
            "description": "Redirecionado para o link de pagamento"
        },
        400: {
            "description": "Erro retornado pelo Asaas"
        }
    }
})
@app.route("/compraerrada")
def compra_errada():
    """Tela de erro ao gerar o link de pagamento."""
    return render_template("compraerrada.html")

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)


# para poder rodar local
