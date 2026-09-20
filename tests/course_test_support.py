"""Scripted wire responses for behavioral regressions; never used by course code."""

from copy import deepcopy
import json


class ScriptedClient:
    mode = "stub"
    model = "fixture-client"
    last_latency_ms = 1.0

    def __init__(self, responses):
        self.responses = deepcopy(list(responses))
        self.requests = []
        self.calls = 0

    def chat(self, messages, tools=None, temperature=0.0, tool_choice=None):
        self.requests.append(deepcopy({"messages": messages, "tools": tools,
                                      "temperature": temperature, "tool_choice": tool_choice}))
        self.calls += 1
        if not self.responses:
            raise AssertionError("unexpected model call")
        return self.responses.pop(0)


def reply(content="Ready.", tool_calls=None, usage=None):
    message = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls
    result = {"choices": [{"message": message, "finish_reason": "stop"}]}
    if usage is not None:
        result["usage"] = usage
    return result


def call(name, arguments, call_id="call-1"):
    return {"id": call_id, "type": "function", "function": {
        "name": name, "arguments": json.dumps(arguments)}}
