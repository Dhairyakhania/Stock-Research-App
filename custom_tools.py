from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
import os
from datetime import datetime

llm = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

def get_stock_price(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        # Get the latest available data
        hist = stock.history(period="1d")
        
        if hist.empty:
            return f"No data available for {ticker}"
        
        # Get the most recent values
        current_price = round(hist['Close'].iloc[-1], 2)
        day_high = round(hist['High'].max(), 2)
        day_low = round(hist['Low'].min(), 2)
        volume = int(hist['Volume'].sum())
        
        # Get 52-week data
        hist_52w = stock.history(period="1y")
        year_high = round(hist_52w['High'].max(), 2) if not hist_52w.empty else "N/A"
        year_low = round(hist_52w['Low'].min(), 2) if not hist_52w.empty else "N/A"
        
        # Include timestamp to see when data was fetched
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
Stock: {ticker} (Data as of {timestamp})
Current Price: ${current_price}
Day High: ${day_high}
Day Low: ${day_low}
Volume: {volume:,}
52-Week High: ${year_high}
52-Week Low: ${year_low}
        """
    except Exception as e:
        return f"Error retrieving price data for {ticker}: {str(e)}"

def get_fundamentals(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Handle missing values gracefully
        pe_ratio = info.get('trailingPE', info.get('forwardPE', 'N/A'))
        eps = info.get('trailingEps', 'N/A')
        beta = info.get('beta', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        dividend_yield = info.get('dividendYield', 'N/A')
        
        # Format marketCap in billions if available
        if market_cap not in ('N/A', None):
            market_cap = f"${market_cap / 1000000000:.2f}B"
        
        # Format dividend yield as percentage if available
        if dividend_yield not in ('N/A', None):
            dividend_yield = f"{dividend_yield * 100:.2f}%"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
Stock: {ticker} (Data as of {timestamp})
P/E Ratio: {pe_ratio}
EPS: {eps}
Beta: {beta}
Market Cap: {market_cap}
Dividend Yield: {dividend_yield}
        """
    except Exception as e:
        return f"Error retrieving fundamentals for {ticker}: {str(e)}"

def summarize_article(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise exception for bad status codes
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Try to find article content more intelligently
        article_content = ""
        
        # Look for article content in common containers
        article_tags = soup.find_all(['article', 'main', 'div'], class_=['article', 'content', 'article-content', 'post-content'])
        if article_tags:
            for tag in article_tags:
                paragraphs = tag.find_all('p')
                if paragraphs:
                    article_content += " ".join([p.get_text() for p in paragraphs])
                    break
        
        # If no content found in specific containers, fall back to all paragraphs
        if not article_content:
            paragraphs = soup.find_all("p")
            article_content = " ".join([para.get_text() for para in paragraphs])
        
        if not article_content or len(article_content) < 100:
            return "Could not extract meaningful content from the article."
            
        # Create summarization prompt
        summary_prompt = PromptTemplate.from_template(
            """You are a professional financial analyst.

Summarize the following article into clear, concise bullet points for a business-savvy audience.

- Focus on the key takeaways, announcements, and figures.
- Avoid unnecessary details or filler.
- Use a formal and neutral tone.
- Include URL and timestamp of when this was summarized.

Article from: {url}
Article content:
{text}

Summary:
- Executive Summary: 
- Key Points:
- Potential Impact:"""
        )
        chain = LLMChain(llm=llm, prompt=summary_prompt)
        # Truncate if very long but keep enough content for good summarization
        text_to_summarize = article_content[:5000]
        summary = chain.run({"text": text_to_summarize, "url": url})
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Summarized at: {timestamp}\n\n{summary.strip()}"
    
    except Exception as e:
        return f"Error summarizing article at {url}: {str(e)}"

def get_news_articles(query: str) -> str:
    # Placeholder: actual news search done by TavilySearch
    return f"Use the TavilySearch tool instead to find recent news for: {query}"