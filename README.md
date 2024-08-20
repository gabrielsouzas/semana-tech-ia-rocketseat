# Semana Tech IA - RocketSeat

Repositório para alocar as aulas da imersão da Rocketseat - IA na Prática - OpenAI + Python + CrewAI

## Requisitos

- [Visual Studio Code](https://code.visualstudio.com/) - Editor de código;
- [Python](https://www.python.org/downloads/) - Linguagem de programação;
- [CrewAI](https://www.crewai.com/) - Framework que fornece uma serie de métodos que permite criar um grupo de agentes de IA, também fornece as ferramentas para lidars com as tasks.

## Instalações

Atualize o pip se necessário:

```shell
python.exe -m pip install --upgrade pip
```

Crie um ambiente virtual python:

```shell
python -m venv venv
```

ou

```shell
py -m venv venv
```

Ative o ambiente virtual:

```shell
venv\Scripts\activate
```

Instale as dependências:

```shell
pip install -r requirements.txt
```

## Aula 1

Descrição do projeto: Desenvolver um consultor para o mercado de ações com a OpenAI, Python e CrewAI.

A imagem abaixo ilustra como funciona um Agente de IA, que será utilizado para as consultas. Esse agente vai ser fornecido pela CrewAI.

![Agente de IA](img/print_01.png)

Funcionamento do consultor a partir da solicitação de um usuário:

![Funcionamento Agentes](img/print_02.png)

Separação de cada agente:

1º Agente: Analise do preço histórico de cada ação com o Yahoo Finance, que é uma API capaz de resgatar preços de ações;

2º Agente: Analise de noticias da empresa com DuckDuck Go para pesquisar noticias sobre as empresas e ações;

3º Agente: Vai finalmente fazer a recomendação da ação usando os dados do agentes anteriores.

![Agente Final](img/print_03.png)

### Criação do arquivo `crewai-stocks.py`

Esse arquivo foi criado no modelo Jupiter Notebook, por ter um formato de células, para analisar erros por partes de códigos. Mas ainda assim, no deploy o script deverá ser python.

Resultado esperado em Markdown:

![Resultado esperado](img/print_04.png)
