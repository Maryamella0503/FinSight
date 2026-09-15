import os

import requests
from dotenv import load_dotenv
from src.ingestion.loader import download_filing

load_dotenv()

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")

SEC_TICKERS_URL = (
    "https://www.sec.gov/files/company_tickers.json"
)


def get_sec_headers() -> dict:
    """
    Return headers used for SEC requests.
    """
    if not SEC_USER_AGENT:
        raise ValueError(
            "SEC_USER_AGENT is not configured."
        )

    return {
        "User-Agent": SEC_USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
    }


def get_company_cik(ticker: str) -> str:
    """
    Resolve a stock ticker to its SEC Central Index Key (CIK).

    Example:
        AAPL -> 0000320193
    """

    response = requests.get(
        SEC_TICKERS_URL,
        headers=get_sec_headers(),
        timeout=30,
    )

    response.raise_for_status()

    companies = response.json()

    ticker = ticker.upper()

    for company in companies.values():
        if company["ticker"].upper() == ticker:
            return str(company["cik_str"]).zfill(10)

    raise ValueError(
        f"Ticker '{ticker}' was not found in SEC company data."
    )

def get_latest_10k(ticker: str) -> dict:
    """
    Find the most recent 10-K filing for a company.

    Returns filing metadata including the accession number,
    filing date, report date, and primary document.
    """

    cik = get_company_cik(ticker)

    submissions_url = (
        f"https://data.sec.gov/submissions/CIK{cik}.json"
    )

    response = requests.get(
        submissions_url,
        headers=get_sec_headers(),
        timeout=30,
    )

    response.raise_for_status()

    submissions = response.json()
    recent = submissions["filings"]["recent"]

    for index, form in enumerate(recent["form"]):
        if form == "10-K":
            return {
                "ticker": ticker.upper(),
                "company": submissions["name"],
                "cik": cik,
                "form": form,
                "filing_date": recent["filingDate"][index],
                "report_date": recent["reportDate"][index],
                "accession_number": recent["accessionNumber"][index],
                "primary_document": recent["primaryDocument"][index],
            }

    raise ValueError(
        f"No recent 10-K filing found for '{ticker.upper()}'."
    )

def build_filing_url(filing: dict) -> str:
    """
    Construct the SEC EDGAR URL for a filing's primary document.
    """

    cik = filing["cik"].lstrip("0")
    accession = filing["accession_number"].replace("-", "")
    primary_document = filing["primary_document"]

    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik}/{accession}/{primary_document}"
    )


def download_company_10k(ticker: str):
    """
    Find and download the latest 10-K filing for a company.
    """

    filing = get_latest_10k(ticker)
    filing_url = build_filing_url(filing)

    filename = (
        f"{filing['ticker']}_"
        f"{filing['report_date']}_10K.html"
    )

    output_path = download_filing(
        url=filing_url,
        filename=filename,
    )

    return {
        **filing,
        "filing_url": filing_url,
        "local_path": str(output_path),
    }