"""AI agent core: manages conversation history and tool-call loop."""

import json
import os
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from .tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS

SYSTEM_PROMPT = """You are a helpful AI assistant with access to the following tools:

- **calculate**: Evaluate mathematical expressions
- **get_current_datetime**: Get the current date and time
- **search_web**: Search the web for information
- **convert_units**: Convert between units (length, weight, temperature)

Use these tools whenever they would help answer the user's question accurately.
Always be concise, friendly, and helpful. When using tools, explain what you are doing.
"""

MAX_TOOL_ROUNDS = 5  # Prevent infinite tool-call loops


class Agent:
    """Stateless agent that processes a conversation and returns the next assistant message."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    async def chat(
        self,
        messages: list[dict],
    ) -> tuple[str, list[dict]]:
        """
        Run the agent for one user turn.

        Args:
            messages: Full conversation history (list of role/content dicts).
                      Must already include the latest user message.

        Returns:
            (reply_text, updated_messages) where updated_messages includes all
            new assistant and tool messages appended during this turn.
        """
        history: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ]
        new_messages: list[dict] = []

        for _ in range(MAX_TOOL_ROUNDS):
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=history,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            choice = response.choices[0]
            assistant_msg = choice.message

            # Convert to plain dict for serialisation
            assistant_dict: dict = {"role": "assistant", "content": assistant_msg.content or ""}
            if assistant_msg.tool_calls:
                assistant_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_msg.tool_calls
                ]

            history.append(assistant_dict)
            new_messages.append(assistant_dict)

            # No tool calls – we have the final reply
            if not assistant_msg.tool_calls:
                return assistant_msg.content or "", new_messages

            # Execute tool calls
            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                fn = TOOL_FUNCTIONS.get(fn_name)
                if fn is None:
                    tool_result = f"Error: unknown tool '{fn_name}'"
                else:
                    try:
                        args = json.loads(tool_call.function.arguments)
                        tool_result = fn(**args)
                    except Exception as exc:
                        tool_result = f"Error calling {fn_name}: {exc}"

                tool_msg: dict = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
                history.append(tool_msg)
                new_messages.append(tool_msg)

        # Fallback if max rounds hit
        return "I'm sorry, I was unable to complete the request within the allowed steps.", new_messages
