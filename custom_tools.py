# your_custom_tools.py
import yfinance as yf
import requests
from bs4 import BeautifulSoup

def get_stock_price(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return f"""
Stock: {ticker}
Current Price: ${info.get('currentPrice')}
Day High: ${info.get('dayHigh')}
Day Low: ${info.get('dayLow')}
Volume: {info.get('volume')}
52-Week High: ${info.get('fiftyTwoWeekHigh')}
52-Week Low: ${info.get('fiftyTwoWeekLow')}
        """
    except Exception as e:
        return f"Error retrieving price data for {ticker}: {e}"

def get_fundamentals(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return f"""
Stock: {ticker}
P/E Ratio: {info.get('trailingPE')}
EPS: {info.get('trailingEps')}
Beta: {info.get('beta')}
Market Cap: {info.get('marketCap')}
Dividend Yield: {info.get('dividendYield')}
        """
    except Exception as e:
        return f"Error retrieving fundamentals for {ticker}: {e}"

def summarize_article(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([para.get_text() for para in paragraphs])
        return text[:1500] + "..." if len(text) > 1500 else text
    except Exception as e:
        return f"Error summarizing article at {url}: {e}"

def get_news_articles(query: str) -> str:
    # Placeholder: actual news search done by TavilySearch
    return f"Use the TavilySearch tool instead to find recent news for: {query}"
