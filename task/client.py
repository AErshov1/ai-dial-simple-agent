import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        # 1. If not api_key then raise error
        # 2. Add `self.__endpoint` with formatted `endpoint` with model (model=deployment_name):
        #   - f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        # 3. Add `self.__api_key`
        # 4. Prepare tools dict where key will be tool name and value will
        # 5. Prepare tools list with tool schemas
        # 6. Optional: print endpoint and tools schemas
        if not api_key:
            raise ValueError("[DialClient] API key is required")

        self._api_key = api_key
        self._endpoint = f"{
            endpoint}/openai/deployments/{deployment_name}/chat/completions"

        self._tools: dict(str, BaseTool) = {}
        for tool in tools or []:
            self._tools[tool.name] = tool

        print(f"{'='*30} DIAL CLIENT {'=' *
                                      30}\nEndpoint: {self._endpoint}\nTools: {[str(key) for key in self._tools.keys()]}\n{'='*80}")

    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        # 1. create `headers` dict with:
        #   - "api-key": self._api_key
        #   - "Content-Type": "application/json"
        # 2. create `request_data` dict with:
        #   - "messages": [msg.to_dict() for msg in messages]
        #   - "tools": self._tools
        # 3. Optional: print request (message history)
        # 4. Make POST request (requests) with:
        #   - url=self._endpoint
        #   - headers=headers
        #   - json=request_data
        # 5. If response status code is 200:
        #   - get response as json
        #   - get "choices" from response json
        #   - get first choice
        #   - Optional: print choice
        #   - Get `message` from `choice` and assign to `message_data` variable
        #   - Get `content` from `message` and assign to `content` variable
        #   - Get `tool_calls` from `message` and assign to `tool_calls` variable
        #   - Create `ai_response` Message (with AI role, `content` and `tool_calls`)
        #   - If `choice` `finish_reason` is `tool_calls`:
        #       Yes:
        #           - append `ai_response` to `messages`
        #           - call `_process_tool_calls` with `tool_calls` and assign result to `tool_messages` variable
        #           - add `tool_messages` to `messages` (use `extend` method)
        #           - make recursive call (return `get_completion` with `messages` and `print_request`)
        #       No: return `ai_response` (final assistant response)
        # Otherwise raise exception

        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }

        tools: list[BaseTool] = [t for t in self._tools.values()]
        request_payload = {
            "messages": [msg.to_dict() for msg in messages],
            "tools": [t.schema for t in tools],
            "stream": False
        }

        print(f"{'='*34} REQUEST {'=' *
              35}\n{json.dumps(request_payload, indent=2)}\n{'='*80}")

        response = requests.post(
            url=self._endpoint, headers=headers, json=request_payload)

        if response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}")

        response_json = response.json()
        choices = response_json.get("choices", [])
        if not choices:
            raise Exception("No choices found in response")

        choice = choices[0]
        print(f"{'='*31} RESPONSE CONTENT {'=' *
              31}\n{json.dumps(choice, indent=2)}\n{'='*80}")

        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "")
        if finish_reason == "tool_calls":
            ai_response = Message(
                role=Role.AI,
                content=message.get("content", ""),
                tool_calls=message.get("tool_calls", [])
            )

            tool_calls = message.get("tool_calls", [])
            tool_messages = self._process_tool_calls(tool_calls)
            if tool_messages:
                messages.append(ai_response)
                messages.extend(tool_messages)
                return self.get_completion(messages, print_request=True)

        return Message(
            role=Role.AI,
            content=message.get("content", ""),
            tool_calls=message.get("tool_calls", [])
        )

    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        tool_messages = []
        for tool_call in tool_calls:
            # 1. Get `id` from `tool_call` and assign to `tool_call_id` variable
            # 2. Get `function` from `tool_call` and assign to `function` variable
            # 3. Get `name` from `function` and assign to `function_name` variable
            # 4. Get `arguments` from `function` as json (json.loads) and assign to `arguments` variable
            # 5. Call `_call_tool` with `function_name` and `arguments`, and assign to `tool_execution_result` variable
            # 6. Append to `tool_messages` Message with:
            #       - role=Role.TOOL
            #       - name=function_name
            #       - tool_call_id=tool_call_id
            #       - content=tool_execution_result
            # 7. print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")
            # 8. Return `tool_messages`
            # -----
            # FYI: It is important to provide `tool_call_id` in TOOL Message. By `tool_call_id` LLM make a  relation
            #      between Assistant message `tool_calls[i][id]` and message in history.
            #      In case if no Tool message presented in history (no message at all or with different tool_call_id),
            #      then LLM with answer with Error (that not find tool message with specified id).
            tool_call_id = tool_call.get("id")
            function = tool_call.get("function", {})
            function_name = function.get("name")
            arguments_json = function.get("arguments", "{}")
            arguments = json.loads(arguments_json)
            tool_output = self._call_tool(function_name, arguments)

            print(f"{'='*50}\nFUNCTION '{function_name}'\n{tool_output}\n{'='*50}")

            tool_messages.append(Message(
                role=Role.TOOL, name=function_name, tool_call_id=tool_call_id, content=tool_output))

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        # Get tool from `__tools_dict`, id present then return executed result, otherwise return `f"Unknown function: {function_name}"`
        tool = self._tools.get(function_name)
        if not tool:
            return f"Unknown function: {function_name}"

        return tool.execute(arguments)
