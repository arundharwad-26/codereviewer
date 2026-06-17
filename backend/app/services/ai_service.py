import json
import time
import google.generativeai as genai
from loguru import logger
from app.config import settings
from app.exceptions import AIServiceError, AIResponseParseError


# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Model to use
MODEL = "gemini-2.0-flash"


def build_prompt(
    agent_type: str,
    diff: str,
    context: dict = None
) -> str:
    """
    Internal helper — builds prompt string for Gemini API call.
    Never call this outside ai_service.py.
    """
    if agent_type == "code_review":
        prompt = f"""You are an expert code reviewer with 10+ years of experience.
Analyze this pull request diff and provide detailed, actionable feedback.

You must respond with ONLY a valid JSON object in this exact format:
{{
    "overall_score": <integer 0-100>,
    "summary": "<brief overall summary>",
    "issues": [
        {{
            "file": "<filename>",
            "line": <line number or null>,
            "type": "<issue type>",
            "severity": "<low|medium|high|critical>",
            "message": "<clear description of the issue>",
            "suggestion": "<specific fix suggestion>"
        }}
    ]
}}

Scoring guide:
90-100: Excellent code
70-89: Good code with some improvements needed
50-69: Average code with several issues
30-49: Poor code with significant problems
0-29: Critical issues that must be fixed

Do not include any text outside the JSON object.
Do not wrap the JSON in markdown code blocks.

Pull request diff to review:
{diff}"""

    elif agent_type == "security":
        context_section = ""
        if context:
            context_section = f"""
Code Review Agent already found these issues:
{json.dumps(context, indent=2)}

Use this as additional context. Focus on security vulnerabilities not already covered.
"""

        prompt = f"""You are an expert security engineer specializing in code security analysis.
Analyze this pull request diff for security vulnerabilities.

You must respond with ONLY a valid JSON object in this exact format:
{{
    "severity": "<low|medium|high|critical>",
    "summary": "<brief security summary>",
    "vulnerabilities": [
        {{
            "file": "<filename>",
            "line": <line number or null>,
            "type": "<vulnerability type>",
            "description": "<clear description>",
            "recommendation": "<specific fix>"
        }}
    ]
}}

If no vulnerabilities found respond with:
{{
    "severity": "low",
    "summary": "No security vulnerabilities detected.",
    "vulnerabilities": []
}}

Do not include any text outside the JSON object.
Do not wrap the JSON in markdown code blocks.

Pull request diff to analyze:
{diff}
{context_section}"""

    else:
        raise AIServiceError(f"Unknown agent type: {agent_type}")

    return prompt


def parse_agent_response(response_text: str) -> dict:
    """
    Internal helper — parses AI response text into a dict.
    Strips markdown code blocks if present.
    Never call this outside ai_service.py.
    """
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent response: {e}")
        logger.error(f"Raw response: {response_text}")
        raise AIResponseParseError(
            f"Agent returned invalid JSON: {str(e)}"
        )


async def run_code_review_agent(diff: str) -> dict:
    """
    Run the code review agent on a diff.
    Returns structured JSON with issues, overall_score, summary.
    """
    logger.info("Running code review agent")
    start_time = time.time()

    prompt = build_prompt("code_review", diff)

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        response_text = response.text

        result = parse_agent_response(response_text)

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            f"Code review agent completed in {processing_time}ms"
        )

        result["_meta"] = {
            "tokens_used": 0,
            "processing_time_ms": processing_time
        }

        return result

    except AIResponseParseError:
        raise
    except Exception as e:
        raise AIServiceError(
            f"Gemini API error in code review agent: {str(e)}",
            agent_type="code_review"
        )


async def run_security_agent(diff: str, code_review_output: dict) -> dict:
    """
    Run the security agent on a diff.
    Takes code review output as context for sequential passing.
    Returns structured JSON with vulnerabilities, severity, summary.
    """
    logger.info("Running security agent")
    start_time = time.time()

    prompt = build_prompt("security", diff, context=code_review_output)

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        response_text = response.text

        result = parse_agent_response(response_text)

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            f"Security agent completed in {processing_time}ms"
        )

        result["_meta"] = {
            "tokens_used": 0,
            "processing_time_ms": processing_time
        }

        return result

    except AIResponseParseError:
        raise
    except Exception as e:
        raise AIServiceError(
            f"Gemini API error in security agent: {str(e)}",
            agent_type="security"
        )