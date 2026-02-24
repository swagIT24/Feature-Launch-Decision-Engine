import streamlit as st
import math
from scipy.stats import norm

st.title("Feature Launch Decision Engine")

st.header("Experiment Inputs")

control_users = st.number_input("Control Group - Total Users", min_value=1, value=1000)
control_conversions = st.number_input("Control Group - Conversions", min_value=0, value=100)

variant_users = st.number_input("AI Feature Group - Total Users", min_value=1, value=1000)
variant_conversions = st.number_input("AI Feature Group - Conversions", min_value=0, value=120)

st.subheader("Retention Guardrail")

control_retained = st.number_input("Control Users Retained", min_value=0, value=400)
variant_retained = st.number_input("Variant Users Retained", min_value=0, value=420)

control_retention = control_retained / control_users
variant_retention = variant_retained / variant_users


retention_pooled = (control_retention * control_users + variant_retention * variant_users) / (control_users + variant_users)

retention_se = math.sqrt(
    retention_pooled * (1 - retention_pooled) *
    (1/control_users + 1/variant_users)
)

retention_z = (variant_retention - control_retention) / retention_se
retention_p_value = 2 * (1 - norm.cdf(abs(retention_z)))

st.write(f"Retention Z-score: {retention_z:.4f}")
st.write(f"Retention P-value: {retention_p_value:.6f}")

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

    st.header("Sample Size Calculator")

    baseline_rate = st.number_input("Baseline Conversion Rate (e.g., 0.10)", value=0.10)
    expected_rate = st.number_input("Expected Conversion Rate After AI (e.g., 0.12)", value=0.12)

    alpha = 0.05
    power = 0.8

    z_alpha = 1.645  # one-sided 5%
    z_beta = 0.84    # for 80% power

    p1 = baseline_rate
    p2 = expected_rate

    pooled = (p1 + p2) / 2

    numerator = (z_alpha * math.sqrt(2 * pooled * (1 - pooled)) +
                z_beta * math.sqrt(p1*(1-p1) + p2*(1-p2))) ** 2

    denominator = (p2 - p1) ** 2

    required_n = numerator / denominator

    st.write(f"Required Sample Size Per Group: {int(required_n)} users")

    st.header("Revenue Impact Simulation")

    avg_revenue = st.number_input("Average Revenue Per Conversion ($)", value=50.0)
    total_users_future = st.number_input("Projected Monthly Users", value=100000)

    control_revenue = total_users_future * control_rate * avg_revenue
    ai_revenue = total_users_future * variant_rate * avg_revenue

    incremental_revenue = ai_revenue - control_revenue

    st.write(f"Projected Revenue (Control): ${control_revenue:,.2f}")
    st.write(f"Projected Revenue (AI Feature): ${ai_revenue:,.2f}")
    st.write(f"Incremental Monthly Revenue: ${incremental_revenue:,.2f}")

    st.header("Final Decision Summary")

    conversion_significant = p_value < 0.05
    retention_safe = not (retention_p_value < 0.05 and variant_retention < control_retention)

    if conversion_significant and retention_safe:
        st.success("✅ LAUNCH AI FEATURE")
        st.write("Conversion improves significantly and retention is not harmed.")
    elif not conversion_significant:
        st.warning("⏳ DO NOT LAUNCH - Conversion uplift not statistically significant.")
    elif not retention_safe:
        st.error("🚨 DO NOT LAUNCH - Retention significantly decreased.")