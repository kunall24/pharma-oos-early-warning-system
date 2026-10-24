import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Pharma OOS Early-Warning System", layout="wide")
st.title("Pharma OOS Early-Warning System")

BRIGHT_COLORS = ["#00C49F", "#FF8042", "#0088FE", "#FFBB28", "#FF4560", "#775DD0", "#00E396"]

# ==========================================
# DATA LOADING
# ==========================================
@st.cache_data
def load_assets():
    model = joblib.load("models/pharma_oos_model.pkl")
    features_df = pd.read_csv("data/features/features.csv")
    merged_df = pd.read_csv("data/cleaned/merged_all.csv")
    merged_df['StartTimestamp'] = pd.to_datetime(merged_df['StartTimestamp'])
    return model, features_df, merged_df

pipe, features_df, merged_df = load_assets()

# ==========================================
# TABS LAYOUT
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📈 Business Insights (EDA Portfolio)", 
    "⚙️ Early-Warning Simulator", 
    "🗄️ Raw Data Directory"
])

# ==========================================
# TAB 1: EXPLORATORY DATA ANALYSIS (PORTFOLIO)
# ==========================================
with tab1:
    st.markdown("## Manufacturing Process & Failure Analysis")
    st.markdown("Historical batch data analysis identifying root causes and mechanical drivers of Out-of-Specification (OOS) failures.")
    st.markdown("---")

    # QUESTION 1
    st.markdown("### 1. Product-wise OOS Performance: How does each product perform in terms of OOS rate?")
    oos_rates = merged_df.groupby("Product_ID")["OOS_Flag"].mean().reset_index()
    fig1 = px.bar(oos_rates, x="Product_ID", y="OOS_Flag", color="Product_ID", color_discrete_sequence=BRIGHT_COLORS, text_auto='.1%', labels={"OOS_Flag": "Failure Rate (%)", "Product_ID": "Product Line"})
    fig1.update_layout(yaxis_tickformat='.0%', showlegend=False, height=350, margin=dict(t=30, b=10))
    st.plotly_chart(fig1, use_container_width=True)
    
    with st.expander("View Analysis: Product-wise Performance"):
        st.markdown("**Observed Result:** NeuroCalm_IR shows a 40.7% OOS rate. CardioStat_IR exhibits moderate OOS (19.8%), while GastroEase_CR is stable (3.9%).")
        st.markdown("**Interpretation:** NeuroCalm_IR shows a significantly higher failure rate, indicating that granulation-related parameters are currently the most sensitive and failure-prone.")
        st.markdown("**Business Insight:** Quality improvement efforts should prioritize NeuroCalm_IR granulation controls, followed by CardioStat_IR mixing optimization.")

    st.markdown("<br>", unsafe_allow_html=True)

    # QUESTION 2
    st.markdown("### 2. OOS Trend Over Time (Rolling Average): Is there time-based drift, leakage, or instability?")
    df_time = merged_df.sort_values("StartTimestamp").set_index("StartTimestamp")
    rolling_oos = df_time["OOS_Flag"].rolling("30D").mean().reset_index()
    fig2 = px.line(rolling_oos, x="StartTimestamp", y="OOS_Flag", color_discrete_sequence=["#FF4560"])
    fig2.update_layout(yaxis_title="30-Day Rolling OOS Rate", xaxis_title="Timeline", height=350, margin=dict(t=30, b=10))
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View Analysis: Time Trends"):
        st.markdown("**Observed Result:** The rolling 30-day OOS rate fluctuates within a stable band (15% - 25%).")
        st.markdown("**Interpretation:** There is no sustained upward or downward drift over the 3-year production cycle.")
        st.markdown("**Business Insight:** The process is time-stationary. Predictive models can safely use historical data without time-based correction factors.")

    st.markdown("<br>", unsafe_allow_html=True)

    # QUESTION 3
    st.markdown("### 3. Single-Parameter Level EDA: How does OOS behavior change with individual parameters?")
    q3_col1, q3_col2 = st.columns(2)
    with q3_col1:
        st.plotly_chart(px.box(merged_df, x="OOS_Flag", y="Coating_Spray_Rate", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], height=300).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)
        st.plotly_chart(px.box(merged_df, x="OOS_Flag", y="Mixing_Speed_RPM", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], height=300).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)
    with q3_col2:
        st.plotly_chart(px.box(merged_df, x="OOS_Flag", y="Inlet_Temp_C", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], height=300).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)
        st.plotly_chart(px.box(merged_df, x="OOS_Flag", y="Granulation_Temp_C", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], height=300).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)
    
    q3_col3, q3_col4 = st.columns(2)
    with q3_col3:
        st.plotly_chart(px.box(merged_df, x="OOS_Flag", y="Granulation_Moisture_%", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], height=300).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)

    with st.expander("View Analysis: Single-Parameter Impact"):
        st.markdown("**Observed Result:** OOS batches show shifted distributions and wider spread for critical parameters compared to In-Spec batches.")
        st.markdown("**Interpretation:** Failures are not random; they emerge when critical parameters drift toward risky regions (e.g., Low Mixing Speed, High Granulation Temp).")
        st.markdown("**Business Insight:** Individual parameters act as early warning indicators, but relying on a single metric is insufficient. Multivariate models are required.")

    st.markdown("<br>", unsafe_allow_html=True)

    # QUESTION 4
    st.markdown("### 4. Product-Wise Sensitivity Analysis: Do different products fail for different reasons?")
    q4_col1, q4_col2, q4_col3 = st.columns(3)
    with q4_col1:
        st.plotly_chart(px.box(merged_df[merged_df["Product_ID"] == "CardioStat_IR"], x="OOS_Flag", y="Mixing_Speed_RPM", color="OOS_Flag", title="CardioStat: Mixing Speed", color_discrete_sequence=[BRIGHT_COLORS[2], BRIGHT_COLORS[4]], height=350).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)
    with q4_col2:
        st.plotly_chart(px.box(merged_df[merged_df["Product_ID"] == "NeuroCalm_IR"], x="OOS_Flag", y="Granulation_Temp_C", color="OOS_Flag", title="NeuroCalm: Gran. Temp", color_discrete_sequence=[BRIGHT_COLORS[3], BRIGHT_COLORS[4]], height=350).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)
    with q4_col3:
        st.plotly_chart(px.box(merged_df[merged_df["Product_ID"] == "GastroEase_CR"], x="OOS_Flag", y="Coating_Spray_Rate", color="OOS_Flag", title="GastroEase: Spray Rate", color_discrete_sequence=[BRIGHT_COLORS[5], BRIGHT_COLORS[4]], height=350).update_layout(showlegend=False, margin=dict(t=30, b=10)), use_container_width=True)

    with st.expander("View Analysis: Product Sensitivity"):
        st.markdown("**Observed Result:** CardioStat_IR is highly sensitive to Mixing Speed, NeuroCalm_IR to Granulation Temp, and GastroEase_CR to Coating Spray Rate.")
        st.markdown("**Interpretation:** Each product exhibits distinct failure mechanics based on its unique active pharmaceutical ingredient (API) properties.")
        st.markdown("**Business Insight:** Control limits and monitoring strategies must be product-specific, aligned with the dominant manufacturing step for each drug.")

    st.markdown("<br>", unsafe_allow_html=True)

    # QUESTION 5
    st.markdown("### 5. Interaction Analysis: Do combinations of parameters amplify OOS risk?")
    q5_col1, q5_col2, q5_col3 = st.columns(3)
    with q5_col1:
        fig5a = px.scatter(merged_df, x="Inlet_Temp_C", y="Coating_Time_Min", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], opacity=0.7, title="Inlet Temp vs Coating Time")
        st.plotly_chart(fig5a.update_layout(showlegend=False, height=350, margin=dict(t=30, b=10)), use_container_width=True)
    with q5_col2:
        fig5b = px.scatter(merged_df, x="Granulation_Temp_C", y="Granulation_Moisture_%", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], opacity=0.7, title="Gran. Temp vs Moisture")
        st.plotly_chart(fig5b.update_layout(showlegend=False, height=350, margin=dict(t=30, b=10)), use_container_width=True)
    with q5_col3:
        fig5c = px.scatter(merged_df, x="Mixing_Speed_RPM", y="Blender_load_%", color="OOS_Flag", color_discrete_sequence=[BRIGHT_COLORS[0], BRIGHT_COLORS[4]], opacity=0.7, title="Mixing Speed vs Blender Load")
        st.plotly_chart(fig5c.update_layout(showlegend=False, height=350, margin=dict(t=30, b=10)), use_container_width=True)

    with st.expander("View Analysis: Interactions"):
        st.markdown("**Observed Result:** High OOS concentrations cluster in specific grid quadrants (e.g., high temperature combined with high moisture).")
        st.markdown("**Interpretation:** Combinations of sub-optimal parameters create a compounding risk zone where failure probability spikes dramatically, even if individual parameters are barely out of range.")
        st.markdown("**Business Insight:** Univariate limits are inadequate. Operational teams need multivariate risk flags to catch edge-case combinations.")

    st.markdown("<br>", unsafe_allow_html=True)

    # QUESTION 6
    st.markdown("### 6. Model Feature Importance: What ultimately drives the Machine Learning predictions?")
    try:
        lr_model = pipe.named_steps["lr"]
        X_cols = features_df.drop(columns=["Batch_ID", "StartTimestamp", "Assay", "Dissolution", "Impurity", "Hardness", "OOS_Flag"], errors="ignore").columns
        importance = pd.DataFrame({"Feature": X_cols, "Importance": np.abs(lr_model.coef_[0])}).sort_values(by="Importance", ascending=True).tail(8)
        fig6 = px.bar(importance, x="Importance", y="Feature", orientation='h', color="Importance", color_continuous_scale="Plasma")
        st.plotly_chart(fig6.update_layout(height=350, margin=dict(t=10, b=10)), use_container_width=True)
    except:
        st.warning("Model feature importance could not be extracted directly from the pipeline.")
    
    with st.expander("View Analysis: Feature Importance"):
        st.markdown("**Observed Result:** The manually engineered 'mixing_risk_flag' and 'granulation_risk_flag' hold higher weight than the raw values themselves.")
        st.markdown("**Interpretation:** The algorithm heavily relies on the domain-specific logic injected during the ETL phase rather than raw sensory outputs.")
        st.markdown("**Business Insight:** Deep domain knowledge translates directly to better model performance. Feature engineering adds massive predictive value.")

    st.markdown("<br>", unsafe_allow_html=True)

    # QUESTION 7
    st.markdown("### 7. Parameter Correlation Heatmap: Are process variables interacting naturally?")
    corr_cols = ["Blender_load_%", "Coating_Spray_Rate", "Granulation_Moisture_%", "Granulation_Temp_C", "Inlet_Temp_C", "Mixing_Speed_RPM"]
    corr_matrix = merged_df[corr_cols].corr()
    fig7 = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="Viridis", aspect="auto")
    st.plotly_chart(fig7.update_layout(height=450, margin=dict(t=10, b=10)), use_container_width=True)

    with st.expander("View Analysis: Correlation"):
        st.markdown("**Observed Result:** Correlation coefficients across disparate manufacturing steps are near zero (e.g., Mixing Speed vs. Coating Spray Rate).")
        st.markdown("**Interpretation:** Machine parameters act independently of one another during sequential execution.")
        st.markdown("**Business Insight:** Validates the modeling approach. Because variables are independent, Logistic Regression handles the weights efficiently without multicollinearity issues.")


# ==========================================
# TAB 2: MODEL SIMULATOR
# ==========================================
with tab2:
    st.markdown("### Live Batch Inference Simulator")
    
    features_df["Batch_Display"] = features_df["Batch_ID"] + " (Product: " + merged_df["Product_ID"] + ")"
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        selected_display = st.selectbox("Select a Batch to simulate QC testing:", features_df["Batch_Display"].unique())
    
    selected_batch_id = selected_display.split(" ")[0]
    batch_data = features_df[features_df["Batch_ID"] == selected_batch_id].iloc[0]
    
    meta_columns = ["Batch_ID", "Batch_Display", "StartTimestamp", "Assay", "Dissolution", "Impurity", "Hardness", "OOS_Flag"]
    X_input = pd.DataFrame([batch_data.drop(labels=[col for col in meta_columns if col in batch_data.index])])

    # Prediction
    prob = pipe.predict_proba(X_input)[0][1]
    threshold = 0.6
    prediction = "High Risk (OOS)" if prob >= threshold else "In-Spec (Safe)"
    color = "#FF4560" if prob >= threshold else "#00E396"

    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric(label="Selected Batch ID", value=selected_batch_id)
    mcol2.metric(label="OOS Probability", value=f"{prob * 100:.1f}%")
    mcol3.markdown(f"<h3 style='margin-top: 15px;'>Status: <span style='color:{color}'>{prediction}</span></h3>", unsafe_allow_html=True)
    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "OOS Risk Probability (%)", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, threshold * 100], 'color': "rgba(0, 227, 150, 0.15)"},
                    {'range': [threshold * 100, 100], 'color': "rgba(255, 69, 96, 0.15)"}
                ],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': threshold * 100}
            }
        ))
        fig_gauge.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

    with chart_col2:
        core_params = ["Mixing_Speed_RPM", "Granulation_Temp_C", "Granulation_Moisture_%", "Coating_Spray_Rate"]
        batch_core_values = X_input[core_params].iloc[0].values
        
        fig_bar = px.bar(
            x=core_params, y=batch_core_values,
            labels={'x': "Process Parameter", 'y': "Recorded Value"},
            title="Core Process Parameters",
            color=core_params, color_discrete_sequence=BRIGHT_COLORS,
            text_auto='.2f'
        )
        fig_bar.update_layout(height=400, showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        fig_bar.update_xaxes(fixedrange=True)
        fig_bar.update_yaxes(fixedrange=True)
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# TAB 3: RAW DATA DIRECTORY
# ==========================================
with tab3:
    st.markdown("### 🗄️ Complete Feature Dataset")
    st.markdown("Full unnested view of all processed engineering features fed into the Logistic Regression pipeline.")
    st.dataframe(features_df.drop(columns=["Batch_Display"], errors='ignore'), use_container_width=True, height=700)
