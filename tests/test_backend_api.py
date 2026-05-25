from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from stock_research.infrastructure.persistence import ResearchRepository


def test_backend_mvp1_flow(tmp_path, monkeypatch):
    db_path = tmp_path / "research.duckdb"
    monkeypatch.setenv("STOCK_RESEARCH_DB", str(db_path))
    client = TestClient(app)

    assert client.get("/health").json() == {"status": "ok"}
    init_response = client.post("/api/database/init")
    assert init_response.status_code == 200
    assert init_response.json()["db_path"] == str(db_path)

    stocks_csv = (
        "stock_code,stock_name,exchange,list_date,industry,is_st,is_active\n"
        "000001,平安银行,SZ,1991-04-03,银行,false,true\n"
        "600519,贵州茅台,SH,2001-08-27,食品饮料,false,true\n"
        "000002,ST测试,SZ,1991-01-29,房地产,true,true\n"
    )
    daily_csv = _daily_csv(["000001", "600519", "000002"])
    valuation_csv = "trade_date,stock_code,pe_ttm,pb,market_cap\n2024-04-29,000001,5.2,0.6,200000000000\n"

    import_response = client.post(
        "/api/data/import-csv",
        files={
            "stocks": ("stocks.csv", stocks_csv, "text/csv"),
            "daily_bars": ("daily.csv", daily_csv, "text/csv"),
            "valuation": ("valuation.csv", valuation_csv, "text/csv"),
        },
    )
    assert import_response.status_code == 200
    assert import_response.json()["stocks"] == 3

    build_response = client.post("/api/mvp1/build", json={"trade_date": "2024-04-29"})
    assert build_response.status_code == 200
    assert build_response.json()["universe_members"] == 2

    status = client.get("/api/data/status").json()
    assert status["tables"]["stocks"] == 3
    assert status["tables"]["factor_values"] > 0

    universe = client.get("/api/universe", params={"trade_date": "2024-04-29", "members_only": True}).json()
    assert {row["stock_code"] for row in universe} == {"000001.SZ", "600519.SH"}

    repo = ResearchRepository(db_path)
    assert len(repo.read_table("daily_bars")) > 0


def _daily_csv(stock_codes: list[str]) -> str:
    rows = ["trade_date,stock_code,open,high,low,close,pre_close,volume,amount,turnover_rate,adj_factor,is_suspended,limit_up_price,limit_down_price"]
    start = date(2024, 1, 1)
    for i in range(120):
        d = start + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        for j, code in enumerate(stock_codes):
            close = 10 + j * 20 + i * 0.05
            rows.append(
                f"{d},{code},{close * 0.99:.2f},{close * 1.01:.2f},{close * 0.98:.2f},{close:.2f},"
                f"{close * 0.995:.2f},1000000,{80_000_000 + j * 20_000_000},1.0,1.0,false,"
                f"{close * 1.1:.2f},{close * 0.9:.2f}"
            )
    return "\n".join(rows) + "\n"
