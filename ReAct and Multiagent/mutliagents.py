from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool
import os

from dotenv import load_dotenv

load_dotenv()

llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

serper_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))
website_tool = WebsiteSearchTool()

orchestrator = Agent(
    role="Orchestrator",
    goal="Coordinate the research, outlining, writing, fact-checking, and editing to deliver a polished technical article. You have to delegate work to every subagent given to you to complete the task.",
    backstory="You are an experienced editor-in-chief who delegates effectively, ensures quality, and keeps the team on schedule.",
    allow_delegation=True,
    verbose=True,
    llm=llm,
)

researcher = Agent(
    role="Researcher",
    goal="Find recent, credible sources and summarize actionable insights for the topic.",
    backstory="You are a meticulous technical researcher who prioritizes reputable sources, recency, and clarity of notes.",
    tools=[serper_tool, website_tool],
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

outliner = Agent(
    role="Outliner",
    goal="Transform research notes into a coherent, detailed outline with logical structure and clear section objectives.",
    backstory="You structure complex information into digestible, well-ordered sections tailored for technical audiences.",
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

writer = Agent(
    role="Writer",
    goal="Draft a comprehensive, accurate, and engaging article based on the outline while maintaining technical clarity.",
    backstory="You are a senior technical writer with strong exposition skills and code-first explanations where relevant.",
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

fact_checker = Agent(
    role="Fact-Checker",
    goal="Verify claims, cite reputable sources, and correct inaccuracies to ensure credibility and consistency.",
    backstory="You are an exacting reviewer who validates every claim against reliable, up-to-date sources.",
    tools=[serper_tool, website_tool],
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

editor = Agent(
    role="Editor",
    goal="Polish the article for grammar, clarity, flow, tone, and structure while preserving technical accuracy.",
    backstory="You are a seasoned editor who elevates readability and engagement without sacrificing precision.",
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

def execute(user_input: str):
    user_task = Task(
        description="Write a technical article about a topic that will be provided to you by the user. The article should be in Markdown format with headings, code blocks where relevant, and a conclusion. Topic: \n\n" + user_input,
        expected_output="A complete article in Markdown with headings, code blocks where relevant, and a conclusion.",
        agent=orchestrator,
    )


    final_crew = Crew(
        agents=[orchestrator, researcher, outliner, writer, fact_checker, editor],
        tasks=[user_task],
        process=Process.sequential,
        verbose=True,
    )

    kickoff_result = final_crew.kickoff()
    return kickoff_result.raw