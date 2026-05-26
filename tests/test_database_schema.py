from __future__ import annotations

import pandas as pd
import pytest

from stock_research.infrastructure.persistence import ResearchRepository, init_db
from stock_research.infrastructure.persistence.schema import CORE_TABLES, SCHEMA_VERSION


def test_init_db_creates_full_schema(tmp_path):
    db_path = tmp_path / "research.duckdb"
    init_db(db_path)
    repo = ResearchRepository(db_path)

    tables = set(repo.list_tables())
    assert set(CORE_TABLES).issubset(tables)
    assert repo.latest_schema_version() == SCHEMA_VERSION

    counts = repo.table_counts()
    assert set(CORE_TABLES).issubset(counts)
    assert counts["schema_versions"] >= 1


@pytest.mark.parametrize(
    ("table", "expected_columns"),
    [
        ("financial_reports", {"stock_code", "report_period", "announce_date", "roe", "profit_growth"}),
        ("labels", {"trade_date", "stock_code", "label_version", "future_excess_return", "top_quantile"}),
        ("model_runs", {"model_version", "algorithm", "factor_version", "label_version", "metrics_json"}),
        ("model_predictions", {"predict_date", "stock_code", "model_version", "score", "rank"}),
        ("selection_results", {"selection_date", "strategy_version", "stock_code", "selection_tier", "suggested_weight"}),
        ("portfolio_targets", {"portfolio_id", "target_date", "strategy_version", "stock_code", "target_weight"}),
        ("trade_plans", {"plan_id", "portfolio_id", "stock_code", "action", "status"}),
        ("trade_executions", {"execution_id", "plan_id", "price", "quantity", "is_follow_plan"}),
        ("portfolio_reviews", {"review_id", "portfolio_return", "max_drawdown", "win_rate"}),
        ("model_reviews", {"review_id", "model_version", "rank_ic", "retrain_required"}),
    ],
)
def test_core_table_columns_exist(tmp_path, table, expected_columns):
    db_path = tmp_path / "research.duckdb"
    repo = ResearchRepository(db_path)
    columns = set(repo.query(f"PRAGMA table_info('{table}')")["name"])
    assert expected_columns.issubset(columns)


def test_generic_write_table_supports_future_layers(tmp_path):
    db_path = tmp_path / "research.duckdb"
    repo = ResearchRepository(db_path)
    config = pd.DataFrame(
        {
            "strategy_version": ["strategy_balanced_v1"],
            "strategy_name": ["平衡模式"],
            "config_json": ['{"target_holding_count": 10}'],
            "is_active": [True],
            "created_at": [pd.Timestamp.now()],
        }
    )

    assert repo.write_table("strategy_configs", config, ["strategy_version"]) == 1
    assert repo.table_counts(["strategy_configs"])["strategy_configs"] == 1

    config.loc[0, "strategy_name"] = "平衡模式 v2"
    assert repo.write_table("strategy_configs", config, ["strategy_version"]) == 1
    rows = repo.read_table("strategy_configs")
    assert len(rows) == 1
    assert rows.loc[0, "strategy_name"] == "平衡模式 v2"
