import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
import os

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Hyperliquid Quant Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, institutional look
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1, h2, h3 { color: #E0E6ED; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #00CC96; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #00A87A; }
    .metric-card { background-color: #1E2127; padding: 20px; border-radius: 10px; border: 1px solid #333; text-align: center; }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. LOAD THE MACHINE LEARNING MODEL
# ==========================================
@st.cache_resource
def load_model():
    model_path = 'hyperliquid_rf_model.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        return None

model = load_model()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=029", width=50) # Placeholder for crypto vibe
st.sidebar.title("Quant Engine")
st.sidebar.markdown("Explore trader behavior vs. market sentiment on Hyperliquid.")

page = st.sidebar.radio("Navigation", ["🔮 Live ML Predictor", "📊 Model Insights"])

st.sidebar.divider()
st.sidebar.markdown("**Built for Data Analysis Assessment**")
st.sidebar.caption("Powered by Random Forest & Streamlit")


# ==========================================
# 4. MAIN APPLICATION LOGIC
# ==========================================

if page == "🔮 Live ML Predictor":
    st.title("🔮 Predictive Alpha Engine")
    st.markdown("Adjust the behavioral and sentiment parameters below to predict if the trader will be profitable tomorrow.")
    
    if model is None:
        st.error("⚠️ Model file 'hyperliquid_rf_model.pkl' not found! Please make sure it is in the same directory as this app.")
    else:
        # Create input form
        with st.form("prediction_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Trader Risk")
                avg_size = st.number_input("Average Trade Size (USD)", min_value=10, max_value=500000, value=15000, step=1000)
                daily_pnl = st.number_input("Today's PnL (USD)", min_value=-100000.0, max_value=100000.0, value=-500.0, step=100.0)
                
            with col2:
                st.subheader("Trader Behavior")
                num_trades = st.slider("Number of Trades Today", min_value=1, max_value=5000, value=500)
                win_rate = st.slider("Today's Win Rate", min_value=0.0, max_value=1.0, value=0.45, step=0.01)
                
            with col3:
                st.subheader("Market Context")
                ls_ratio = st.slider("Long/Short Ratio ( >1 is Long Bias)", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
                sentiment = st.slider("BTC Fear/Greed Index", min_value=0, max_value=100, value=45, help="0 = Extreme Fear, 100 = Extreme Greed")

            submit = st.form_submit_button("Run Prediction Engine")

        # Process prediction when user clicks submit
        if submit:
            # Must match the exact order: ['avg_size_usd', 'num_trades', 'win_rate', 'long_short_ratio', 'daily_pnl', 'value']
            input_data = pd.DataFrame([[avg_size, num_trades, win_rate, ls_ratio, daily_pnl, sentiment]], 
                                      columns=['avg_size_usd', 'num_trades', 'win_rate', 'long_short_ratio', 'daily_pnl', 'value'])
            
            prediction = model.predict(input_data)[0]
            probabilities = model.predict_proba(input_data)[0]
            profit_prob = probabilities[1] * 100
            
            st.divider()
            
            # Display beautifully formatted results
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                if prediction == 1:
                    st.success("### Prediction: PROFITABLE 📈")
                    st.markdown("The model detects a favorable behavioral setup. Historically, this signature yields positive returns the following day.")
                else:
                    st.error("### Prediction: UNPROFITABLE 📉")
                    st.markdown("The model detects high risk of drawdown. This behavioral signature (often tied to panic or over-leverage) typically precedes a losing day.")
            
            with res_col2:
                # Plotly Gauge Chart for Confidence
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = profit_prob,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Probability of Profit (%)", 'font': {'size': 20, 'color': 'white'}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#00CC96" if profit_prob >= 50 else "#EF553B"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(239, 85, 59, 0.3)'},
                            {'range': [40, 60], 'color': 'rgba(255, 255, 255, 0.1)'},
                            {'range': [60, 100], 'color': 'rgba(0, 204, 150, 0.3)'}],
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Model Insights":
    st.title("📊 Inside the Black Box")
    st.markdown("Understanding *why* the Random Forest model makes its decisions.")
    
    if model is None:
        st.warning("Please upload 'hyperliquid_rf_model.pkl' to view insights.")
    else:
        # Extract feature importances
        features = ['Average Size (USD)', 'Num Trades', 'Win Rate', 'Long/Short Ratio', 'Daily PnL', 'Fear/Greed Sentiment']
        importances = model.feature_importances_
        
        df_importance = pd.DataFrame({'Feature': features, 'Importance': importances})
        df_importance = df_importance.sort_values(by='Importance', ascending=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Feature Importance")
            fig = px.bar(df_importance, x='Importance', y='Feature', orientation='h', 
                         color='Importance', color_continuous_scale='viridis')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                              font_color='white', margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Analyst Notes")
            st.info("""
            **How to read this:**
            The chart on the left shows the internal mathematical weighting of the Random Forest model. 
            
            Features with a higher score have a greater predictive impact on whether a trader will be profitable tomorrow. 
            
            Notice how **Behavioral Features** (like Win Rate and Size) interact with **Macro Features** (Fear/Greed) to form the final prediction.
            """)
