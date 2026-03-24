import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the secret key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # We are using 'flash' for high-speed analysis. 
    # To upgrade later, just change 'flash' to 'pro'!
    model = genai.GenerativeModel('gemini-2.5-flash') 
else:
    model = None

def get_financial_summary(ticker, metrics, income_stmt_string):
    """Sends raw financial data to Gemini for an executive summary."""
    if not model:
        return "❌ API Key missing. Please check your .env file."
        
    prompt = f"""
    You are an expert Wall Street financial analyst. 
    Review the following key metrics and income statement data for {ticker}.
    
    Key Metrics:
    {metrics}
    
    Recent Income Statement Data:
    {income_stmt_string}
    
    Provide a professional, concise 3-paragraph executive summary of the company's financial health, highlighting any major revenue trends or red flags. Use bullet points for key takeaways at the end.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error connecting to Gemini API: {e}"