import os
from autogen import ConversableAgent, GroupChat, GroupChatManager
from tavily import TavilyClient

def build_team(task: str) -> str:
    """Run the high-five multi-agent team on a given task."""
    gemini_config = {
        "config_list": [
            {
                "model": "gemini-2.0-flash",
                "api_key": os.environ["GEMINI_API_KEY"],
                "api_type": "google",
            }
        ]
    }

    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    def web_search(query: str) -> str:
        results = tavily.search(query=query, max_results=5)
        return "\n\n".join(
            f"**{r['title']}**\n{r['content']}" for r in results.get("results", [])
        )

    researcher = ConversableAgent(
        name="Researcher",
        system_message=(
            "You are a research specialist. Use web_search to find relevant, "
            "up-to-date information needed to complete the task. "
            "Always cite your sources."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
    )

    analyst = ConversableAgent(
        name="Analyst",
        system_message=(
            "You are an analytical thinker. Take information gathered by the Researcher "
            "and synthesize it into clear insights and structured findings."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
    )

    writer = ConversableAgent(
        name="Writer",
        system_message=(
            "You are a concise technical writer. Take the Analyst's findings and produce "
            "a clear, well-structured final output for the user."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
    )

    coordinator = ConversableAgent(
        name="Coordinator",
        system_message=(
            "You coordinate the team. Delegate to Researcher first, then Analyst, "
            "then Writer. Say TERMINATE when the final answer is ready."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content") or ""),
    )

    for agent in [researcher, analyst, writer, coordinator]:
        agent.register_function(
            function_map={"web_search": web_search},
        )

    group_chat = GroupChat(
        agents=[coordinator, researcher, analyst, writer],
        messages=[],
        max_round=12,
        speaker_selection_method="auto",
    )

    manager = GroupChatManager(groupchat=group_chat, llm_config=gemini_config)

    coordinator.initiate_chat(manager, message=task)

    last_message = group_chat.messages[-1]["content"] if group_chat.messages else ""
    return last_message
