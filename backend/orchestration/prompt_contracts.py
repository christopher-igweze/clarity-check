"""Prompt contract registry for orchestration and agent handoff stability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PromptContractName = Literal[
    "build_planner",
    "task_executor",
    "gate_reviewer",
    "replanner",
]


@dataclass(frozen=True)
class PromptContract:
    name: PromptContractName
    version: str
    owner: str
    description: str
    input_schema_ref: str
    output_schema_ref: str


_REGISTRY: dict[PromptContractName, PromptContract] = {
    "build_planner": PromptContract(
        name="build_planner",
        version="v0.1.0",
        owner="team",
        description="Expands build objective into a DAG plan.",
        input_schema_ref="BuildCreateRequest",
        output_schema_ref="DagNode[]",
    ),
    "task_executor": PromptContract(
        name="task_executor",
        version="v0.1.0",
        owner="team",
        description="Runs one DAG node with deterministic guardrails.",
        input_schema_ref="DagNode + BuildRun",
        output_schema_ref="TaskRun",
    ),
    "gate_reviewer": PromptContract(
        name="gate_reviewer",
        version="v0.1.0",
        owner="team",
        description="Validates merge/test/policy gates.",
        input_schema_ref="TaskRun + BuildRun",
        output_schema_ref="PolicyViolation[]",
    ),
    "replanner": PromptContract(
        name="replanner",
        version="v0.1.0",
        owner="team",
        description="Selects CONTINUE/MODIFY_DAG/REDUCE_SCOPE/ABORT action.",
        input_schema_ref="BuildRun + failures",
        output_schema_ref="ReplanDecision",
    ),
}


def list_prompt_contracts() -> list[PromptContract]:
    return list(_REGISTRY.values())


def get_prompt_contract(name: PromptContractName) -> PromptContract:
    return _REGISTRY[name]

