from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from backend.app.core.config import get_db_path
from stock_research.application.use_cases import build_mvp1, import_csv_data, init_database
from stock_research.infrastructure.persistence import ResearchRepository

router = APIRouter(prefix="/api", tags=["research"])


class InitDatabaseResponse(BaseModel):
    db_path: str


class BuildMvp1Request(BaseModel):
    trade_date: str = Field(..., examples=["2024-06-07"])
    factor_version: str = "factor_v0_1"
    min_listed_days: int = 120
    min_avg_amount_20d: float = 50_000_000


class BuildMvp1Response(BaseModel):
    universe_rows: int
    universe_members: int
    factor_rows: int


class ImportCsvResponse(BaseModel):
    stocks: int = 0
    daily_bars: int = 0
    valuation: int = 0


@router.post("/database/init", response_model=InitDatabaseResponse)
def initialize_database() -> InitDatabaseResponse:
    db_path = init_database(get_db_path())
    return InitDatabaseResponse(db_path=str(db_path))


@router.post("/data/import-csv", response_model=ImportCsvResponse)
async def import_csv_files(
    stocks: UploadFile | None = File(default=None),
    daily_bars: UploadFile | None = File(default=None),
    valuation: UploadFile | None = File(default=None),
) -> ImportCsvResponse:
    if not any([stocks, daily_bars, valuation]):
        raise HTTPException(status_code=400, detail="Upload at least one CSV file.")

    with tempfile.TemporaryDirectory() as tmpdir:
        paths: dict[str, Path | None] = {"stocks": None, "daily_bars": None, "valuation": None}
        for key, upload in [("stocks", stocks), ("daily_bars", daily_bars), ("valuation", valuation)]:
            if upload is None:
                continue
            path = Path(tmpdir) / f"{key}.csv"
            path.write_bytes(await upload.read())
            paths[key] = path

        result = import_csv_data(
            get_db_path(),
            stocks_path=paths["stocks"],
            daily_bars_path=paths["daily_bars"],
            valuation_path=paths["valuation"],
        )
        return ImportCsvResponse(stocks=result.stocks, daily_bars=result.daily_bars, valuation=result.valuation)


@router.post("/mvp1/build", response_model=BuildMvp1Response)
def build_mvp1_endpoint(request: BuildMvp1Request) -> BuildMvp1Response:
    result = build_mvp1(
        get_db_path(),
        trade_date=request.trade_date,
        factor_version=request.factor_version,
        min_listed_days=request.min_listed_days,
        min_avg_amount_20d=request.min_avg_amount_20d,
    )
    return BuildMvp1Response(
        universe_rows=result.universe_rows,
        universe_members=result.universe_members,
        factor_rows=result.factor_rows,
    )


@router.get("/data/status")
def data_status() -> dict[str, Any]:
    repo = ResearchRepository(get_db_path())
    tables = ["stocks", "daily_bars", "valuation_daily", "universe_members", "factor_values"]
    status = {}
    for table in tables:
        try:
            df = repo.query(f"SELECT COUNT(*) AS rows FROM {table}")
            status[table] = int(df.loc[0, "rows"])
        except Exception:
            status[table] = None
    latest_dates = {}
    for table, column in [("daily_bars", "trade_date"), ("universe_members", "trade_date"), ("factor_values", "trade_date")]:
        try:
            df = repo.query(f"SELECT MAX({column}) AS latest_date FROM {table}")
            latest_dates[table] = _json_ready(df.loc[0, "latest_date"])
        except Exception:
            latest_dates[table] = None
    return {"db_path": str(get_db_path()), "tables": status, "latest_dates": latest_dates}


@router.get("/universe")
def get_universe(
    trade_date: str | None = None,
    members_only: bool = False,
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[dict[str, Any]]:
    repo = ResearchRepository(get_db_path())
    where = []
    params: list[Any] = []
    if trade_date:
        where.append("trade_date = ?")
        params.append(trade_date)
    if members_only:
        where.append("is_member = true")
    sql = "SELECT * FROM universe_members"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY trade_date DESC, is_member DESC, stock_code LIMIT ?"
    params.append(limit)
    return _df_records(repo.query(sql, params))


@router.get("/factors")
def get_factors(
    trade_date: str | None = None,
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[dict[str, Any]]:
    repo = ResearchRepository(get_db_path())
    params: list[Any] = []
    sql = "SELECT * FROM factor_values"
    if trade_date:
        sql += " WHERE trade_date = ?"
        params.append(trade_date)
    sql += " ORDER BY trade_date DESC, stock_code LIMIT ?"
    params.append(limit)
    return _df_records(repo.query(sql, params))


def _df_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{key: _json_ready(value) for key, value in row.items()} for row in df.to_dict(orient="records")]


def _json_ready(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value
