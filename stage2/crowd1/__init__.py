"""CROWD-1 Stage 2: registered predictions P1, P1-delay, P2, P2-delay, P3, P4, P6.

The engine is the Stage 1 engine extended with the capabilities Stage 2 needs
(state save/resume, seed injection, generation tracking, frozen-background
operator checks, compact initial-class ids).  Every extension is an OPTIONAL
parameter whose default reproduces Stage 1 behaviour exactly; `regression_stage1.py`
re-runs the whole Stage 1 suite against this engine and diffs the certified table.
"""
__spec_version__ = "review_packet_v0_6_1.md / PROCESS SPECIFICATION v0.6"
__design_version__ = "crowd1_cs_design_and_manuscript_brief_v0_3.md / Part A (v0.3)"
__stage__ = "Stage 2 (A4: P1, P1-delay, P2, P2-delay, P3, P4, P6) under A6 with Holm"
__archive_version__ = "s2-v2 (s2-v1 retained in outputs_v1/; see BUGLOG.md B3)"
