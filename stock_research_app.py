import os
import streamlit as st
from datetime import datetime
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import pdfkit
import tempfile
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import markdown

# load_dotenv()

# Custom Tools you just saved
from custom_tools import get_stock_price, get_fundamentals, summarize_article, get_news_articles

# === LangChain LLM Setup ===
llm = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",  # or llama3 if preferred
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

# === Define Tools ===
tavily_search = TavilySearchResults( max_results=5)

stock_tools = [
    Tool.from_function(
        func=get_stock_price,
        name="StockPriceTool",
        description="Returns stock price, high/low, volume, and 52-week data."
    ),
    Tool.from_function(
        func=get_fundamentals,
        name="StockFundamentalsTool",
        description="Returns stock fundamentals like P/E, EPS, Beta, Dividend, Market Cap."
    ),
    Tool.from_function(
        func=tavily_search.run,
        name="TavilySearch",
        description="Searches the web for historical data, analyst reports, or industry context."
    ),
    Tool.from_function(
        func=summarize_article,
        name="ArticleSummarizer",
        description="Summarizes news articles or research documents."
    )
]

# === Prompts ===

def generate_stock_analysis_prompt(ticker):
    now = datetime.now()
    return f"""
You are a seasoned credit rating analyst with deep expertise in market analysis! 📊
Let's deeply analyze the stock ticker: {ticker} step-by-step.
You have access to the following tools. Use them exactly as named:

- StockPriceTool: to get the current stock price, day high/low, volume, and 52-week data.
- StockFundamentalsTool: to retrieve stock fundamentals like P/E, EPS, Beta, Dividend Yield, Market Cap.
- TavilySearch: to perform web searches for historical data, analyst reports, or industry context.
- ArticleSummarizer: to summarize news articles or documents.

When you want to get information, output an action like:

Action: <ToolName>
Action Input: <input for the tool>

For example:

Action: StockPriceTool
Action Input: {ticker}

Wait for the tool output before proceeding.

If you cannot find precise data, clearly state so and provide qualitative insights.

Produce the entire detailed report in one response without asking for confirmation or pausing.

## Stock Analysis Report
Date: {now.strftime('%Y-%m-%d')}
Time: {now.strftime('%H:%M:%S')}

Perform a structured report on the stock: {ticker}

## Executive Summary
Provide a brief overview of the stock's current status and key findings.
...

## Market Overview
- Use StockPriceTool for current price data.
- Latest stock price, day high/low, volume.
- 52-week high and low.
...

## Financial Deep Dive (Current & Historical Context)
...

## Growth Potential
...

## CAGR: Compound Annual Growth Rate
Explain CAGR and provide figures if found for key metrics.
- **Attempt to calculate or find CAGR for revenue/earnings based on data from your comprehensive search.** Explain CAGR and provide figures if found.
...

## Profitability Analysis
- Discuss Net Profit Margin trends (e.g., last few quarters/years if available).
- Discuss Return on Equity (ROE) trends.
- Discuss PAT (Profit After Tax) trends.
...

## Financial Health
- Comment on Loans and Advances if the company is a financial institution and data is found.
- Comment on Surplus and Reserves if data is found.
- Discuss Debt to Equity Ratio (D/E) trends.
- Discuss Interest Coverage Ratio trends.
- Discuss Current Ratio trends.
...

## Dividend Analysis
- Current Dividend Yield.
- Discuss Dividend Payout Ratio, Dividend Growth Rate if information is found via search.

...

## Market Context
- Industry positioning.
- Competitive landscape.
- Recent market sentiment towards the stock/sector.
- Discuss any recent news or events impacting the stock.
- Use TavilySearch to find relevant news articles.
...

## Risk Disclosure
- Potential risk factors specific to the company or market.
- Market uncertainties.
- Regulatory concerns if applicable.
...

Do not invent numbers. If specific data is not found through tools, state that and provide qualitative analysis or general trends based on search.
Provide a detailed analysis. Use bullet points and tables where appropriate.
"""

def generate_news_prompt(topic):
    now = datetime.now()
    return f"""
You are an elite financial research analyst.
Your expertise includes deep investigative financial research, fact-checking,
trend analysis, simplification of complex topics, and ethical balanced reporting.

Date: {now.strftime('%Y-%m-%d')}
Time: {now.strftime('%H:%M:%S')}

Your task is to research the topic: \"{topic}\"
Follow this workflow:
1. Research Phase:
   - Use TavilySearch to identify 3-5 recent, authoritative sources on the topic \"{topic}\".
   - Prioritize news articles, reputable financial sites, and expert opinions.
   - For promising articles, use ArticleSummarizer to get key details.

2. Analysis Phase:
   - Synthesize the information from the searched sources.
   - Identify key themes, events, or data points.
   - Note any conflicting viewpoints if found.

3. Reporting Phase:
   - Craft an attention-grabbing headline for your research findings.
   - Provide an Executive Summary.
   - Detail Key Findings/Themes with bullet points, citing information source ideas if possible (e.g. \"According to a report from X...\").
   - Briefly discuss Potential Impact or Implications.
   - List the primary URLs of sources you found most useful (if any were summarized).

Format the output in **markdown**. Ensure your report is concise yet informative.
Focus on delivering actionable insights or a clear understanding of the topic.

Please generate the full report in one response without stopping or requesting confirmation.

Topic for Research: {topic}
"""

# === PDF Export ===
# def export_to_pdf(ticker, content):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
#         html_path = tmp.name
#         tmp.write(content.encode("utf-8"))

#     pdf_path = f"{ticker}_report.pdf"
#     pdfkit.from_file(html_path, pdf_path)
#     return pdf_path

def export_to_pdf(title, markdown_content, output_dir="reports"):
    # Convert markdown to HTML
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    html_content = markdown.markdown(markdown_content)

    # Create a full HTML page with basic styling
    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
                line-height: 1.5;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 90%;
            }}
            ul {{
                margin-left: 20px;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    html_path = os.path.join(output_dir, f"{title}_temp.html")
    pdf_path = os.path.join(output_dir, f"{title}_temp.html")

    # Save the intermediate HTML file
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    # Optional: specify path to wkhtmltopdf executable if not in PATH
    # config = None
    # Example for Windows (change as per your installation)
    # import os
    path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    pdfkit.from_file(html_path, pdf_path, configuration=config)

    return pdf_path

# === Streamlit UI ===
st.set_page_config(page_title="📈 Stock Research", layout="wide")
with st.sidebar:
    st.title("🧠 Stock Research Assistant")
    st.markdown("""
    Welcome to AI-powered financial research assistant!

    - Analyze multiple tickers simultaneously
    - Summarize and explore current financial news
    - Export detailed reports as PDFs
    """)
    st.markdown("---")
    st.caption("Developed by Dhairya.")

st.title("📊 Stock Research App")

mode = st.radio("🔍 Select Analysis Type:", ["📈 Stock Report", "📰 News Research"], horizontal=True)

if mode == "📈 Stock Report":
    st.markdown("### 📌 Stock Analysis")
    ticker_input = st.text_input("Enter one or more Stock Tickers (comma-separated, e.g., AAPL, MSFT):")
    if ticker_input:
        tickers = [ticker.strip().upper() for ticker in ticker_input.split(",")]
        chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{text}"))
        reports = {}

        st.markdown("---")
        for ticker in tickers:
            with st.container():
                st.subheader(f"📘 {ticker} Report")
                prompt = generate_stock_analysis_prompt(ticker)
                with st.spinner(f"🧠 Analyzing {ticker}..."):
                    result = chain.run({"text": prompt})
                st.markdown(result, unsafe_allow_html=True)
                reports[ticker] = result

                # Export PDF to reports directory
                pdf_path = export_to_pdf(ticker, result, output_dir="reports")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download PDF",
                        data=f,
                        file_name=f"{ticker}_analysis.pdf",
                        mime="application/pdf"
                    )

elif mode == "📰 News Research":
    st.markdown("### 🗞️ Financial News Research")
    topic = st.text_input("Enter Financial Topic or Event:")
    if topic:
        prompt = generate_news_prompt(topic)
        chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{text}"))
        with st.spinner("🗞️ Researching and summarizing news..."):
            result = chain.run({"text": prompt})
        st.markdown(result, unsafe_allow_html=True)

        # Export News Report PDF to reports directory
        pdf_path = export_to_pdf("news", result, output_dir="reports")
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download News PDF",
                data=f,
                file_name=f"{topic[:20]}_news_analysis.pdf",
                mime="application/pdf"
            )
