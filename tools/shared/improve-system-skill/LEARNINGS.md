# LEARNINGS — /improve-system changelog

Running log of task learnings and the edits they drove. Newest at the bottom. Each entry names one target file; the edit is applied only after DVN approves it.

## 2026-06-23 — Four-project framework build (Board of Advisors, Command Center, AI Website, Internal OS)
- **Worked:** Mapped the three-folder OS model (Knowledge/Skills/Projects) onto the existing repo instead of inventing a new structure; matched the aiDrVN suite conventions (deterministic Python + --selftest + approval-gated).
- **Change:** When building a new skill, write the --selftest assertions against the exact output string including markdown formatting (caught a Status line bold mismatch on first run).
- **Target:** skill → `tools/shared/improve-system-skill/scripts/capture_feedback.py`
- **Status:** proposed
