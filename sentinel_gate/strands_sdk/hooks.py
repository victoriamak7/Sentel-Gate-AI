from abc import ABC, abstractmethod
from typing import Dict, Any

class PipelineContext:
    def __init__(self, raw_prompt: str, user_id: str, session_id: str):
        self.raw_prompt = raw_prompt
        self.user_id = user_id
        self.session_id = session_id
        self.metadata: Dict[str, Any] = {}
        self.interrupted = False
        self.interruption_reason = ""


class StrandsHook(ABC):
    @abstractmethod
    def on_before_eval(self, ctx: PipelineContext) -> None:
        pass

    @abstractmethod
    def on_after_eval(self, ctx: PipelineContext, result: Dict[str, Any]) -> None:
        pass


class AuditLoggingHook(StrandsHook):
    def on_before_eval(self, ctx: PipelineContext) -> None:
        pass

    def on_after_eval(self, ctx: PipelineContext, result: Dict[str, Any]) -> None:
        ctx.metadata["audit_logged"] = True
