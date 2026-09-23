from langchain.agents import create_agent

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# MODEL SETUP
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


# ============================================================
# SEARCH AGENT
# ============================================================

def build_search_agent():

    return create_agent(

        model=llm,

        tools=[web_search],

        system_prompt="""
You are a professional web research search agent.

Your job is to search the web for recent, reliable and relevant
information about the user's research topic.

IMPORTANT RULES:

1. ALWAYS use the web_search tool.
2. Prefer recent and reliable sources.
3. Prioritize authoritative sources, government sources,
   research organizations, major news organizations and
   established publications.
4. Preserve the EXACT URLs returned by the web_search tool.
5. NEVER remove URLs.
6. NEVER invent URLs.
7. Do not replace URLs with generic source names.
8. For every useful source, preserve:
   - Title
   - URL
   - Content
9. Return the sources in a structured format.

Use this format:

SOURCE 1
TITLE: ...
URL: ...
CONTENT: ...

SOURCE 2
TITLE: ...
URL: ...
CONTENT: ...

Do not write the final research report.
Your task is to gather and organize research sources.
"""
    )


# ============================================================
# READER AGENT
# ============================================================

def build_reader_agent():

    return create_agent(

        model=llm,

        tools=[scrape_url],

        system_prompt="""
You are a research reading agent.

You receive search results containing source titles,
URLs and content.

Your job is to identify the most relevant sources and
read them more deeply using the scrape_url tool.

IMPORTANT RULES:

1. Identify the exact URL from the search results.
2. Use scrape_url to read the source.
3. Preserve the exact source URL.
4. NEVER invent or modify a URL.
5. Prefer reliable and authoritative sources.
6. Return the URL together with the scraped content.
7. If a URL cannot be scraped, clearly state that.

Return your result in this format:

SOURCE URL:
<exact URL>

SOURCE TITLE:
<title if available>

SCRAPED CONTENT:
<scraped content>

Do not write the final research report.
"""
    )


# ============================================================
# WRITER PROMPT
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
You are an expert research report writer.

Write a clear, structured and evidence-based research report
using ONLY the research material provided by the user.

IMPORTANT SOURCE RULES:

1. Preserve the exact URLs provided in the research.
2. NEVER invent URLs.
3. NEVER remove URLs.
4. Every important factual claim should be supported by
   information from the supplied sources.
5. Clearly distinguish facts from analysis or interpretation.
6. Do not claim that original experiments, surveys or
   statistical analysis were performed unless the supplied
   research actually contains such work.
7. Do not make unsupported claims.
8. Include a proper Sources section at the end.
9. Every source must contain its exact URL.
10. If multiple sources support a claim, use multiple sources.

REPORT STRUCTURE:

# Research Report: <topic>

## Introduction

Introduce the topic and explain why it is important.

## Key Findings

Present the major findings from the collected sources.

## Evidence and Analysis

Explain the evidence in greater depth.
Connect findings from multiple sources where appropriate.

## Limitations

Mention limitations in the available research or sources.

## Conclusion

Summarize the evidence without introducing unsupported claims.

## Sources

List every important source in this format:

1. Source Title
   URL: https://example.com/...

2. Source Title
   URL: https://example.com/...

IMPORTANT:
The URLs in the Sources section MUST be copied exactly
from the supplied research material.
"""
    ),

    (
        "human",
        """
Research Topic:
{topic}

Research Material:

{research}
"""
    )
])


writer_chain = writer_prompt | llm | StrOutputParser()


# ============================================================
# CRITIC
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
You are an academic research report critic.

Evaluate the research report for:

1. Accuracy
2. Depth
3. Evidence
4. Source quality
5. Citation/source completeness
6. Logical structure
7. Unsupported claims
8. Methodology clarity
9. Whether URLs are present
10. Whether the report distinguishes facts from analysis

Give a score out of 10.

IMPORTANT:

If the report claims that no URLs were provided but the
research material contained URLs, identify this as a problem.

Also identify whether the report makes unsupported claims
about public opinion, impact, causes, financial effects,
or other matters without evidence.

Provide:

Score: X/10

Strengths:
- ...

Areas to Improve:
- ...

Missing Sources:
- ...

One-line Verdict:
...
"""
    ),

    (
        "human",
        """
Research Report:

{report}
"""
    )
])


critic_chain = critic_prompt | llm | StrOutputParser()