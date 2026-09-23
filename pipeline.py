from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ============================================================
    # STEP 1 - SEARCH AGENT
    # ============================================================

    print("\n" + "=" * 80)
    print("STEP 1 - SEARCH AGENT IS WORKING ...")
    print("=" * 80)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({

        "messages": [
            (
                "user",
                f"""
Find recent, reliable and detailed information about:

{topic}

Search for multiple high-quality sources.

IMPORTANT:
Preserve the exact title and URL of every useful source.
"""
            )
        ]

    })

    state["search_results"] = (
        search_result["messages"][-1].content
    )

    print("\nSEARCH RESULTS:\n")
    print(state["search_results"])


    # ============================================================
    # STEP 2 - READER AGENT
    # ============================================================

    print("\n" + "=" * 80)
    print("STEP 2 - READER AGENT IS SCRAPING TOP RESOURCES ...")
    print("=" * 80)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({

        "messages": [
            (
                "user",
                f"""
Based on the following search results about:

{topic}

Identify the most relevant sources and scrape them
for deeper information.

IMPORTANT:

- Extract the exact URLs.
- Use the scrape_url tool.
- Preserve the exact URLs.
- Do not invent URLs.
- Return the source URL with the scraped content.

SEARCH RESULTS:

{state["search_results"]}
"""
            )
        ]

    })

    state["scraped_content"] = (
        reader_result["messages"][-1].content
    )

    print("\nSCRAPED CONTENT:\n")
    print(state["scraped_content"])


    # ============================================================
    # STEP 3 - WRITER
    # ============================================================

    print("\n" + "=" * 80)
    print("STEP 3 - WRITER IS DRAFTING THE REPORT ...")
    print("=" * 80)

    research_combined = (

        f"SEARCH RESULTS:\n\n"
        f"{state['search_results']}\n\n"

        f"{'=' * 60}\n\n"

        f"DETAILED SCRAPED CONTENT:\n\n"
        f"{state['scraped_content']}"

    )

    state["report"] = writer_chain.invoke({

        "topic": topic,

        "research": research_combined

    })

    print("\n" + "=" * 80)
    print("FINAL RESEARCH REPORT")
    print("=" * 80)

    print(state["report"])


    # ============================================================
    # STEP 4 - CRITIC
    # ============================================================

    print("\n" + "=" * 80)
    print("STEP 4 - CRITIC IS REVIEWING THE REPORT ...")
    print("=" * 80)

    state["feedback"] = critic_chain.invoke({

        "report": state["report"]

    })

    print("\nCRITIC REPORT:\n")

    print(state["feedback"])


    return state


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    topic = input(
        "\nEnter a research topic: "
    )

    run_research_pipeline(topic)