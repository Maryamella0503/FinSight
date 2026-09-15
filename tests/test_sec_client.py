from src.ingestion.sec_client import get_company_cik


def test_apple_cik():
    cik = get_company_cik("AAPL")

    assert cik == "0000320193"