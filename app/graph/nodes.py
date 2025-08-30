from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Intent:
    raw: str
    parsed: Dict[str, Any]

@dataclass
class Plan:
    steps: List[str]
    sql: str = ""

@dataclass
class GuardedSQL:
    sql: str
    reason: str

@dataclass
class ExecutionResult:
    columns: list
    rows: list
    elapsed_sec: float
    error: str = None
