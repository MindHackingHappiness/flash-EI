"""
Script to scrape pricing information from provider websites.
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
import sys

# Add the parent directory to the path so we can import the model_info module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def scrape_openai_pricing():
    """
    Scrape OpenAI pricing information.
    
    Returns:
        dict: Dictionary of model pricing information
    """
    url = "https://platform.openai.com/docs/pricing"
    print(f"Scraping OpenAI pricing from {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Note: OpenAI's pricing page uses JavaScript to load content,
        # so a simple requests.get won't work. In a real implementation,
        # you might use Selenium or Playwright to handle JavaScript.
        
        # This is a placeholder for the actual scraping logic
        print("Note: OpenAI's pricing page requires JavaScript. Using hardcoded values.")
        
        # Hardcoded values based on the latest pricing
        return {
            "gpt-4-turbo": {"input": 0.01/1e3, "output": 0.03/1e3},
            "gpt-4": {"input": 0.03/1e3, "output": 0.06/1e3},
            "gpt-4-32k": {"input": 0.06/1e3, "output": 0.12/1e3},
            "gpt-3.5-turbo": {"input": 0.0015/1e3, "output": 0.002/1e3},
            "gpt-3.5-turbo-16k": {"input": 0.003/1e3, "output": 0.004/1e3},
        }
    except Exception as e:
        print(f"Error scraping OpenAI pricing: {e}")
        return {}

def scrape_anthropic_pricing():
    """
    Scrape Anthropic pricing information.
    
    Returns:
        dict: Dictionary of model pricing information
    """
    url = "https://www.anthropic.com/pricing#anthropic-api"
    print(f"Scraping Anthropic pricing from {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This is a placeholder for the actual scraping logic
        # In a real implementation, you would parse the HTML to extract pricing
        print("Note: Using simplified scraping logic for Anthropic. May not capture all details.")
        
        # Example of how you might extract pricing (simplified)
        pricing = {}
        model_sections = soup.find_all('h3')
        
        for section in model_sections:
            model_name = section.text.strip().lower()
            if model_name.startswith('claude-'):
                # Find pricing information in the following elements
                price_elements = section.find_next_siblings('p')
                input_price = None
                output_price = None
                
                for elem in price_elements:
                    text = elem.text.strip()
                    if 'input' in text.lower() and '/' in text:
                        # Extract input price
                        match = re.search(r'(\d+\.?\d*)\s*/\s*MTok', text)
                        if match:
                            input_price = float(match.group(1)) / 1e6  # Convert from per MTok to per token
                    
                    if 'output' in text.lower() and '/' in text:
                        # Extract output price
                        match = re.search(r'(\d+\.?\d*)\s*/\s*MTok', text)
                        if match:
                            output_price = float(match.group(1)) / 1e6  # Convert from per MTok to per token
                
                if input_price and output_price:
                    pricing[model_name] = {"input": input_price, "output": output_price}
        
        # If scraping failed, use hardcoded values
        if not pricing:
            print("Falling back to hardcoded Anthropic pricing")
            pricing = {
                "claude-3.7-sonnet": {"input": 0.003/1e3, "output": 0.015/1e3},
                "claude-3.5-sonnet": {"input": 0.003/1e3, "output": 0.015/1e3},
                "claude-3.5-haiku": {"input": 0.00080/1e3, "output": 0.004/1e3},
                "claude-3-opus": {"input": 0.015/1e3, "output": 0.075/1e3},
                "claude-3-sonnet": {"input": 0.003/1e3, "output": 0.015/1e3},
                "claude-3-haiku": {"input": 0.00025/1e3, "output": 0.00125/1e3},
            }
        
        return pricing
    except Exception as e:
        print(f"Error scraping Anthropic pricing: {e}")
        return {}

def scrape_gemini_pricing():
    """
    Scrape Gemini pricing information.
    
    Returns:
        dict: Dictionary of model pricing information
    """
    url = "https://ai.google.dev/gemini-api/docs/pricing"
    print(f"Scraping Gemini pricing from {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This is a placeholder for the actual scraping logic
        # In a real implementation, you would parse the HTML to extract pricing
        print("Note: Using simplified scraping logic for Gemini. May not capture all details.")
        
        # Example of how you might extract pricing (simplified)
        pricing = {}
        model_sections = soup.find_all(['h2', 'h3'])
        
        for section in model_sections:
            model_name = section.text.strip().lower()
            if 'gemini' in model_name:
                # Find the table with pricing information
                tables = section.find_next('table')
                if tables:
                    rows = tables.find_all('tr')
                    input_price = None
                    output_price = None
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            row_text = cells[0].text.strip().lower()
                            price_text = cells[1].text.strip()
                            
                            if 'input' in row_text:
                                # Extract input price
                                match = re.search(r'\$(\d+\.?\d*)', price_text)
                                if match:
                                    input_price = float(match.group(1)) / 1e6  # Convert from per 1M tokens to per token
                            
                            if 'output' in row_text:
                                # Extract output price
                                match = re.search(r'\$(\d+\.?\d*)', price_text)
                                if match:
                                    output_price = float(match.group(1)) / 1e6  # Convert from per 1M tokens to per token
                    
                    if input_price and output_price:
                        # Clean up model name to match our format
                        clean_name = model_name.replace(' ', '-').lower()
                        pricing[clean_name] = {"input": input_price, "output": output_price}
        
        # If scraping failed, use hardcoded values
        if not pricing:
            print("Falling back to hardcoded Gemini pricing")
            pricing = {
                "gemini-2.0-flash": {"input": 0.00010/1e3, "output": 0.00040/1e3},
                "gemini-2.0-flash-lite": {"input": 0.000075/1e3, "output": 0.00030/1e3},
                "gemini-1.5-flash": {"input": 0.000075/1e3, "output": 0.00030/1e3},
                "gemini-1.5-flash-8b": {"input": 0.0000375/1e3, "output": 0.00015/1e3},
                "gemini-1.5-pro": {"input": 0.00125/1e3, "output": 0.005/1e3},
            }
        
        return pricing
    except Exception as e:
        print(f"Error scraping Gemini pricing: {e}")
        return {}

def update_model_info():
    """
    Update model_info.py with the latest pricing information.
    """
    print("Starting price scraping...")
    openai_pricing = scrape_openai_pricing()
    anthropic_pricing = scrape_anthropic_pricing()
    gemini_pricing = scrape_gemini_pricing()
    
    # Combine and format the pricing information
    combined_pricing = {
        "openai": openai_pricing,
        "anthropic": anthropic_pricing,
        "gemini": gemini_pricing,
        "last_updated": datetime.now().isoformat()
    }
    
    # Create the scripts directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Save to a JSON file for reference
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pricing_data.json")
    with open(json_path, "w") as f:
        json.dump(combined_pricing, f, indent=2)
    
    print(f"Pricing information updated and saved to {json_path}")
    
    # Note: In a real implementation, this would also update model_info.py
    # but that would require more complex code to modify Python source files
    print("To update model_info.py, manually copy the relevant pricing information from pricing_data.json")

if __name__ == "__main__":
    update_model_info()
