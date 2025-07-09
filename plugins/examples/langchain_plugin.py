"""Minimal LangChain plugin example."""
from langchain.chains import LLMChain
from langchain.llms import OpenAI


def summarize(text: str) -> str:
    """Return a short summary of ``text`` using an LLMChain."""
    llm = OpenAI(model="gpt-3.5-turbo")
    chain = LLMChain.from_string(llm, "Summarize:")
    return chain.run(text)
