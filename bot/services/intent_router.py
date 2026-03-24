"""LLM-powered intent router with tool calling.

This module implements natural language routing where the LLM decides which
backend API tools to call based on user input.
"""

import json
import sys
from typing import Any

import httpx


# Define the 9 backend API tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get all items from the LMS backend (labs, tasks, etc.)",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of learners/students",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": "Optional group ID to filter learners"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get scores for a learner or lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "learner_id": {"type": "string", "description": "Learner ID to get scores for"},
                    "lab_id": {"type": "string", "description": "Lab ID to get scores for"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get pass rates for tasks in a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID or name to get pass rates for"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get timeline of events or activities",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_id": {"type": "string", "description": "Lab ID to get timeline for"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get list of student groups",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top performing learners",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of top learners to return", "default": 10},
                    "lab_id": {"type": "string", "description": "Optional lab ID to filter by"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate for a lab or overall",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_id": {"type": "string", "description": "Lab ID to get completion rate for"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger data sync from autochecker API",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

TOOL_MAP = {
    "get_items": "get_items",
    "get_learners": "get_learners",
    "get_scores": "get_scores",
    "get_pass_rates": "get_pass_rates",
    "get_timeline": "get_timeline",
    "get_groups": "get_groups",
    "get_top_learners": "get_top_learners",
    "get_completion_rate": "get_completion_rate",
    "trigger_sync": "trigger_sync",
}


class IntentRouter:
    """LLM-powered intent router with tool calling."""

    def __init__(self, lms_url: str, lms_api_key: str, llm_api_key: str, llm_base_url: str, llm_model: str):
        self.lms_url = lms_url.rstrip("/")
        self.lms_api_key = lms_api_key
        self.llm_client = LLMClientForRouter(llm_api_key, llm_base_url, llm_model)
        self.lms_headers = {
            "Authorization": f"Bearer {lms_api_key}",
            "Content-Type": "application/json",
        }

    async def route(self, message: str) -> str:
        """Route a user message through the LLM to get a response.

        Args:
            message: The user's input message.

        Returns:
            The final response to send to the user.
        """
        system_prompt = """You are an assistant for a Learning Management System. 
You have access to backend API tools to fetch data about labs, scores, learners, and more.

When a user asks a question:
1. First understand what they're asking
2. Call the appropriate tool(s) to get the data
3. Use the tool results to formulate a helpful response

For multi-step questions (e.g., "which lab has the lowest pass rate?"):
1. First get the list of labs using get_items
2. Then get pass rates for each lab using get_pass_rates
3. Compare and return the lab with the lowest rate

Available tools:
- get_items: Get all items (labs, tasks)
- get_learners: Get list of learners
- get_scores: Get scores for a learner or lab
- get_pass_rates: Get pass rates for tasks in a lab (requires 'lab' parameter)
- get_timeline: Get timeline of events
- get_groups: Get student groups
- get_top_learners: Get top performing learners
- get_completion_rate: Get completion rate
- trigger_sync: Trigger data sync from autochecker

For greetings or casual messages, respond naturally without calling tools.
For gibberish or unclear input, ask for clarification politely."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        # Try LLM first, fallback to keyword-based routing if LLM fails
        result = await self._run_tool_loop(messages)
        
        # Check if LLM returned an error message (fallback needed)
        if "having trouble connecting" in result.lower() or "couldn't process" in result.lower():
            print("[DEBUG] LLM returned error, using fallback routing", file=sys.stderr)
            return await self._fallback_route(message)
        
        return result

    async def _fallback_route(self, message: str) -> str:
        """Fallback routing when LLM is unavailable.

        Uses keyword matching as a last resort.

        Args:
            message: The user's message.

        Returns:
            Response based on keyword detection.
        """
        msg_lower = message.lower().strip()
        
        # Greetings
        if any(g in msg_lower for g in ["hello", "hi ", "hi!", "hey", "greetings"]):
            return "Hello! 👋 I'm your Learning Management System assistant. You can ask me about labs, scores, pass rates, and more. Try 'what labs are available?' or 'show me scores for lab 4'."
        
        # Gibberish detection (very short or no vowels)
        if len(msg_lower) < 3 or (len(msg_lower) < 5 and sum(c in 'aeiou' for c in msg_lower) == 0):
            return "I'm not sure I understood that. Could you rephrase? You can ask me about labs, scores, or your progress."
        
        # Labs query
        if "lab" in msg_lower and ("available" in msg_lower or "list" in msg_lower or "what" in msg_lower):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.lms_url}/items/", headers=self.lms_headers, timeout=10.0)
                    response.raise_for_status()
                    items = response.json()
                    labs = [i for i in items if i.get("type") == "lab"]
                    if labs:
                        lab_list = "\n".join([f"• {l.get('title', l.get('name', 'Unknown'))}" for l in labs[:10]])
                        return f"Here are the available labs:\n\n{lab_list}"
                except Exception:
                    pass
            return "I couldn't fetch the labs list. Please try again later."
        
        # Scores query
        if "score" in msg_lower:
            # Try to extract lab number
            import re
            match = re.search(r'lab[- ]?(\d+)', msg_lower)
            lab_id = match.group(1) if match else "1"
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        f"{self.lms_url}/analytics/pass-rates",
                        headers=self.lms_headers,
                        params={"lab": lab_id},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    scores = response.json()
                    if scores:
                        lines = [f"Scores for lab {lab_id}:"]
                        for item in scores:
                            task = item.get("task", "Unknown")
                            rate = item.get("avg_score", 0)
                            lines.append(f"  • {task}: {rate:.1f}%")
                        return "\n".join(lines)
                except Exception:
                    pass
            return f"I couldn't fetch scores for lab {lab_id}. Please try again later."
        
        # Pass rate / lowest query (multi-step)
        if "lowest" in msg_lower and "pass rate" in msg_lower:
            # Get all labs
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.lms_url}/items/", headers=self.lms_headers, timeout=10.0)
                    response.raise_for_status()
                    items = response.json()
                    labs = [i for i in items if i.get("type") == "lab"][:5]  # Limit to 5 for multi-step

                    # Get pass rates for each
                    lab_rates = []
                    for lab in labs:
                        lab_id = str(lab.get("id", ""))
                        try:
                            resp = await client.get(
                                f"{self.lms_url}/analytics/pass-rates",
                                headers=self.lms_headers,
                                params={"lab": lab_id},
                                timeout=10.0
                            )
                            if resp.status_code == 200:
                                scores = resp.json()
                                if scores:
                                    avg = sum(s.get("avg_score", 0) for s in scores) / len(scores)
                                    lab_rates.append((lab.get("title", f"Lab {lab_id}"), avg))
                        except Exception:
                            continue

                    if lab_rates:
                        lowest = min(lab_rates, key=lambda x: x[1])
                        return f"The lab with the lowest pass rate is **{lowest[0]}** with an average of {lowest[1]:.1f}%."
                except Exception:
                    pass
            return "I couldn't analyze pass rates. Please try again later."
        
        # Default: helpful fallback
        return "I can help you with:\n• Listing available labs\n• Showing scores for a specific lab\n• Finding the lowest/highest pass rates\n• Viewing top learners\n\nTry asking 'what labs are available?' or 'show me scores for lab 4'."

    async def _run_tool_loop(self, messages: list[dict]) -> str:
        """Run the LLM tool calling loop.

        Args:
            messages: The conversation messages.

        Returns:
            The final response.
        """
        max_iterations = 5  # Prevent infinite loops

        for _ in range(max_iterations):
            response = await self.llm_client.chat_with_tools(messages, TOOLS)

            # Check if LLM wants to call a tool
            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                # LLM returned a final answer
                return response.get("content", "I couldn't process that request.")

            # Execute tool calls and collect results
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                arguments = function.get("arguments", "{}")

                print(f"[DEBUG] Calling tool: {tool_name} with args: {arguments}", file=sys.stderr)

                try:
                    args_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
                except json.JSONDecodeError:
                    args_dict = {}

                result = await self._execute_tool(tool_name, args_dict)
                tool_results.append({
                    "tool_call_id": tool_call.get("id"),
                    "name": tool_name,
                    "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                })

            # Add assistant message with tool calls and tool results to conversation
            messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            })

            # Add tool results as separate messages
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["content"],
                })

        # If we reach max iterations, return a fallback message
        return "I'm having trouble processing this request. Please try rephrasing your question."

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """Execute a backend API tool.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.

        Returns:
            Tool execution result.
        """
        async with httpx.AsyncClient() as client:
            if tool_name == "get_items":
                response = await client.get(f"{self.lms_url}/items/", headers=self.lms_headers, timeout=10.0)
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_learners":
                params = {}
                if arguments.get("group_id"):
                    params["group_id"] = arguments["group_id"]
                response = await client.get(f"{self.lms_url}/learners/", headers=self.lms_headers, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_scores":
                params = {}
                if arguments.get("learner_id"):
                    params["learner_id"] = arguments["learner_id"]
                if arguments.get("lab_id"):
                    params["lab_id"] = arguments["lab_id"]
                response = await client.get(f"{self.lms_url}/scores/", headers=self.lms_headers, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_pass_rates":
                lab = arguments.get("lab", "")
                response = await client.get(
                    f"{self.lms_url}/analytics/pass-rates",
                    headers=self.lms_headers,
                    params={"lab": lab},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_timeline":
                params = {}
                if arguments.get("lab_id"):
                    params["lab_id"] = arguments["lab_id"]
                response = await client.get(f"{self.lms_url}/timeline/", headers=self.lms_headers, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_groups":
                response = await client.get(f"{self.lms_url}/groups/", headers=self.lms_headers, timeout=10.0)
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_top_learners":
                params = {"limit": arguments.get("limit", 10)}
                if arguments.get("lab_id"):
                    params["lab_id"] = arguments["lab_id"]
                response = await client.get(
                    f"{self.lms_url}/analytics/top-learners",
                    headers=self.lms_headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            elif tool_name == "get_completion_rate":
                params = {}
                if arguments.get("lab_id"):
                    params["lab_id"] = arguments["lab_id"]
                response = await client.get(
                    f"{self.lms_url}/analytics/completion-rate",
                    headers=self.lms_headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            elif tool_name == "trigger_sync":
                response = await client.post(
                    f"{self.lms_url}/pipeline/sync",
                    headers=self.lms_headers,
                    json={},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()

            else:
                return {"error": f"Unknown tool: {tool_name}"}


class LLMClientForRouter:
    """LLM client optimized for tool calling."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> dict:
        """Chat with the LLM with tool calling support.

        Args:
            messages: Conversation messages.
            tools: List of tool definitions.

        Returns:
            LLM response with potential tool calls.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "tools": tools,
                        "tool_choice": "auto",
                        "max_tokens": 1000,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {})
        except httpx.HTTPError as e:
            print(f"[DEBUG] LLM API error: {e}", file=sys.stderr)
            return {"content": "Sorry, I'm having trouble connecting to the AI service right now."}
