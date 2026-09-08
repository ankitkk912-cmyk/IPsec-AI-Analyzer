import os

def get_ai_explanation(analysis):
    """
    Optional AI layer.
    The app works without an API key. If OPENAI_API_KEY is set and the
    openai package is installed, it asks the Responses API for a concise
    defensive explanation of the already-computed findings.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "AI API is not configured. The dashboard is still fully usable: "
            "the local rules engine already produced the score, findings and recommendations. "
            "To enable natural-language AI explanations, add OPENAI_API_KEY to .env."
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a defensive network-security assistant. Explain this IPsec "
            "configuration assessment for a student hackathon demo. Do not provide "
            "attack instructions. Give: (1) overall risk, (2) top 3 findings, "
            "(3) practical remediation steps. Keep it under 250 words.\n\n"
            + str(analysis["result"])
        )
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            input=prompt
        )
        return response.output_text
    except Exception as exc:
        return f"AI explanation could not be generated: {exc}"
