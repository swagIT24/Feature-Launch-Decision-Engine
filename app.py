import streamlit as st
import math
from scipy.stats import norm

st.title("AI Feature Launch Decision Engine")

st.header("Experiment Inputs")

control_users = st.number_input("Control Group - Total Users", min_value=1, value=1000)
control_conversions = st.number_input("Control Group - Conversions", min_value=0, value=100)

variant_users = st.number_input("AI Feature Group - Total Users", min_value=1, value=1000)
variant_conversions = st.number_input("AI Feature Group - Conversions", min_value=0, value=120)

if st.button("Calculate Conversion Rates"):
    control_rate = control_conversions / control_users
    variant_rate = variant_conversions / variant_users

    st.write(f"Control Conversion Rate: {control_rate:.4f}")
    st.write(f"AI Feature Conversion Rate: {variant_rate:.4f}")

    # Pooled proportion
    pooled_p = (control_conversions + variant_conversions) / (control_users + variant_users)

    # Standard error
    se = math.sqrt(pooled_p * (1 - pooled_p) * 
                (1/control_users + 1/variant_users))

    # Z-score
    z = (variant_rate - control_rate) / se

    # One-sided p-value (testing if variant > control)
    p_value = 1 - norm.cdf(z)

    st.write(f"Z-score: {z:.4f}")
    st.write(f"P-value: {p_value:.6f}")

    alpha = 0.05

    if p_value < alpha:
        st.success("Statistically Significant: Launch AI Feature 🚀")
    else:
        st.warning("Not Statistically Significant: Collect More Data ⏳")

    
    # Unpooled Standard Error
    se_unpooled = math.sqrt(
        (control_rate * (1 - control_rate)) / control_users +
        (variant_rate * (1 - variant_rate)) / variant_users
    )

    # 95% confidence level
    z_critical = 1.96  # For 95%

    difference = variant_rate - control_rate

    lower_bound = difference - z_critical * se_unpooled
    upper_bound = difference + z_critical * se_unpooled

    st.write(f"95% Confidence Interval for Difference: ({lower_bound:.4f}, {upper_bound:.4f})")