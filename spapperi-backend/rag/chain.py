from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)

# Prompt for the State Machine
system_prompt = """
You are the Spapperi AI Configurator Agent.
Your goal is to guide the user through the configuration process defined in the technical flow.

Current Phase: {phase}
Collected Data: {config}

Follow these rules:
1. Only ask ONE question at a time.
2. Validate the user's input against the requirements of the current step.
3. If they ask a technical question, answer it using your knowledge base, then gently return to the flow.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}")
])

chain = prompt | llm | StrOutputParser()
