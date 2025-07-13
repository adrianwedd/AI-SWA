"""Minimal CrewAI plugin example."""
from crewai import Agent, Crew


def run_mission(prompt: str) -> str:
    """Run a simple two-agent CrewAI mission."""
    analyst = Agent(name="Analyst")
    writer = Agent(name="Writer")
    crew = Crew([analyst, writer])
    result = crew.chat(prompt)
    return result[-1].content
