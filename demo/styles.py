"""Custom CSS styles for the Streamlit demo."""

import streamlit as st

# Color palette for PII types
PII_COLORS = {
    "EMAIL": "#FF6B6B",
    "PHONE": "#4ECDC4",
    "IBAN": "#45B7D1",
    "NAME": "#96CEB4",
    "ADDRESS": "#FFEAA7",
    "GERMAN_ID": "#DDA0DD",
    "CREDIT_CARD": "#98D8C8",
    "IP_ADDRESS": "#F7DC6F",
    "DATE_OF_BIRTH": "#FFB347",
    "UNKNOWN": "#C0C0C0",
}

# Icons for PII types
PII_ICONS = {
    "EMAIL": "📧",
    "PHONE": "📱",
    "IBAN": "🏦",
    "NAME": "👤",
    "ADDRESS": "📍",
    "GERMAN_ID": "🪪",
    "CREDIT_CARD": "💳",
    "IP_ADDRESS": "🌐",
    "DATE_OF_BIRTH": "📅",
    "UNKNOWN": "❓",
}


def inject_custom_css():
    """Inject custom CSS for modern styling."""
    st.markdown(
        """
    <style>
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* PII highlight base styles - underline approach */
    .pii-highlight {
        text-decoration: underline;
        text-decoration-thickness: 3px;
        text-underline-offset: 3px;
        cursor: help;
        font-weight: 500;
    }
    .pii-highlight:hover {
        text-decoration-thickness: 4px;
    }

    /* PII type specific underline colors */
    .pii-EMAIL { text-decoration-color: #FF6B6B; }
    .pii-PHONE { text-decoration-color: #4ECDC4; }
    .pii-IBAN { text-decoration-color: #45B7D1; }
    .pii-NAME { text-decoration-color: #96CEB4; }
    .pii-ADDRESS { text-decoration-color: #FFEAA7; }
    .pii-GERMAN_ID { text-decoration-color: #DDA0DD; }
    .pii-CREDIT_CARD { text-decoration-color: #98D8C8; }
    .pii-IP_ADDRESS { text-decoration-color: #F7DC6F; }
    .pii-DATE_OF_BIRTH { text-decoration-color: #FFB347; }
    .pii-UNKNOWN { text-decoration-color: #C0C0C0; }

    /* Confidence badges */
    .confidence-high { color: #4CAF50; font-weight: bold; }
    .confidence-medium { color: #FFC107; font-weight: bold; }
    .confidence-low { color: #F44336; font-weight: bold; }

    /* Strategy cards */
    .strategy-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #30363d;
        margin: 5px 0;
    }

    /* Code blocks */
    .code-block {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Fira Code', monospace;
        overflow-x: auto;
    }

    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
    }

    /* Legend styling - compact underline style */
    .legend-item {
        display: inline-flex;
        align-items: center;
        margin-right: 12px;
        font-size: 0.8rem;
    }
    .legend-color {
        width: 16px;
        height: 3px;
        margin-right: 4px;
        border-radius: 1px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
