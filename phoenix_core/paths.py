from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
LEDGER_DB = DATA_DIR / "phoenix.db"
PORTFOLIO_JSON = DATA_DIR / "portfolio.json"
LLM_COST_LOG = DATA_DIR / "llm_costs.csv"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
