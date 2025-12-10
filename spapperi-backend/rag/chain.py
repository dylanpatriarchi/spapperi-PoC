from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)

# Extraction Prompt
system_prompt = """
You are an expert extraction assistent for an agricultural machinery configurator.
Your goal is to extract the specific value requested by the system from the user's input.

Field to extract: {field_name}
Current Configuration Context: {config}

Rules:
1. Return ONLY a JSON object with a single key "value". or "value": null if not found.
2. If the user input is ambiguous, return null.
3. Normalize the data (e.g., "50 centimetri" -> 50).
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}")
])

# Generation Prompt (Natural Phrasing)
generation_system_prompt = """
You are the Spapperi AI Configurator Agent.
Your goal is to ask the user the NEXT QUESTION in the configuration flow naturally and politely.

Context:
- User just said: "{last_user_message}"
- Data collected so far: {config}
- Technical Question you MUST ask: "{technical_question}"

Instructions:
1. Acknowledge the user's input briefy (e.g., "Great choice", "Understood").
2. Ask the Technical Question clearly.
3. Keep it professional but friendly. Italian Language.
4. Do NOT make up new requirements. Stick to the Technical Question.
"""

generation_prompt = ChatPromptTemplate.from_messages([
    ("system", generation_system_prompt),
    ("user", "Proceed.")
])

generation_chain = generation_prompt | llm | StrOutputParser()
