
# ♻️ GreenCycle - O Ciclo Verde Começa Aqui!

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Django](https://img.shields.io/badge/backend-Django-brightgreen)
![React](https://img.shields.io/badge/frontend-React-blue)
![PostgreSQL](https://img.shields.io/badge/banco-PostgreSQL-9cf)

O **GreenCycle** é uma plataforma que conecta cidadãos a pontos de coleta e parceiros recicladores, promovendo o descarte correto de resíduos e incentivando a sustentabilidade urbana. O projeto foi desenvolvido como parte de um trabalho acadêmico, integrando **backend em Django**, **frontend em React Native** e **banco de dados PostgreSQL**.

---

## 🚀 Funcionalidades

- ✅ Cadastro de usuários (cliente ou parceiro)
- ♻️ Solicitação de coleta de resíduos
- 🏙️ Cadastro de pontos de coleta e materiais aceitos
- ⭐ Avaliações mútuas entre clientes e parceiros
- 📍 Geolocalização via OpenStreetMap + consulta de CEP
- 🔐 Autenticação via JWT
- 🧾 Upload de imagens de coleta
- ⚙️ Painel administrativo Django (ativável)

---

## 🧪 Tecnologias Utilizadas

### 🔧 Backend

Desenvolvido por mim, [@lucasdeinani](https://github.com/lucasdeinani).

- Python 3.13
- Django 5.1
- Django REST Framework
- PostgreSQL
- JWT Authentication
- API ViaCEP e OpenStreetMap (Nominatim)

### 💻 Frontend

Repositório separado em desenvolvimento por [@DBalbinot](https://github.com/DBalbinot) / [@DjStrips](https://github.com/DjStrips)

- React Native (Expo)
- Axios
- React Navigation
- Expo Router

👉 **Repositório do Frontend**: [GreenCycleFrontEnd](https://github.com/lucasdeinani/GreenCycleFrontEnd)

---

## 📦 Como Executar o Projeto

### Backend

```bash
# Clone o repositório
git clone https://github.com/flaviofogaca/GreenCycle.git
cd GreenCycle/backend

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure variáveis no arquivo .env
ALLOWED_HOSTS=127.0.0.1,localhost
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://usuario:senha@host:porta/nome_do_banco

# Rode o servidor
python manage.py runserver
```

---

## 📂 Organização do Projeto

```
backend/
├── core/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── mixins.py
│   └── ...
├── manage.py
├── requirements.txt
└── .env
```

---

## 🤝 Contribuição

Sinta-se à vontade para abrir issues, pull requests ou dar sugestões! Toda ajuda é bem-vinda 🌱

---

## ⭐ Licença

Este projeto é livre para fins acadêmicos. Pode ser utilizado como inspiração para soluções sustentáveis e projetos educacionais.

> "A mudança começa com pequenas atitudes. O GreenCycle é o primeiro passo!" 💚
