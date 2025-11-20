# AutoCodeFixer — AI Code Reviewer + Refactoring Assistant

This project is a scaffold for a GenAI-based code reviewer and refactoring assistant.
It implements:
- repo ingestion (git clone / local path)
- static analysis via flake8, pylint, bandit, mypy
- understanding agent (summarization via LLM wrapper)
- bug detection & prioritization
- refactor suggestion agent that outputs unified diffs
- patch apply sandbox + pytest run
- Streamlit UI for demo

The project runs in **mock mode** by default (no API keys required). You can plug your OpenAI API key later by exporting `OPENAI_API_KEY`.

See `PLAN.md` for project plan and checkpoint mapping.

Quick start:
1. Create virtualenv and install requirements
2. Run:
   python scripts/run_review.py --repo https://github.com/<user>/<sample_repo>.git --out reports/output
3. Optional: open the Streamlit UI:
   streamlit run web/app.py
