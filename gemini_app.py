"""
Specialized Streamlit UI for Gemini Flash 2.0 with the MHH EI superprompt.
Features enhanced visualization, logging, and metrics tracking.
"""

import streamlit as st
import os
import json
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import re
import logging
from dotenv import load_dotenv
import base64
from io import BytesIO
import uuid # Added for session ID

from ei_harness import EIHarness
from ei_harness.utils.prompt_loader import DEFAULT_PROMPT_URL, load_prompt_from_url
from ei_harness.utils.token_counter import count_tokens
from ei_harness.utils.model_info import MODEL_PRICING, MODEL_CONTEXT_WINDOW

# Constants
GEMINI_MODEL = "gemini-2.0-flash-001"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LOGS_DIR = "logs"
THEME_COLORS = {
    "primary": "#4285F4",    # Google Blue
    "secondary": "#34A853",  # Google Green
    "accent": "#FBBC05",     # Google Yellow
    "error": "#EA4335",      # Google Red
    "background": "#F8F9FA", # Light gray
    "text": "#202124",       # Dark gray
    "light_text": "#5F6368", # Medium gray
}

# Create logs directory if it doesn't exist
Path(LOGS_DIR).mkdir(exist_ok=True)

# Configure logging
log_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"gemini_app_{log_timestamp}.log"
log_filepath = Path(LOGS_DIR) / log_filename

# Set up file handler for logging
file_handler = logging.FileHandler(log_filepath, mode='w')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Configure logger
logger = logging.getLogger('gemini_app')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Load environment variables from .env file if it exists
load_dotenv()

# Helper functions
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    return img_str

def apply_custom_css():
    """Apply custom CSS styling to the app."""
    # Define a slightly refined color palette
    primary_color = "#1a73e8" # Slightly deeper Google Blue
    secondary_color = "#34a853" # Google Green
    accent_color = "#fbbc05" # Google Yellow
    error_color = "#d93025" # Slightly deeper Google Red
    background_color = "#f8f9fa"
    text_color = "#202124"
    light_text_color = "#5f6368"
    border_color = "#dadce0"
    card_bg_color = "#ffffff"
    user_msg_bg = "#e8f0fe"

    st.markdown(f"""
    <style>
    /* Main theme colors */
    :root {{
        --primary: {primary_color};
        --secondary: {secondary_color};
        --accent: {accent_color};
        --error: {error_color};
        --background: {background_color};
        --text: {text_color};
        --light-text: {light_text_color};
        --border-color: {border_color};
        --card-bg: {card_bg_color};
        --user-msg-bg: {user_msg_bg};
    }}

    /* General body styling */
    body {{
        background-color: var(--background);
        color: var(--text);
    }}

    /* Header styling */
    .main-header {{
        color: var(--primary);
        font-size: 2.2rem; /* Slightly smaller */
        font-weight: 600; /* Slightly less bold */
        margin-bottom: 0.2rem; /* Reduced margin */
        padding-bottom: 0;
    }}

    .sub-header {{
        color: var(--light-text);
        font-size: 1.1rem; /* Slightly smaller */
        font-weight: 400;
        margin-top: 0;
        padding-top: 0;
        margin-bottom: 1.5rem; /* Reduced margin */
    }}

    /* Card styling (used for metrics) */
    .card {{
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 15px; /* Adjusted padding */
        border: 1px solid var(--border-color); /* Added subtle border */
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); /* Softer shadow */
        margin-bottom: 15px; /* Adjusted margin */
        height: 100%; /* Ensure cards in columns have same height */
    }}

    .card-title {{
        color: var(--primary);
        font-size: 1rem; /* Adjusted size */
        font-weight: 500; /* Medium weight */
        margin-bottom: 8px; /* Adjusted margin */
        text-transform: uppercase; /* Uppercase for distinction */
        letter-spacing: 0.5px;
    }}

    /* Metric styling (within cards) */
    /* Using st.metric directly is often cleaner, but if using custom cards: */
    .metric-value {{
        font-size: 1.6rem; /* Adjusted size */
        font-weight: 600;
        color: var(--primary);
        line-height: 1.2; /* Adjust line height */
        margin-bottom: 4px;
    }}

    /* Chat styling */
    .stChatMessage {{ /* Target Streamlit's chat message component */
        border-radius: 8px;
        border: 1px solid transparent; /* Base border */
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
    }}

    .stChatMessage[data-testid="stChatMessage"] {{ /* User message */
        background-color: var(--user-msg-bg);
        border-color: #d0e1fd;
    }}

    .stChatMessage:has(div[data-testid="stChatMessageContent--assistant"]) {{ /* Assistant message */
        background-color: var(--card-bg);
        border-color: var(--border-color);
        border-left: 3px solid var(--primary);
    }}

    /* Style the message content and timestamp area */
     div[data-testid="stChatMessageContent"] {{
         color: var(--text);
     }}
     div[data-testid="stChatMessageContent"] p {{ /* Ensure paragraphs inside have normal margin */
         margin-bottom: 0.5em;
     }}
     div[data-testid="stChatMessageContent"] > div:last-child {{ /* Timestamp/metadata area */
        font-size: 0.75rem;
        color: var(--light-text);
        margin-top: 0.5rem;
     }}

    /* Style the embedded metrics within assistant messages */
    .stChatMessage .metrics-container {{
        background-color: rgba(0,0,0,0.03); /* Slightly different background */
        padding: 5px 10px;
        border-radius: 4px;
        margin-top: 8px !important; /* Ensure spacing */
        font-size: 0.7rem; /* Smaller font for metrics */
    }}
     .stChatMessage .metrics-container div {{
         margin-right: 10px !important; /* Spacing between metrics */
         color: var(--light-text);
     }}
     .stChatMessage .metrics-container strong {{
         color: var(--text);
         font-weight: 500;
     }}

    /* Button styling */
    /* Target Streamlit's default button */
    .stButton > button {{
        border-radius: 6px;
        border: 1px solid var(--primary);
        background-color: var(--primary);
        color: white;
        padding: 0.4rem 0.8rem;
        transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
    }}
    .stButton > button:hover {{
        background-color: #185abc; /* Darker blue on hover */
        border-color: #185abc;
    }}
    .stButton > button:focus {{
        outline: none;
        box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.4); /* Focus ring */
    }}
    /* Secondary button style (e.g., Reset) */
    .stButton > button:not(:first-child) {{ /* Example: target non-primary buttons */
         background-color: var(--card-bg);
         color: var(--primary);
         border: 1px solid var(--border-color);
    }}
     .stButton > button:not(:first-child):hover {{
         background-color: #f1f3f4; /* Light gray hover */
         border-color: #c6c8ca;
         color: #185abc;
     }}


    /* Input styling */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        border-radius: 6px;
        border: 1px solid var(--border-color);
        background-color: var(--card-bg);
        color: var(--text);
    }}
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary);
        box-shadow: 0 0 0 1px var(--primary);
    }}
    /* Chat input specific */
    div[data-testid="stChatInput"] {{
        background-color: #e8eaed; /* Slightly different background */
        border-top: 1px solid var(--border-color);
        padding: 0.5rem 1rem;
    }}
     div[data-testid="stChatInput"] input {{
         border-radius: 18px; /* Rounded chat input */
         border: 1px solid #bdc1c6;
     }}

    /* Footer styling */
    .footer {{
        text-align: center;
        color: var(--light-text);
        font-size: 0.8rem;
        margin-top: 3rem; /* Increased margin */
        padding-top: 1.5rem; /* Increased padding */
        border-top: 1px solid var(--border-color);
    }}
     .footer a {{
         color: var(--primary);
         text-decoration: none;
     }}
     .footer a:hover {{
         text-decoration: underline;
     }}

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 5px; /* Increased gap */
        border-bottom: 1px solid var(--border-color); /* Add bottom border */
    }}

    .stTabs [data-baseweb="tab"] {{
        height: auto; /* Auto height */
        white-space: normal; /* Allow wrapping */
        background-color: transparent; /* Transparent background */
        border-radius: 6px 6px 0 0; /* Slightly more rounded */
        border: 1px solid transparent; /* Transparent border */
        border-bottom: none; /* No bottom border */
        padding: 0.6rem 1rem; /* Adjusted padding */
        margin-bottom: -1px; /* Overlap border */
        color: var(--light-text);
        transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out, color 0.2s ease-in-out;
    }}
     .stTabs [data-baseweb="tab"]:hover {{
         background-color: #e8f0fe; /* Light blue hover */
         color: var(--primary);
     }}

    .stTabs [aria-selected="true"] {{
        background-color: var(--card-bg);
        border-color: var(--border-color) var(--border-color) var(--card-bg) var(--border-color); /* Border trick */
        color: var(--primary);
        font-weight: 500;
    }}

    /* Sidebar styling */
    div[data-testid="stSidebarUserContent"] {{
        padding: 1rem; /* Add padding to sidebar */
    }}
     div[data-testid="stSidebarUserContent"] h2 {{
         font-size: 1.3rem;
         color: var(--primary);
         margin-bottom: 0.5rem;
     }}
     div[data-testid="stSidebarUserContent"] h3 {{
         font-size: 1rem;
         color: var(--text);
         text-transform: uppercase;
         letter-spacing: 0.5px;
         margin-top: 1.5rem;
         margin-bottom: 0.5rem;
         border-bottom: 1px solid var(--border-color);
         padding-bottom: 0.3rem;
     }}
     div[data-testid="stSidebarUserContent"] .stMetric {{
         background-color: var(--card-bg);
         border-radius: 6px;
         padding: 10px;
         border: 1px solid var(--border-color);
         margin-bottom: 0.5rem;
     }}
      div[data-testid="stSidebarUserContent"] .stMetric label {{ /* Metric label */
          font-size: 0.8rem;
          color: var(--light-text);
      }}
      div[data-testid="stSidebarUserContent"] .stMetric div[data-testid="stMetricValue"] {{ /* Metric value */
          font-size: 1.2rem;
          font-weight: 600;
          color: var(--primary);
      }}

    </style>
    """, unsafe_allow_html=True)

def create_metrics_plots(metrics_data):
    """Create visualizations for metrics data."""
    plots = {}
    
    if not metrics_data or not metrics_data.get('iterations'):
        return plots
    
    # Extract data for plotting
    iterations = len(metrics_data['iterations'])
    data = {
        'iteration': list(range(1, iterations + 1)),
        'prompt_tokens': [],
        'completion_tokens': [],
        'total_tokens': [],
        'response_time': [],
        'input_cost': [],
        'output_cost': [],
        'total_cost': []
    }
    
    for i, iteration in enumerate(metrics_data['iterations']):
        # Token usage
        if 'token_usage' in iteration:
            data['prompt_tokens'].append(iteration['token_usage'].get('prompt_tokens', 0))
            data['completion_tokens'].append(iteration['token_usage'].get('completion_tokens', 0))
            data['total_tokens'].append(iteration['token_usage'].get('total_tokens', 0))
        else:
            data['prompt_tokens'].append(0)
            data['completion_tokens'].append(0)
            data['total_tokens'].append(0)
        
        # Response time
        data['response_time'].append(iteration.get('response_time', 0))
        
        # Cost
        if 'cost' in iteration:
            data['input_cost'].append(iteration['cost'].get('input_cost', 0))
            data['output_cost'].append(iteration['cost'].get('output_cost', 0))
            data['total_cost'].append(iteration['cost'].get('total_cost', 0))
        else:
            data['input_cost'].append(0)
            data['output_cost'].append(0)
            data['total_cost'].append(0)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Token usage plot
    fig_tokens = px.bar(
        df, 
        x='iteration', 
        y=['prompt_tokens', 'completion_tokens'],
        title='Token Usage by Interaction',
        labels={'value': 'Tokens', 'iteration': 'Interaction', 'variable': 'Token Type'},
        color_discrete_map={'prompt_tokens': THEME_COLORS['primary'], 'completion_tokens': THEME_COLORS['secondary']}
    )
    fig_tokens.update_layout(
        legend_title_text='',
        xaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    plots['tokens'] = fig_tokens
    
    # Cost plot
    fig_cost = px.bar(
        df, 
        x='iteration', 
        y=['input_cost', 'output_cost'],
        title='Cost by Interaction',
        labels={'value': 'Cost ($)', 'iteration': 'Interaction', 'variable': 'Cost Type'},
        color_discrete_map={'input_cost': THEME_COLORS['primary'], 'output_cost': THEME_COLORS['secondary']}
    )
    fig_cost.update_layout(
        legend_title_text='',
        xaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    plots['cost'] = fig_cost
    
    # Response time plot
    fig_time = px.line(
        df, 
        x='iteration', 
        y='response_time',
        title='Response Time by Interaction',
        labels={'response_time': 'Time (seconds)', 'iteration': 'Interaction'},
        markers=True
    )
    fig_time.update_traces(line_color=THEME_COLORS['primary'])
    fig_time.update_layout(
        xaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    plots['time'] = fig_time
    
    # Cumulative tokens plot
    df['cumulative_tokens'] = df['total_tokens'].cumsum()
    fig_cumulative = px.line(
        df, 
        x='iteration', 
        y='cumulative_tokens',
        title='Cumulative Token Usage',
        labels={'cumulative_tokens': 'Total Tokens', 'iteration': 'Interaction'},
        markers=True
    )
    fig_cumulative.update_traces(line_color=THEME_COLORS['accent'])
    fig_cumulative.update_layout(
        xaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    plots['cumulative'] = fig_cumulative
    
    # Cumulative cost plot
    df['cumulative_cost'] = df['total_cost'].cumsum()
    fig_cumulative_cost = px.line(
        df, 
        x='iteration', 
        y='cumulative_cost',
        title='Cumulative Cost',
        labels={'cumulative_cost': 'Total Cost ($)', 'iteration': 'Interaction'},
        markers=True
    )
    fig_cumulative_cost.update_traces(line_color=THEME_COLORS['error'])
    fig_cumulative_cost.update_layout(
        xaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    plots['cumulative_cost'] = fig_cumulative_cost
    
    return plots

def calculate_summary_metrics(metrics_data):
    """Calculate summary metrics from the metrics data."""
    summary = {
        'total_interactions': 0,
        'total_tokens': 0,
        'avg_tokens_per_interaction': 0,
        'total_cost': 0,
        'avg_cost_per_interaction': 0,
        'avg_response_time': 0
    }
    
    if not metrics_data or not metrics_data.get('iterations'):
        return summary
    
    iterations = metrics_data['iterations']
    summary['total_interactions'] = len(iterations)
    
    total_tokens = 0
    total_cost = 0
    total_response_time = 0
    
    for iteration in iterations:
        # Token usage
        if 'token_usage' in iteration:
            total_tokens += iteration['token_usage'].get('total_tokens', 0)
        
        # Cost
        if 'cost' in iteration:
            total_cost += iteration['cost'].get('total_cost', 0)
        
        # Response time
        if 'response_time' in iteration:
            total_response_time += iteration['response_time']
    
    summary['total_tokens'] = total_tokens
    summary['total_cost'] = total_cost
    
    if summary['total_interactions'] > 0:
        summary['avg_tokens_per_interaction'] = total_tokens / summary['total_interactions']
        summary['avg_cost_per_interaction'] = total_cost / summary['total_interactions']
        summary['avg_response_time'] = total_response_time / summary['total_interactions']
    
    return summary

def extract_metrics_from_message(message):
    """Extract metrics from a message in the chat history."""
    metrics = {}
    
    if 'metadata' in message:
        return message['metadata']
    
    return metrics

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if isinstance(timestamp, str):
        try:
            dt = datetime.datetime.fromisoformat(timestamp)
            return dt.strftime("%I:%M:%S %p")
        except:
            return timestamp
    elif isinstance(timestamp, datetime.datetime):
        return timestamp.strftime("%I:%M:%S %p")
    else:
        return str(timestamp) # Indent this line

# Initialize session state
if "chat_history" not in st.session_state: # Renamed for clarity, stores Gemini API format
    st.session_state.chat_history = []
if "display_messages" not in st.session_state: # For displaying in UI, includes timestamps etc.
    st.session_state.display_messages = []
if "harness" not in st.session_state:
    st.session_state.harness = None
if "superprompt_loaded" not in st.session_state:
    st.session_state.superprompt_loaded = False
if "superprompt_text" not in st.session_state:
    st.session_state.superprompt_text = ""
if "edited_superprompt" not in st.session_state:
    st.session_state.edited_superprompt = ""
if "superprompt_token_count" not in st.session_state:
    st.session_state.superprompt_token_count = 0
if "metrics_data" not in st.session_state:
    st.session_state.metrics_data = {'iterations': []}
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.datetime.now().isoformat()
if "total_session_tokens" not in st.session_state:
    st.session_state.total_session_tokens = 0
if "total_session_cost" not in st.session_state:
    st.session_state.total_session_cost = 0

MAX_HISTORY_TURNS = 10 # Keep last 10 turns (5 user, 5 assistant) for API context

# Set page config
st.set_page_config(
    page_title="Gemini Flash 2.0 with EI Superprompt",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Main layout
st.markdown('<h1 class="main-header">Gemini Flash 2.0</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Powered by MHH EI Superprompt</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Header instead of logo
    st.markdown("## Zenodelic AI")
    st.markdown("### Session Information")
    
    # Session metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tokens", f"{st.session_state.total_session_tokens:,}")
    with col2:
        st.metric("Total Cost", f"${st.session_state.total_session_cost:.6f}")
    
    # Session duration
    if "session_start_time" in st.session_state:
        start_time = datetime.datetime.fromisoformat(st.session_state.session_start_time)
        current_time = datetime.datetime.now()
        duration = current_time - start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        st.markdown(f"**Session Duration:** {hours:02}:{minutes:02}:{seconds:02}")
    
    st.markdown("---")
    
    # Superprompt information
    st.markdown("### Superprompt Information")
    
    if st.session_state.superprompt_token_count > 0:
        st.markdown(f"**Token Count:** {st.session_state.superprompt_token_count:,}")
        
        # Context window usage
        context_window = MODEL_CONTEXT_WINDOW.get(GEMINI_MODEL, 1000000)
        usage_percentage = (st.session_state.superprompt_token_count / context_window) * 100
        
        # Progress bar for context window usage
        st.markdown(f"**Context Window Usage:** {usage_percentage:.1f}%")
        st.progress(usage_percentage / 100)
        
        if usage_percentage > 90:
            st.warning(f"⚠️ Superprompt is using over 90% of the context window!")
        elif usage_percentage > 70:
            st.info(f"ℹ️ Superprompt is using over 70% of the context window.")
    
    st.markdown("---")
    
    # Export options
    st.markdown("### Export Options")
    
    export_format = st.selectbox(
        "Export Format",
        ["JSON", "CSV", "Markdown"],
        index=0
    )
    
    if st.button("Export Chat History"):
        if export_format == "JSON":
            # Export as JSON
            export_data = {
                "session_info": {
                    "start_time": st.session_state.session_start_time,
                    "export_time": datetime.datetime.now().isoformat(),
                    "total_tokens": st.session_state.total_session_tokens,
                    "total_cost": st.session_state.total_session_cost
                },
                "messages": st.session_state.display_messages, # Use display_messages
                "metrics": st.session_state.metrics_data
            }

            export_str = json.dumps(export_data, indent=2)
            b64 = base64.b64encode(export_str.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="gemini_chat_export_{log_timestamp}.json">Download JSON</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        elif export_format == "CSV":
            # Export as CSV
            data = []
            for msg in st.session_state.display_messages: # Use display_messages
                row = {
                    "timestamp": msg.get("timestamp", ""),
                    "role": msg.get("role", ""),
                    "content": msg.get("content", "")
                }
                
                # Add metrics if available
                if "metadata" in msg:
                    metrics = msg["metadata"]
                    if "token_usage" in metrics:
                        row["prompt_tokens"] = metrics["token_usage"].get("prompt_tokens", 0)
                        row["completion_tokens"] = metrics["token_usage"].get("completion_tokens", 0)
                        row["total_tokens"] = metrics["token_usage"].get("total_tokens", 0)
                    
                    if "cost" in metrics:
                        row["input_cost"] = metrics["cost"].get("input_cost", 0)
                        row["output_cost"] = metrics["cost"].get("output_cost", 0)
                        row["total_cost"] = metrics["cost"].get("total_cost", 0)
                    
                    if "response_time" in metrics:
                        row["response_time"] = metrics["response_time"]
                
                data.append(row)
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:text/csv;base64,{b64}" download="gemini_chat_export_{log_timestamp}.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        elif export_format == "Markdown":
            # Export as Markdown
            md_content = f"# Gemini Flash 2.0 Chat Export\n\n"
            md_content += f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            md_content += f"**Total Tokens:** {st.session_state.total_session_tokens:,}\n"
            md_content += f"**Total Cost:** ${st.session_state.total_session_cost:.6f}\n\n"
            md_content += "## Chat History\n\n"

            for msg in st.session_state.display_messages: # Use display_messages
                role = msg.get("role", "")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                
                md_content += f"### {role.capitalize()} ({format_timestamp(timestamp)})\n\n"
                md_content += f"{content}\n\n"
                
                # Add metrics if available
                if "metadata" in msg:
                    metrics = msg["metadata"]
                    md_content += "**Metrics:**\n\n"
                    
                    if "token_usage" in metrics:
                        md_content += f"- Tokens: {metrics['token_usage'].get('total_tokens', 0):,}\n"
                    
                    if "cost" in metrics:
                        md_content += f"- Cost: ${metrics['cost'].get('total_cost', 0):.6f}\n"
                    
                    if "response_time" in metrics:
                        md_content += f"- Response Time: {metrics['response_time']:.2f} seconds\n"
                    
                    md_content += "\n"
            
            b64 = base64.b64encode(md_content.encode()).decode()
            href = f'<a href="data:text/markdown;base64,{b64}" download="gemini_chat_export_{log_timestamp}.md">Download Markdown</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    if st.button("Export Metrics"):
        # Export metrics as JSON
        export_data = {
            "session_info": {
                "start_time": st.session_state.session_start_time,
                "export_time": datetime.datetime.now().isoformat(),
                "total_tokens": st.session_state.total_session_tokens,
                "total_cost": st.session_state.total_session_cost
            },
            "metrics": st.session_state.metrics_data
        }
        
        export_str = json.dumps(export_data, indent=2)
        b64 = base64.b64encode(export_str.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="gemini_metrics_{log_timestamp}.json">Download Metrics</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    st.markdown("---")

    # Clear History Button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.display_messages = []
        st.session_state.metrics_data = {'iterations': []} # Also clear metrics for this session
        st.rerun()

    st.markdown("---")

    # Add cache savings display
    if st.session_state.harness and hasattr(st.session_state.harness.model, "cache_stats"):
        stats = st.session_state.harness.model.cache_stats

        st.markdown("### Cache Savings")
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Tokens Saved",
                f"{stats.get('tokens_saved', 0):,}",
                help="Number of input tokens saved by caching"
            )

        with col2:
            st.metric(
                "Cost Saved",
                f"${stats.get('cost_saved', 0):.4f}",
                help="Estimated cost savings from caching input tokens"
            )

        # Hit rate
        total = stats.get("hits", 0) + stats.get("misses", 0)
        hit_rate = stats.get("hits", 0) / total if total > 0 else 0
        st.metric("Cache Hit Rate", f"{hit_rate:.1%}")
        st.markdown("---")


    # About section
    with st.expander("About", expanded=False):
        st.markdown("""
        This application uses the Gemini Flash 2.0 model with the MHH EI superprompt to provide enhanced emotional intelligence capabilities.
        
        **Features:**
        - Real-time metrics tracking
        - Chat history with timestamps
        - Export options for data analysis
        - Superprompt editing capabilities
        
        **Model Information:**
        - Model: Gemini Flash 2.0
        - Context Window: 1,000,000 tokens
        - Pricing: $0.000125 per 1K input tokens, $0.000375 per 1K output tokens
        
        **Credits:**
        - MHH EI Superprompt: [GitHub Repository](https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms)
        """)

# Create tabs for Chat, Metrics, and Superprompt Editor
chat_tab, metrics_tab, prompt_tab = st.tabs(["💬 Chat", "📊 Metrics", "✏️ Superprompt Editor"])

# Chat tab
with chat_tab:
    # Chat container
    chat_container = st.container()
    
    # Display chat history (using display_messages)
    with chat_container:
        for i, message in enumerate(st.session_state.display_messages): # Use display_messages
            role = message.get("role", "")
            content = message.get("content", "")
            timestamp = message.get("timestamp", datetime.datetime.now().isoformat())

            # Extract metrics for assistant messages
            metrics_html = ""
            if role == "assistant" and "metadata" in message:
                metrics = message["metadata"]
                
                # Create a metrics div with proper styling to prevent breaking
                metrics_html = "<div class='metrics-container' style='margin-top: 5px; display: flex; flex-wrap: wrap;'>"
                
                if "token_usage" in metrics:
                    total_tokens = metrics["token_usage"].get("total_tokens", 0)
                    metrics_html += f"<div style='margin-right: 15px;'><strong>Tokens:</strong> {total_tokens:,}</div>"
                
                if "cost" in metrics:
                    total_cost = metrics["cost"].get("total_cost", 0)
                    metrics_html += f"<div style='margin-right: 15px;'><strong>Cost:</strong> ${total_cost:.6f}</div>"
                
                if "response_time" in metrics:
                    response_time = metrics["response_time"]
                    metrics_html += f"<div><strong>Time:</strong> {response_time:.2f}s</div>"
                
                metrics_html += "</div>"
            
            # Display message using Streamlit's chat elements
            with st.chat_message(role):
                st.markdown(content) # Display the main content

                # Display metrics and timestamp below assistant messages if metadata exists
                if role == "assistant" and "metadata" in message:
                    metrics = message["metadata"]
                    metrics_parts = []
                    if "token_usage" in metrics:
                        total_tokens = metrics["token_usage"].get("total_tokens", 0)
                        metrics_parts.append(f"Tokens: {total_tokens:,}")
                    if "cost" in metrics:
                        total_cost = metrics["cost"].get("total_cost", 0)
                        metrics_parts.append(f"Cost: ${total_cost:.6f}")
                    if "response_time" in metrics:
                        response_time = metrics["response_time"]
                        metrics_parts.append(f"Time: {response_time:.2f}s")
                    
                    if metrics_parts:
                         st.caption(" | ".join(metrics_parts)) # Display metrics in a caption

                # Always display timestamp for all messages
                st.caption(f"{format_timestamp(timestamp)}")

    # User input
    user_input = st.chat_input("Your message:")
    
    if user_input:
        # Add user message to display history
        timestamp = datetime.datetime.now().isoformat()
        st.session_state.display_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        # Add user message to API history
        st.session_state.chat_history.append({"role": "user", "parts": [user_input]})

        # Log user message
        logger.info(f"User: {user_input}")
        
        # Initialize EI harness if not already initialized
        if st.session_state.harness is None:
            # Check if API key is available
            if not GEMINI_API_KEY:
                st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
                st.stop()
            
            # Use edited superprompt if available
            custom_prompt = None
            if st.session_state.edited_superprompt:
                custom_prompt = st.session_state.edited_superprompt
            
            # Initialize harness
            st.session_state.harness = EIHarness(
                model_provider="gemini",
                api_key=GEMINI_API_KEY,
                model_name=GEMINI_MODEL,
                prompt_url=DEFAULT_PROMPT_URL,
                custom_prompt_text=custom_prompt,
                enable_cache=True,
                verbose=False  # Don't print to console in Streamlit
            )
            st.session_state.superprompt_loaded = False
        
        # Generate response
        with st.spinner("Generating response..."):
            try:
                start_time = time.time()
                
                # Load superprompt if not already loaded
                if not st.session_state.superprompt_loaded:
                    st.session_state.superprompt_text = st.session_state.harness.load_prompt()
                    st.session_state.superprompt_loaded = True
                    st.session_state.superprompt_token_count = st.session_state.harness.superprompt_tokens
                    
                    if not st.session_state.edited_superprompt:
                        st.session_state.edited_superprompt = st.session_state.superprompt_text

                # Prepare history for API call - Limit to last MAX_HISTORY_TURNS
                # Also need to adapt EIHarness/GeminiModel to handle history + system prompt
                # For now, just pass the limited history assuming backend handles it
                history_for_api = st.session_state.chat_history[-MAX_HISTORY_TURNS:]
                superprompt_text = st.session_state.edited_superprompt or st.session_state.superprompt_text

                # EIHarness.generate now handles passing the superprompt as system_instruction
                response = st.session_state.harness.generate(
                    prompt=history_for_api # Pass history list
                )

                # Calculate response time
                end_time = time.time()
                response_time = end_time - start_time
                
                # Get usage information
                usage_info = st.session_state.harness.get_usage_info()

                # Add metadata to usage info
                usage_info["response_time"] = response_time
                usage_info["timestamp"] = datetime.datetime.now().isoformat()

                # Add assistant message to display history
                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "metadata": usage_info
                })
                # Add assistant message to API history
                st.session_state.chat_history.append({"role": "model", "parts": [response]})

                # Log assistant response and metrics
                logger.info(f"Assistant: {response}")
                logger.info(f"Metrics: {json.dumps(usage_info)}")
                
                # Add to metrics data
                iteration_data = {
                    "prompt": user_input,
                    "response": response,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "response_time": response_time
                }
                
                # Add token usage if available
                if "usage" in usage_info:
                    iteration_data["token_usage"] = usage_info["usage"]
                
                # Add cost if available
                if "cost" in usage_info:
                    iteration_data["cost"] = usage_info["cost"]
                
                # Add to metrics data
                st.session_state.metrics_data["iterations"].append(iteration_data)
                
                # Update session totals
                if "usage" in usage_info:
                    st.session_state.total_session_tokens += usage_info["usage"]["total_tokens"]
                
                if "cost" in usage_info:
                    st.session_state.total_session_cost += usage_info["cost"]["total_cost"]
                
                # Force a rerun to immediately display the assistant's message
                st.rerun()
                
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                logger.error(error_msg)
                
                # Add error message to display history
                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": f"I'm sorry, but I encountered an error: {str(e)}",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "error": True
                })
                # Don't add error to API history

                # Force a rerun to immediately display the error message
                st.rerun()

# Metrics tab
with metrics_tab:
    st.markdown("## Metrics Dashboard")
    
    # Summary metrics
    summary = calculate_summary_metrics(st.session_state.metrics_data)
    
    # Display summary metrics in cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Total Interactions</div>
            <div class="metric-value">{:,}</div>
        </div>
        """.format(summary["total_interactions"]), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Total Tokens</div>
            <div class="metric-value">{:,}</div>
        </div>
        """.format(summary["total_tokens"]), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">Total Cost</div>
            <div class="metric-value">${:.6f}</div>
        </div>
        """.format(summary["total_cost"]), unsafe_allow_html=True)
    
    # Second row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Avg. Tokens per Interaction</div>
            <div class="metric-value">{:.1f}</div>
        </div>
        """.format(summary["avg_tokens_per_interaction"]), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Avg. Cost per Interaction</div>
            <div class="metric-value">${:.6f}</div>
        </div>
        """.format(summary["avg_cost_per_interaction"]), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">Avg. Response Time</div>
            <div class="metric-value">{:.2f}s</div>
        </div>
        """.format(summary["avg_response_time"]), unsafe_allow_html=True)
    
    # Create visualizations
    if st.session_state.metrics_data["iterations"]:
        st.markdown("## Visualizations")
        
        plots = create_metrics_plots(st.session_state.metrics_data)
        
        # Display plots in tabs
        plot_tabs = st.tabs(["Token Usage", "Cost", "Response Time", "Cumulative"])
        
        with plot_tabs[0]:
            if "tokens" in plots:
                st.plotly_chart(plots["tokens"], use_container_width=True)
        
        with plot_tabs[1]:
            if "cost" in plots:
                st.plotly_chart(plots["cost"], use_container_width=True)
        
        with plot_tabs[2]:
            if "time" in plots:
                st.plotly_chart(plots["time"], use_container_width=True)
        
        with plot_tabs[3]:
            col1, col2 = st.columns(2)
            
            with col1:
                if "cumulative" in plots:
                    st.plotly_chart(plots["cumulative"], use_container_width=True)
            
            with col2:
                if "cumulative_cost" in plots:
                    st.plotly_chart(plots["cumulative_cost"], use_container_width=True)
        
        # Raw data
        with st.expander("Raw Metrics Data", expanded=False):
            # Convert iterations to DataFrame
            iterations = st.session_state.metrics_data["iterations"]
            
            # Extract relevant data
            data = []
            for i, iteration in enumerate(iterations):
                row = {
                    "Interaction": i + 1,
                    "Timestamp": format_timestamp(iteration.get("timestamp", "")),
                    "Prompt": iteration.get("prompt", ""),
                    "Response Time (s)": iteration.get("response_time", 0)
                }
                
                # Add token usage if available
                if "token_usage" in iteration:
                    row["Prompt Tokens"] = iteration["token_usage"].get("prompt_tokens", 0)
                    row["Completion Tokens"] = iteration["token_usage"].get("completion_tokens", 0)
                    row["Total Tokens"] = iteration["token_usage"].get("total_tokens", 0)
                
                # Add cost if available
                if "cost" in iteration:
                    row["Input Cost ($)"] = iteration["cost"].get("input_cost", 0)
                    row["Output Cost ($)"] = iteration["cost"].get("output_cost", 0)
                    row["Total Cost ($)"] = iteration["cost"].get("total_cost", 0)
                
                data.append(row)
            
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
    else:
        st.info("No metrics data available yet. Start a conversation to generate metrics.")

# Superprompt editor tab
with prompt_tab:
    st.markdown("## Superprompt Editor")
    
    # Function to load superprompt from URL
    def load_superprompt():
        try:
            if not st.session_state.superprompt_text:
                st.session_state.superprompt_text = load_prompt_from_url(DEFAULT_PROMPT_URL)
            
            if not st.session_state.edited_superprompt:
                st.session_state.edited_superprompt = st.session_state.superprompt_text
            
            # Count tokens
            st.session_state.superprompt_token_count = count_tokens(st.session_state.superprompt_text, GEMINI_MODEL)
            return True
        except Exception as e:
            st.error(f"Error loading superprompt: {str(e)}")
            return False
    
    # Function to split prompt into sections
    def split_prompt_into_sections(prompt_text):
        sections = {}
        
        # Try to find the main sections
        lines = prompt_text.split('\n')
        
        # Initialize section boundaries
        copyright_end = 9   # Default
        title_end = 15      # Default
        foreword_end = 47   # Default
        instructions_start = 50  # Default
        
        # Find the exact "Instructions to the LLM:" line
        for i, line in enumerate(lines):
            if "Instructions to the LLM:" in line:
                instructions_start = i
                # Look for the separator line before instructions
                for j in range(i-1, i-5, -1):
                    if j >= 0 and "—" in lines[j]:
                        foreword_end = j - 1
                        break
                break
        
        # Find copyright section end (look for blank line after copyright)
        for i in range(5, 15):
            if i < len(lines) and lines[i].strip() == "":
                copyright_end = i
                break
        
        # Find title section end (look for "Foreword" or blank line)
        for i in range(copyright_end + 1, copyright_end + 10):
            if i < len(lines) and (lines[i].strip() == "Foreword" or lines[i].strip() == ""):
                title_end = i
                break
        
        # Create sections with better boundaries
        sections["copyright"] = "\n".join(lines[:copyright_end])
        sections["title"] = "\n".join(lines[copyright_end:title_end])
        sections["foreword"] = "\n".join(lines[title_end:foreword_end])
        sections["instructions"] = "\n".join(lines[instructions_start:])
        
        return sections
    
    # Load superprompt button
    if st.button("Load Superprompt"):
        with st.spinner("Loading superprompt..."):
            success = load_superprompt()
            if success:
                # Update prompt sections
                st.session_state.prompt_sections = split_prompt_into_sections(st.session_state.superprompt_text)
                st.success(f"Superprompt loaded successfully! ({st.session_state.superprompt_token_count:,} tokens)")
    
    # If superprompt is not loaded yet, try to load it
    if not st.session_state.superprompt_text:
        with st.spinner("Loading superprompt..."):
            if load_superprompt():
                # Update prompt sections
                st.session_state.prompt_sections = split_prompt_into_sections(st.session_state.superprompt_text)
    
    # Display token count
    if st.session_state.superprompt_token_count > 0:
        st.info(f"Current superprompt size: {st.session_state.superprompt_token_count:,} tokens")
        
        # Context window warning
        context_window = MODEL_CONTEXT_WINDOW.get(GEMINI_MODEL, 1000000)
        usage_percentage = (st.session_state.superprompt_token_count / context_window) * 100
        
        if usage_percentage > 90:
            st.warning(f"⚠️ Superprompt is using over 90% of the context window!")
        elif usage_percentage > 70:
            st.warning(f"⚠️ Superprompt is using over 70% of the context window.")
    
    # Add tabs for different editing modes
    edit_tab, sections_tab = st.tabs(["Full Editor", "Section Editor"])
    
    with edit_tab:
        # Text editor for the superprompt
        st.text_area(
            "Edit Superprompt",
            value=st.session_state.edited_superprompt,
            height=500,
            key="superprompt_editor",
            help="Edit the superprompt directly. Changes will be applied when you click 'Apply Changes'."
        )
        
        # Update edited superprompt when text area changes
        st.session_state.edited_superprompt = st.session_state.superprompt_editor
    
    with sections_tab:
        st.markdown("### Prompt Sections")
        
        # Initialize sections in session state if not present
        if "prompt_sections" not in st.session_state and st.session_state.superprompt_text:
            st.session_state.prompt_sections = split_prompt_into_sections(st.session_state.superprompt_text)
        
        # Display sections as expandable areas
        if "prompt_sections" in st.session_state:
            sections = st.session_state.prompt_sections
            
            with st.expander("Copyright and License", expanded=False):
                sections["copyright"] = st.text_area(
                    "Edit Copyright Section",
                    value=sections["copyright"],
                    height=150
                )
            
            with st.expander("Title and Author", expanded=False):
                sections["title"] = st.text_area(
                    "Edit Title Section",
                    value=sections["title"],
                    height=150
                )
            
            with st.expander("Foreword", expanded=False):
                sections["foreword"] = st.text_area(
                    "Edit Foreword Section",
                    value=sections["foreword"],
                    height=300
                )
            
            with st.expander("Instructions to the LLM (Main Content)", expanded=True):
                sections["instructions"] = st.text_area(
                    "Edit Instructions Section",
                    value=sections["instructions"],
                    height=400
                )
            
            # Button to apply section changes
            if st.button("Apply Section Changes", type="primary"):
                # Combine sections back into full prompt
                combined_prompt = f"{sections['copyright']}\n\n{sections['title']}\n\n{sections['foreword']}\n\n{sections['instructions']}"
                
                # Update edited superprompt
                st.session_state.edited_superprompt = combined_prompt
                st.session_state.superprompt_editor = combined_prompt
                
                # Count tokens
                token_count = count_tokens(combined_prompt, GEMINI_MODEL)
                st.session_state.superprompt_token_count = token_count
                    
                st.success(f"Section changes applied! New token count: {token_count:,}")
                
                # Reset the harness to use the new superprompt
                st.session_state.harness = None
                st.session_state.superprompt_loaded = False
    
    # Buttons for applying changes or resetting
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Changes", type="primary"):
            # Count tokens in edited superprompt
            token_count = count_tokens(st.session_state.edited_superprompt, GEMINI_MODEL)
            st.session_state.superprompt_token_count = token_count
            st.success(f"Changes applied! New token count: {token_count:,}")
            
            # Reset the harness to use the new superprompt
            st.session_state.harness = None
            st.session_state.superprompt_loaded = False
    
    with col2:
        if st.button("Reset to Original"):
            st.session_state.edited_superprompt = st.session_state.superprompt_text
            st.session_state.superprompt_editor = st.session_state.superprompt_text
            st.info("Reset to original superprompt.")
            
            # Reset the harness to use the original superprompt
            st.session_state.harness = None
            st.session_state.superprompt_loaded = False

# Footer
st.markdown("""
<div class="footer">
    <p>Gemini Flash 2.0 with MHH EI Superprompt | Created with ❤️ using Streamlit</p>
    <p><a href="https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms">MHH EI for AI</a></p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh for session duration
# Create a placeholder for the auto-refresh mechanism
refresh_placeholder = st.empty()

# Add an auto-refresh mechanism that updates every 5 seconds
# This is done by creating an invisible component that triggers a rerun
refresh_placeholder.markdown(
    f"""
    <div id="refresh" style="display: none;">
        {datetime.datetime.now().isoformat()}
    </div>
    <script>
        setInterval(function() {{
            document.getElementById('refresh').innerHTML = new Date().toISOString();
            setTimeout(function() {{ window.location.reload() }}, 5000);
        }}, 60000);
    </script>
    """,
    unsafe_allow_html=True
)
