import streamlit as st
from datetime import datetime


def show_footer():
    """Show the dashboard footer"""
    
    st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e9ecef;
            padding: 0.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: #6c757d;
            z-index: 999;
        }
        
        .footer .brand {
            font-weight: 600;
            color: #1A2A4A;
        }
        
        .footer .brand .yellow {
            color: #FEDB00;
        }
        
        @media (max-width: 768px) {
            .footer {
                flex-direction: column;
                padding: 0.5rem 1rem;
                gap: 0.25rem;
                text-align: center;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    now = datetime.now()
    
    st.markdown(f"""
    <div class="footer">
        <div>
            <span class="brand">Expiry<span class="yellow">Dash</span></span>
            <span style="margin: 0 0.5rem;">|</span>
            v2.0.0
        </div>
        <div>
            <span>© {now.year} Expiry Removal Dashboard</span>
            <span style="margin: 0 0.5rem;">|</span>
            <span>Powered by <strong>Noon</strong></span>
            <span style="margin: 0 0.5rem;">|</span>
            <span>Last refresh: {now.strftime('%H:%M:%S')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)