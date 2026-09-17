"""The café spine: one agent the learner grows across S01-S12.

Course logic is Python standard library only. The single external boundary is
`cafe.model`, which speaks the OpenAI-compatible /chat/completions wire format
over `urllib`. No SDK, no third-party dependency.
"""

__all__ = ["domain", "model", "tools"]
