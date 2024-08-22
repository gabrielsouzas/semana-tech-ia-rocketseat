import json
import os
from datetime import datetime

import yfinance as yf  # type: ignore

from crewai import Agent, Task, Crew, Process  # type: ignore

from langchain.tools import Tool
from langchain_openai import ChatOpenAI  # type: ignore
from langchain_community.tools import DuckDuckGoSearchResults

import streamlit as st  # type: ignore


# CRIANDO YAHOO FINANCE TOOL


# Função que agrupa os preços por ação, com um intervalo de datas
def fetch_stock_price(ticket):
    # Parametros(nome_acao, inicio, fim)
    stock = yf.download(ticket, start="2023-08-08", end="2024-08-08")
    return stock


# Ferramenta para pegar ações a partir da função fetch_stock_price
yahoo_finance_tool = Tool(
    name="Yahoo Finance Tool",
    description="Fetches stocks prices for {ticket} from the last year about a specific company from Yahoo Finance API",
    func=lambda ticket: fetch_stock_price(ticket),
)

# IMPORTANDO OPENAI LLM - GPT
os.environ["OPENAI_API_KEY"] = st.secrets[
    "OPEN_API_KEY"
]  # Pega a KEY da Open AI registrada no Streamlit cloud
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Agente da CrewAI que recebe a ferramenta do Yahoo Finance
stockPriceAnalyst = Agent(
    role="Senior stock price Analyst",
    goal="Find the {ticket} stock price and analyses trends",
    backstory="""You're highly experienced in analyzing the price of an specific stock
    and make predictions about its future price.""",
    verbose=True,
    llm=llm,
    max_iter=5,
    memory=True,
    tools=[yahoo_finance_tool],
    allow_delegation=False,
)


# In[6]:

# Tarefa da CrewAI que vai analisar a ação (eg. é o exemplo passado para o output da tarefa)
getStockPrice = Task(
    description="Analyze the stock {ticket} price history and create a trend analyses of up, down or sideways",
    expected_output="""" Specify the current trend stock price - up, down or sideways. 
    eg. stock= 'APPL, price UP'
""",
    agent=stockPriceAnalyst,
)


# In[7]:


# IMPORTANT A TOOL DE SEARCH
search_tool = DuckDuckGoSearchResults(backend="news", num_results=10)


# In[8]:

# Agente que vai buscar as noticias com o duckduck go
newsAnalyst = Agent(
    role="Stock News Analyst",
    goal="""Create a short summary of the market news related to the stock {ticket} company. Specify the current trend - up, down or sideways with
    the news context. For each request stock asset, specify a numbet between 0 and 100, where 0 is extreme fear and 100 is extreme greed.""",
    backstory="""You're highly experienced in analyzing the market trends and news and have tracked assest for more then 10 years.

    You're also master level analyts in the tradicional markets and have deep understanding of human psychology.

    You understand news, theirs tittles and information, but you look at those with a health dose of skepticism. 
    You consider also the source of the news articles. 
    """,
    verbose=True,
    llm=llm,
    max_iter=10,
    memory=True,
    tools=[search_tool],
    allow_delegation=False,
)


# In[9]:

# Tarefa que vai usar o agente analista de ações, para pegar as noticias e criar um sumário geral do mercado, usando um formato especifico solicitado
get_news = Task(
    description=f"""Take the stock and always include BTC to it (if not request).
    Use the search tool to search each one individually. 

    The current date is {datetime.now()}.

    Compose the results into a helpfull report""",
    expected_output=""""A summary of the overall market and one sentence summary for each request asset. 
    Include a fear/greed score for each asset based on the news. Use format:
    <STOCK ASSET>
    <SUMMARY BASED ON NEWS>
    <TREND PREDICTION>
    <FEAR/GREED SCORE>
""",
    agent=newsAnalyst,
)


# In[10]:

# Agente que vai fazer a analise de fato, ou seja, que vai finalmente escrever a analise baseando se no relatorio de ações e na tendencia dos preços que os agentes anteriores resgataram
stockAnalystWrite = Agent(
    role="Senior Stock Analyts Writer",
    goal=""""Analyze the trends price and news and write an insighfull compelling and informative 3 paragraph long newsletter based on the stock report and price trend. """,
    backstory="""You're widely accepted as the best stock analyst in the market. You understand complex concepts and create compelling stories
    and narratives that resonate with wider audiences. 

    You understand macro factors and combine multiple theories - eg. cycle theory and fundamental analyses. 
    You're able to hold multiple opinions when analyzing anything.
""",
    verbose=True,
    llm=llm,
    max_iter=5,
    memory=True,
    allow_delegation=True,  # Pode delegar tarefas a outros por conta da utilização de outros agentes
)


# In[11]:

# Tarefa que vai usar o Agente de escrita da analise
writeAnalyses = Task(
    description="""Use the stock price trend and the stock news report to create an analyses and write the newsletter about the {ticket} company
    that is brief and highlights the most important points.
    Focus on the stock price trend, news and fear/greed score. What are the near future considerations?
    Include the previous analyses of stock trend and news summary.
""",
    expected_output=""""An eloquent 3 paragraphs newsletter formated as markdown in an easy readable manner. It should contain:

    - 3 bullets executive summary 
    - Introduction - set the overall picture and spike up the interest
    - main part provides the meat of the analysis including the news summary and fead/greed scores
    - summary - key facts and concrete future trend prediction - up, down or sideways.
""",
    agent=stockAnalystWrite,
    context=[
        getStockPrice,
        get_news,
    ],  # Passa o contexto com as tasks que usam outros agentes, como descrito em sua description
)


# In[12]:

# Grupo que vai configurar/organizar os agentes de IA criados até aqui
crew = Crew(
    agents=[stockPriceAnalyst, newsAnalyst, stockAnalystWrite],
    tasks=[getStockPrice, get_news, writeAnalyses],
    verbose=2,
    process=Process.hierarchical,  # Vai organizar as tasks por cadeia de comando, por ter um delegador que deve ser o primeiro a ser chamado
    full_output=True,
    share_crew=False,
    manager_llm=llm,
    max_iter=15,
)

# Chamada da execução da crew
# results= crew.kickoff(inputs={'ticket': 'AAPL})


# Criação da página Web
with st.sidebar:  # Cria um sidebar
    st.header("Enter the Stock to Research")  # Cria um header

    with st.form(key="research_form"):  # Cria um form
        topic = st.text_input("Select the ticket")  # Recebe um input do usuário
        submit_button = st.form_submit_button(
            label="Run Research"
        )  # Botão de enviar o form
if submit_button:
    if not topic:  # Se o botão for pressionado e não passar o topic, apresenta um erro
        st.error("Please fill the ticket field")
    else:  # Caso seja passado o topic executa os Agentes de IA com o topico passado pelo usuario
        results = crew.kickoff(inputs={"ticket": topic})

        st.subheader("Results of research:")
        st.write(results["final_output"])
