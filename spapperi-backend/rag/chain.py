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

extractor_chain = prompt | llm | JsonOutputParser()
