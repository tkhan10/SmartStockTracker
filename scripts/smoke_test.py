"""CI smoke test: import every module and execute each Streamlit page's
top-level code directly, without a live server or real API keys.

Streamlit widgets/session_state no-op safely when there's no ScriptRunContext
(confirmed locally), so this catches real Python errors -- import failures,
typos, broken calls into the service layer -- without needing a browser.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    import cache_utils  # noqa: F401
    import config  # noqa: F401
    import ui_common  # noqa: F401
    from providers import base, factory, finnhub_provider, yfinance_provider  # noqa: F401
    from services import finnhub_client, news_service, stock_service, watchlist_service  # noqa: F401
    from storage import db, models  # noqa: F401

    print("Pure logic modules imported OK")

    db.init_db()

    page_files = [
        ROOT / "app.py",
        ROOT / "pages" / "1_Watchlist.py",
        ROOT / "pages" / "2_Stock_Detail.py",
    ]
    for i, path in enumerate(page_files):
        load_module_from_path(f"smoke_page_{i}", path)
        print(f"{path.relative_to(ROOT)} executed OK")

    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
