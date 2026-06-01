"""Copilot — a conversational agent that plans and acts over the other AI
features (Foresight, Coalition, Simulator) plus graph search/recommendations.

The LLM uses OpenAI function-calling to choose tools; this module executes them
and feeds results back until the model produces a final answer, returning both
the answer and the chain of reasoning steps (tool calls + summaries) for the UI.

Identity is injected server-side: the caller's ``user_id`` and ``profile`` are
bound into every tool invocation — the LLM never supplies them. Degrades to a
deterministic keyword router when no OpenAI key is configured.
"""
import json

from backend.utils.logger import get_logger

logger = get_logger("copilot")

SYSTEM_PROMPT = (
    "You are the APhA RFP Copilot, an assistant for pharmacists discovering and "
    "winning pharmacy RFPs. You can search current RFPs, predict upcoming RFPs "
    "from posting cadence, assemble complementary pharmacist coalitions for an "
    "RFP, and simulate how profile changes affect win probability. Use the tools "
    "to gather facts before answering. Be concise, factual, and cite specific "
    "organizations, dates, and scores from tool results. Never invent RFP ids."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_rfps",
            "description": "Search current pharmacy RFPs by free-text query and/or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keywords, e.g. 'oncology' or 'medicaid'"},
                    "status": {"type": "string", "enum": ["open", "closed"]},
                    "limit": {"type": "integer", "default": 5},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "predict_upcoming_rfps",
            "description": "Predict RFPs expected to be posted soon, based on each organization's historical posting cadence. Personalized to the current pharmacist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "horizon_days": {"type": "integer", "default": 180},
                    "limit": {"type": "integer", "default": 5},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_coalition",
            "description": "Assemble a complementary team of pharmacists whose specialties cover a specific RFP's requirements. Requires an RFP id (get one from search_rfps first).",
            "parameters": {
                "type": "object",
                "properties": {"rfp_id": {"type": "string"}},
                "required": ["rfp_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_win_probability",
            "description": "Compute the current pharmacist's win probability for an RFP, optionally with hypothetical added specialties or a different location. Requires an RFP id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfp_id": {"type": "string"},
                    "add_specialties": {"type": "array", "items": {"type": "string"}},
                    "location_state": {"type": "string"},
                },
                "required": ["rfp_id"],
            },
        },
    },
]


def _execute_tool(name: str, args: dict, user_id: str, profile: dict) -> dict:
    """Run a tool with server-bound identity. Never trusts LLM-supplied identity."""
    if name == "search_rfps":
        from backend.graph.queries import search_rfps
        res = search_rfps(query=args.get("query"), status=args.get("status"),
                          limit=min(args.get("limit", 5), 10))
        return {"items": [
            {"id": r["id"], "title": r["title"], "organization": r.get("organization_name"),
             "deadline": r.get("deadline"), "status": r.get("status")}
            for r in res.get("items", [])
        ]}

    if name == "predict_upcoming_rfps":
        from backend.ai.foresight import forecast_reposts, personalize_predictions
        preds = forecast_reposts(horizon_days=args.get("horizon_days", 180))
        preds = personalize_predictions(preds, {
            "specialties": profile.get("specialties") or [],
            "location_state": profile.get("location_state"),
        })
        return {"items": preds[:min(args.get("limit", 5), 10)]}

    if name == "find_coalition":
        from backend.ai.coalition import find_coalition
        return find_coalition(args["rfp_id"])

    if name == "simulate_win_probability":
        from backend.ai.simulator import simulate
        hypo = {}
        if args.get("add_specialties"):
            hypo["specialties"] = list(set((profile.get("specialties") or []) + args["add_specialties"]))
        if args.get("location_state"):
            hypo["location_state"] = args["location_state"]
        return simulate(args["rfp_id"], profile, hypo)

    return {"error": f"unknown tool {name}"}


def _fallback(message: str, user_id: str, profile: dict) -> dict:
    """Deterministic single-tool router used when no OpenAI key is available."""
    m = message.lower()
    steps = []
    if any(k in m for k in ["predict", "upcoming", "before", "foresight", "cadence"]):
        result = _execute_tool("predict_upcoming_rfps", {"limit": 5}, user_id, profile)
        steps.append({"tool": "predict_upcoming_rfps", "result": result})
        items = result.get("items", [])
        if items:
            lines = [f"- {p['organization']} — ~{p['predicted_date']} ({p['confidence']}% confidence)"
                     for p in items]
            answer = "Here are the RFPs I expect to be posted soon:\n" + "\n".join(lines)
        else:
            answer = "I don't have enough posting history to predict upcoming RFPs yet."
    else:
        query = next((w for w in ["oncology", "medicaid", "340b", "mtm", "immunization",
                                   "clinical", "compliance", "specialty"] if w in m), None)
        result = _execute_tool("search_rfps", {"query": query, "status": "open", "limit": 5},
                              user_id, profile)
        steps.append({"tool": "search_rfps", "args": {"query": query}, "result": result})
        items = result.get("items", [])
        if items:
            lines = [f"- {r['title']} ({r.get('organization') or 'unknown org'}), due {r.get('deadline')}"
                     for r in items]
            answer = "Here are matching open RFPs:\n" + "\n".join(lines)
        else:
            answer = "I couldn't find matching RFPs. Try a different keyword."
    return {"answer": answer, "steps": steps, "used_llm": False}


def run_copilot(message: str, user_id: str, profile: dict, max_turns: int = 5) -> dict:
    """Plan-and-act loop. Returns {answer, steps, used_llm}."""
    try:
        from backend.utils.config import get_settings
        from openai import OpenAI

        settings = get_settings()
        if not settings.openai_api_key:
            return _fallback(message, user_id, profile)

        client = OpenAI(api_key=settings.openai_api_key)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        steps = []

        for _ in range(max_turns):
            resp = client.chat.completions.create(
                model=settings.openai_model_name,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.2,
            )
            msg = resp.choices[0].message
            if not msg.tool_calls:
                return {"answer": msg.content or "", "steps": steps, "used_llm": True}

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            })
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = _execute_tool(tc.function.name, args, user_id, profile)
                steps.append({"tool": tc.function.name, "args": args, "result": result})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, default=str)[:4000],
                })

        # Ran out of turns — ask for a final synthesis without more tools.
        final = client.chat.completions.create(
            model=settings.openai_model_name,
            messages=messages + [{"role": "user", "content": "Summarize your findings now."}],
            temperature=0.2,
        )
        return {"answer": final.choices[0].message.content or "", "steps": steps, "used_llm": True}
    except Exception as e:
        logger.warning(f"Copilot fell back to deterministic router: {e}")
        return _fallback(message, user_id, profile)
