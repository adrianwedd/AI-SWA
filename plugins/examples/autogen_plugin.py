"""Minimal AutoGen plugin example."""
from autogen import AssistantAgent, UserProxyAgent, GroupChat


def chat(prompt: str) -> str:
    """Start a conversation between two agents and return the last reply."""
    assistant = AssistantAgent(name="assistant")
    user = UserProxyAgent(name="user")
    chat = GroupChat(members=[assistant, user])
    messages = chat.run(prompt)
    return messages[-1].content
