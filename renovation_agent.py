#!/usr/bin/env python3
"""
Renovation Ideas Agent for Peltheide 11, 3150 Haacht, Belgium.

Property details sourced from:
https://www.dekrem.be/pand-detail/verkoop-woning-haacht/7523708

Run this script to interactively ask for the best renovation ideas for this property.

Requirements:
    pip install openai

Set OPENAI_API_KEY as an environment variable before running:
    export OPENAI_API_KEY=sk-...
"""

import json
import os
import sys

PROPERTY_FILE = os.path.join(os.path.dirname(__file__), "property_data.json")

SYSTEM_PROMPT = """You are a professional renovation advisor specialising in Belgian residential properties.
You have been given the full details of the property at Peltheide 11, 3150 Haacht, Belgium.
Use this data to give concrete, practical, and prioritised renovation advice.
Always take into account:
- The Flemish renovation obligation (EPC label F, score 708 kWh/m²·year → must reach at least label D within 6 years of purchase).
- Available Flemish government renovation premiums (mijn verbouwpremie, mijn verbouwlening, etc.).
- The property's year of construction (1968), split-level layout, south-facing garden, and current utilities.
- Budget efficiency, return-on-investment, and liveability improvements.
When the user asks a general question, proactively suggest the most impactful renovations first.
Always be concise, actionable, and refer to specific rooms or features from the property data where relevant."""


def load_property_data(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_property_context(data: dict) -> str:
    return (
        "PROPERTY DATA (Peltheide 11, 3150 Haacht):\n"
        + json.dumps(data, indent=2, ensure_ascii=False)
    )


def chat(messages: list, model: str = "gpt-4o") -> str:
    try:
        import openai
    except ImportError:
        sys.exit(
            "The 'openai' package is required. Install it with:  pip install openai"
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit(
            "Please set the OPENAI_API_KEY environment variable before running this agent."
        )

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def main():
    property_data = load_property_data(PROPERTY_FILE)
    property_context = build_property_context(property_data)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Here is the full property data for the house I want to renovate:\n\n{property_context}",
        },
        {
            "role": "assistant",
            "content": (
                "Thank you! I have reviewed all the details for Peltheide 11, 3150 Haacht. "
                "This is a detached split-level home built in 1968, with 3 bedrooms, a south-facing "
                "garden, and a large garage. It currently has an EPC label F (708 kWh/m²·year) and "
                "you are legally required to upgrade it to at least label D within 6 years of purchase. "
                "I'm ready to help — what would you like to know about the best renovation ideas?"
            ),
        },
    ]

    print("=" * 65)
    print("  Renovation Ideas Agent — Peltheide 11, 3150 Haacht")
    print("=" * 65)
    print(
        "Property loaded. Type your renovation questions below.\n"
        "Type 'quit' or press Ctrl+C to exit.\n"
    )
    print("Agent: " + messages[-1]["content"])
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        print("Agent: thinking…", end="\r", flush=True)

        try:
            reply = chat(messages)
        except Exception as exc:
            print(f"Agent: [Error communicating with the AI: {exc}]")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": reply})
        print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()
