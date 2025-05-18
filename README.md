# 📊 Multi-Agent Stock Research App

A modern, interactive financial research assistant powered by **LangChain** and **Groq**. This app generates AI-based stock analysis and financial news summaries with exportable reports.

## 🚀 Features

- 🔍 Analyze multiple stock tickers in one go
- 📰 Summarize real-time financial news or events
- 📄 Export AI-generated reports as PDF files
- 🧠 Uses Large Language Models (LLMs) to generate structured, insightful outputs
- 🌐 Clean Streamlit UI for seamless interactivity

## 📸 App Demo

![Stock Research Demo](demo/demo.gif)

## 🧰 Tech Stack

- **Frontend/UI**: Streamlit
- **LLM Integration**: LangChain + Groq
- **Data Tools**: Custom Python tools for stock prices, fundamentals, and news
- **PDF Export**: Markdown → HTML → PDF via `pdfkit` and `wkhtmltopdf`
- **Language**: Python 3.10+

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Dhairyakhania/Stock-Research-App.git
   cd stock-research-app

## 🧰 Install dependencies:

```bash
   pip install -r requirements.txt
```

- Install wkhtmltopdf and ensure it's in your system path.

## Set your environment variable:

  ```bash
    export GROQ_API_KEY=your_groq_api_key
  ```

## Run the app:

  ```bash
     streamlit run stock_research_app.py
  ```

## 📂 Directory Structure
  ```bash
    .
    ├── stock_research_app.py        
    ├── custom_tools.py     
    ├── reports/                    
    ├── requirements.txt
    └── README.md
  ```

## 📄 License
This project is licensed under the [License](LICENSE).