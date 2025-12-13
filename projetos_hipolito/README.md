# 🩺 PokémonPB: O Centro de Estratégias com Assistente IA

![Banner temático d Pokédex](https://cdn.dribbble.com/userupload/28294886/file/original-18cc0f398ac8226985372af1c06ff326.gif)
![Tecnologia Principal](https://img.shields.io/badge/Python-3.14%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/Framework-Flask-orange?style=for-the-badge&logo=flask)
![Assistente IA](https://img.shields.io/badge/Google-Gemini_API-3C3C3C?style=for-the-badge&logo=google)

Este projeto é uma **Pokédex interativa** desenvolvida em Python e Flask, que oferece dados de Pokémon (status, ataques, evoluções e lore) e se diferencia por integrar a **Enfermeira Joy**, uma assistente de Inteligência Artificial dedicada a fornecer conselhos estratégicos e builds.

## ✨ Destaques & Funcionalidades

Nosso projeto combina dados estáticos de uma Pokédex com o poder da IA generativa para criar uma experiência completa para Treinadores:

### 🌟 Pokédex Completa
* **Detalhes e Status:** Visualize os status base, tipos e informações essenciais de qualquer Pokémon.
* **Cadeia Evolutiva:** Acompanhe a linha de evolução completa, desde a forma inicial até a Mega Evolução ou Dynamax (se aplicável).
* **Lista de Ataques:** Descubra o moveset completo que cada Pokémon pode aprender 
* **Lore e Descrição:** Acesse descrições oficiais e informações de lore da Pokédex.

### 🤖 Assistente IA: Enfermeira Joy
A Enfermeira Joy está pronta para ajudar com decisões estratégicas, utilizando o poder do modelo Gemini:
* **Sugestão de Builds:** Obtenha as 4 melhores sugestões de ataques para qualquer Pokémon, com foco em estratégias de batalha.
* **Recomendações de Time:** Peça sugestões de times de 6 Pokémon com base em um tipo ou objetivo específico.
* **Respostas Contextualizadas:** Faça perguntas específicas sobre regras e interações do universo Pokémon.

## 🛠️ Tecnologias Envolvidas

| Componente | Tecnologia | Uso no Projeto |
| :--- | :--- | :--- |
| **Backend** | Python, Flask, Jinja2 | Roteamento, lógica de aplicação e renderização de templates. |
| **IA Core** | Google Gemini API (`2.0-flash-lite`) | Motor de chat e inteligência estratégica da Enfermeira Joy. |
| **Segurança** | `python-dotenv` | Carregamento seguro da chave de API (`GEMINI_API_KEY`) via arquivo `.env`. |
| **Deploy** | `gunicorn` | Servidor HTTP robusto, usado para rodar a aplicação em produção (Render). |
| **Dados** | PokéAPI | Fonte de dados principal para todas as informações de Pokémon. |


### 🌐 Internacionalização
- Integração com **Google Translate** para fornecer descrições e histórias (Lore) em Português do Brasil sempre que a API oficial não disponibiliza.

---

## 🚀 Roteiro de Futuro (Roadmap)

Estamos trabalhando duro para trazer a verdadeira batalha para o navegador!

- [ ] **Battle Engine (PvE)**: Enfrente uma Inteligência Artificial em batalhas estratégicas por turnos.
- [ ] **Multiplayer Online**: Desafie amigos em tempo real usando WebSockets (Socket.IO).
- [ ] **Team Builder**: Crie, salve e compartilhe suas equipes Pokémon ideais.
- [ ] **Animações de Batalha**: Efeitos visuais para os ataques durante o combate.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3 (Variáveis CSS, Grid, Flexbox), JavaScript (Vanilla)
- **Dados**: [PokéAPI](https://pokeapi.co/)
- **Tradução**: Deep Translator
- **Comunicação Real-Time**: Flask-SocketIO (Preparado para o futuro)

---

## ✅ Rodar o Projeto Localmente

- **Instalar Python 3.14.* ***: Instale a versão do python 3.14+
- **Crie um ambiente virtual**: Evite que outros pacotes instalados na sua máquina atrapalhem no codigo execute ''python -m venv venv'' ou ''py -m venv venv'' no terminal do projeto. 
- **Ative o Script**: Use venv\Scripts\activate no terminal para ativar, em seguida use pip install -r requirements.txt (Caso você retire ou atualize uma nova biblioteca, utilize o comando pip freeze > requirements.txt) esse comando irá atualizar as dependencias do projeto
- **Rode o projeto**: Divirta-se! 😅 

- **EXTRA**: Caso você queira usar a enfermeira joy, você precisa de uma api do goggle studio e uma conta maior de 18 anos, acesse [Goggle-Studio](https://aistudio.google.com/api-keys) selecione o plano free e crie uma api key, crie um arquivo .env e coloque sua api key GEMINI_API_KEY = (SUA_API_KEY) (Cuidado com os limites dos modelos!)

<p align="center">
  Desenvolvido Por @FrierenSZ_ para fãs de Pokémon.
</p>