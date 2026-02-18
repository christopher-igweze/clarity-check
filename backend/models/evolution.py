"""Behavioral analysis schemas (CodeScene-style signals)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Hotspot(BaseModel):
    file_path: str
    change_count: int = Field(ge=1)


class ChangeCoupling(BaseModel):
    file_a: str
    file_b: str
    co_change_count: int = Field(ge=1)


class OwnershipRisk(BaseModel):
    file_path: str
    primary_author: str
    primary_author_share: int = Field(ge=0, le=100)


class EvolutionReport(BaseModel):
    hotspots: list[Hotspot] = Field(default_factory=list)
    change_coupling: list[ChangeCoupling] = Field(default_factory=list)
    ownership_risk: list[OwnershipRisk] = Field(default_factory=list)

