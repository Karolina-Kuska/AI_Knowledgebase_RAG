# src/ingest/sql_loader.py
import sqlalchemy as sa
import pyodbc
from urllib.parse import quote_plus
from src.utils.settings import settings
from typing import Iterable, Dict, Any

def _pick_odbc_driver() -> str:
    drivers = pyodbc.drivers()
    if "ODBC Driver 18 for SQL Server" in drivers:
        return "ODBC Driver 18 for SQL Server"
    candidates = [d for d in drivers if "ODBC Driver" in d and "SQL Server" in d]
    return sorted(candidates)[-1] if candidates else "ODBC Driver 17 for SQL Server"

def get_engine():
    driver = _pick_odbc_driver()
    odbc_str = (
        f"Driver={{{driver}}};"
        f"Server=tcp:{settings.AZURE_SQL_SERVER},1433;"
        f"Database={settings.AZURE_SQL_DATABASE};"
        f"Uid={settings.AZURE_SQL_USERNAME};"
        f"Pwd={settings.AZURE_SQL_PASSWORD};"
        f"Encrypt={'yes' if settings.AZURE_SQL_ENCRYPT else 'no'};"
        "TrustServerCertificate=no;Connection Timeout=30;"
    )
    conn_str = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)
    return sa.create_engine(conn_str, fast_executemany=True)

def fetch_articles_since(dt_iso: str | None) -> Iterable[Dict[str, Any]]:
    """
    Pobiera rekordy z widoku; jeżeli dt_iso podane, zwraca tylko nowsze.
    Kolumny aliasujemy na stałe nazwy (CreatedAt/UpdatedAt), niezależnie od case w bazie.
    """
    cond = "WHERE Content IS NOT NULL AND LEN(Content) > 0"
    if dt_iso:
        cond += " AND UpdatedAt > CONVERT(datetime2, :wm)"

    sql = f"""
      SELECT
        Id,
        Title,
        Content,
        Url,
        CategoryName,
        ProductName,
        ProductGroupName,
        CreatedAt   AS CreatedAt,
        UpdatedAt   AS UpdatedAt
      FROM dbo.ArticleMetadataView
      {cond}
      ORDER BY UpdatedAt ASC
    """
    with get_engine().connect() as c:
        params = {"wm": dt_iso} if dt_iso else {}
        for row in c.execute(sa.text(sql), params):
            yield dict(row._mapping)
