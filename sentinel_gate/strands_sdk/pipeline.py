from typing import List, Dict, Any, Optional
from sentinel_gate.strands_sdk.hooks import StrandsHook, PipelineContext, AuditLoggingHook
from sentinel_gate.strands_sdk.handlers import PolicyFirewallHandler
from sentinel_gate.strands_sdk.interventions import InterventionResult

class StrandsAgentPipeline:
    """
    Strands Agents SDK Pipeline orchestrating hooks, handlers,
    inline Decider 2B inspection, and external cloud LLM dispatch.
    """

    def __init__(self):
        self.hooks: List[StrandsHook] = [AuditLoggingHook()]
        self.firewall_handler = PolicyFirewallHandler()

    def add_hook(self, hook: StrandsHook) -> None:
        self.hooks.append(hook)

    def execute_firewall(self, prompt: str, user_id: str = "emp_01", session_id: str = "default_session"):
        ctx = PipelineContext(raw_prompt=prompt, user_id=user_id, session_id=session_id)

        # Pre-evaluation hooks
        for hook in self.hooks:
            hook.on_before_eval(ctx)

        # Policy decision via Decider 2B & Handler
        decision, intervention_result = self.firewall_handler.handle(prompt)

        # Post-evaluation hooks
        for hook in self.hooks:
            hook.on_after_eval(ctx, decision)

        return ctx, decision, intervention_result

agent_pipeline = StrandsAgentPipeline()
