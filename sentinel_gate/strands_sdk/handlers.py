from typing import Dict, Any, Tuple
from sentinel_gate.core.decider_2b import decider_2b_agent
from sentinel_gate.core.models import PolicyCategory, PolicyEnforcementAction
from sentinel_gate.strands_sdk.interventions import (
    BlockImmediateIntervention,
    RedactAndForwardIntervention,
    PassThroughIntervention,
    HoldForReviewIntervention,
    InterventionResult
)

class PolicyFirewallHandler:
    """
    Core Strands Agents SDK Handler:
    Runs Decider 2B inline before any generative model inference.
    Executes policy classification in ~115ms and dispatches corresponding intervention.
    """

    def __init__(self):
        self.decider = decider_2b_agent
        self.interventions = {
            PolicyCategory.CONFIDENTIAL_BLOCKED: BlockImmediateIntervention(),
            PolicyCategory.SENSITIVE_PII: RedactAndForwardIntervention(),
            PolicyCategory.PUBLIC_SAFE: PassThroughIntervention(),
            PolicyCategory.UNCERTAIN_REVIEW: HoldForReviewIntervention()
        }

    def handle(self, prompt: str) -> Tuple[Dict[str, Any], InterventionResult]:
        # 1. Run Decider 2B inline evaluation
        decision = self.decider.evaluate(prompt)
        category = decision["category"]

        # 2. Select and execute intervention
        intervention = self.interventions.get(category, self.interventions[PolicyCategory.UNCERTAIN_REVIEW])
        intervention_result = intervention.execute(prompt, decision)

        return decision, intervention_result
