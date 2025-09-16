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


def fetch_articles(limit: int | None = None) -> Iterable[Dict[str, Any]]:
    """
    Pobiera artykuły z widoku dbo.ArticleMetadataView
    Kolumny: Id, Title, Content, Url, CategoryName, ProductName, ProductGroupName
    """
    top = f"TOP ({limit})" if limit else ""
    sql = f"""
        SELECT {top}
            Id,
            Title,
            Content,
            Url,
            CategoryName,
            ProductName,
            ProductGroupName
        FROM dbo.ArticleMetadataView
        WHERE Content IS NOT NULL AND LEN(Content) > 0;
    """
    engine = get_engine()
    with engine.connect() as conn:
        for row in conn.execute(sa.text(sql)):
            yield dict(row._mapping)
