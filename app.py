import streamlit as st
import plotly.graph_objects as go
import math

st.set_page_config(
    page_title="Financial Planner & Investment Calculator",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.4rem; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Tax Data ──────────────────────────────────────────────────────────────────
# 2024 Federal brackets (Single). MFJ doubles thresholds; MFS same as Single; HoH uses own brackets.
FED_BRACKETS_SINGLE = [
    (0, 11_600, 10), (11_600, 47_150, 12), (47_150, 100_525, 22),
    (100_525, 191_950, 24), (191_950, 243_725, 32), (243_725, 609_350, 35),
    (609_350, math.inf, 37),
]
FED_BRACKETS_MFJ = [(lo * 2 if lo > 0 else 0, hi * 2, r) for lo, hi, r in FED_BRACKETS_SINGLE]
FED_BRACKETS_HOH = [
    (0, 16_550, 10), (16_550, 63_100, 12), (63_100, 100_500, 22),
    (100_500, 191_950, 24), (191_950, 243_700, 32), (243_700, 609_350, 35),
    (609_350, math.inf, 37),
]

STANDARD_DEDUCTIONS = {
    "Single": 14_600,
    "Married Filing Jointly": 29_200,
    "Married Filing Separately": 14_600,
    "Head of Household": 21_900,
}

SS_WAGE_BASE_2024 = 168_600  # Social Security wage cap

# State tax data: flat rate OR progressive brackets (2024 approximate)
# Format: {"type": "flat", "rate": X}  OR  {"type": "brackets", "brackets": [(lo, hi, rate), ...]}
STATE_TAX = {
    "Alabama":              {"type": "brackets", "brackets": [(0,500,2),(500,3000,4),(3000,math.inf,5)]},
    "Alaska":               {"type": "flat", "rate": 0},
    "Arizona":              {"type": "flat", "rate": 2.5},
    "Arkansas":             {"type": "brackets", "brackets": [(0,4300,2),(4300,8500,4),(8500,math.inf,4.4)]},
    "California":           {"type": "brackets", "brackets": [(0,10099,1),(10099,23942,2),(23942,37788,4),(37788,52455,6),(52455,66295,8),(66295,338639,9.3),(338639,406364,10.3),(406364,677275,11.3),(677275,math.inf,13.3)]},
    "Colorado":             {"type": "flat", "rate": 4.4},
    "Connecticut":          {"type": "brackets", "brackets": [(0,10000,3),(10000,50000,5),(50000,100000,5.5),(100000,200000,6),(200000,250000,6.5),(250000,500000,6.9),(500000,math.inf,6.99)]},
    "Delaware":             {"type": "brackets", "brackets": [(0,2000,0),(2000,5000,2.2),(5000,10000,3.9),(10000,20000,4.8),(20000,25000,5.2),(25000,60000,5.55),(60000,math.inf,6.6)]},
    "Florida":              {"type": "flat", "rate": 0},
    "Georgia":              {"type": "flat", "rate": 5.49},
    "Hawaii":               {"type": "brackets", "brackets": [(0,2400,1.4),(2400,4800,3.2),(4800,9600,5.5),(9600,14400,6.4),(14400,19200,6.8),(19200,24000,7.2),(24000,36000,7.6),(36000,48000,7.9),(48000,math.inf,11)]},
    "Idaho":                {"type": "flat", "rate": 5.8},
    "Illinois":             {"type": "flat", "rate": 4.95},
    "Indiana":              {"type": "flat", "rate": 3.05},
    "Iowa":                 {"type": "brackets", "brackets": [(0,6210,4.4),(6210,31050,4.82),(31050,math.inf,5.7)]},
    "Kansas":               {"type": "brackets", "brackets": [(0,15000,3.1),(15000,30000,5.25),(30000,math.inf,5.7)]},
    "Kentucky":             {"type": "flat", "rate": 4.0},
    "Louisiana":            {"type": "brackets", "brackets": [(0,12500,1.85),(12500,50000,3.5),(50000,math.inf,4.25)]},
    "Maine":                {"type": "brackets", "brackets": [(0,24500,5.8),(24500,58050,6.75),(58050,math.inf,7.15)]},
    "Maryland":             {"type": "brackets", "brackets": [(0,1000,2),(1000,2000,3),(2000,3000,4),(3000,100000,4.75),(100000,125000,5),(125000,150000,5.25),(150000,250000,5.5),(250000,math.inf,5.75)]},
    "Massachusetts":        {"type": "flat", "rate": 5.0},
    "Michigan":             {"type": "flat", "rate": 4.25},
    "Minnesota":            {"type": "brackets", "brackets": [(0,30070,5.35),(30070,98760,6.8),(98760,183340,7.85),(183340,math.inf,9.85)]},
    "Mississippi":          {"type": "flat", "rate": 5.0},
    "Missouri":             {"type": "brackets", "brackets": [(0,1121,1.5),(1121,2242,2),(2242,3363,2.5),(3363,4484,3),(4484,5605,3.5),(5605,6726,4),(6726,7847,4.5),(7847,8968,5),(8968,math.inf,4.7)]},
    "Montana":              {"type": "brackets", "brackets": [(0,20500,4.7),(20500,math.inf,6.75)]},
    "Nebraska":             {"type": "brackets", "brackets": [(0,3700,2.46),(3700,22170,3.51),(22170,35730,5.01),(35730,math.inf,6.64)]},
    "Nevada":               {"type": "flat", "rate": 0},
    "New Hampshire":        {"type": "flat", "rate": 0},
    "New Jersey":           {"type": "brackets", "brackets": [(0,20000,1.4),(20000,35000,1.75),(35000,40000,3.5),(40000,75000,5.525),(75000,500000,6.37),(500000,1000000,8.97),(1000000,math.inf,10.75)]},
    "New Mexico":           {"type": "brackets", "brackets": [(0,5500,1.7),(5500,11000,3.2),(11000,16000,4.7),(16000,210000,4.9),(210000,math.inf,5.9)]},
    "New York":             {"type": "brackets", "brackets": [(0,8500,4),(8500,11700,4.5),(11700,13900,5.25),(13900,21400,5.85),(21400,80650,6.25),(80650,215400,6.85),(215400,1077550,9.65),(1077550,5000000,10.3),(5000000,math.inf,10.9)]},
    "North Carolina":       {"type": "flat", "rate": 4.5},
    "North Dakota":         {"type": "brackets", "brackets": [(0,44725,1.1),(44725,225975,2.04),(225975,math.inf,2.27)]},
    "Ohio":                 {"type": "brackets", "brackets": [(0,26050,0),(26050,46100,2.765),(46100,92150,3.226),(92150,math.inf,3.688)]},
    "Oklahoma":             {"type": "brackets", "brackets": [(0,1000,0.25),(1000,2500,0.75),(2500,3750,1.75),(3750,4900,2.75),(4900,7200,3.75),(7200,math.inf,4.75)]},
    "Oregon":               {"type": "brackets", "brackets": [(0,4050,4.75),(4050,10200,6.75),(10200,125000,8.75),(125000,math.inf,9.9)]},
    "Pennsylvania":         {"type": "flat", "rate": 3.07},
    "Rhode Island":         {"type": "brackets", "brackets": [(0,73450,3.75),(73450,166950,4.75),(166950,math.inf,5.99)]},
    "South Carolina":       {"type": "brackets", "brackets": [(0,3200,0),(3200,16040,3),(16040,math.inf,6.5)]},
    "South Dakota":         {"type": "flat", "rate": 0},
    "Tennessee":            {"type": "flat", "rate": 0},
    "Texas":                {"type": "flat", "rate": 0},
    "Utah":                 {"type": "flat", "rate": 4.65},
    "Vermont":              {"type": "brackets", "brackets": [(0,45400,3.35),(45400,110050,6.6),(110050,229550,7.6),(229550,math.inf,8.75)]},
    "Virginia":             {"type": "brackets", "brackets": [(0,3000,2),(3000,5000,3),(5000,17000,5),(17000,math.inf,5.75)]},
    "Washington":           {"type": "flat", "rate": 0},
    "Washington D.C.":      {"type": "brackets", "brackets": [(0,10000,4),(10000,40000,6),(40000,60000,6.5),(60000,250000,8.5),(250000,500000,9.25),(500000,1000000,9.75),(1000000,math.inf,10.75)]},
    "West Virginia":        {"type": "brackets", "brackets": [(0,10000,2.36),(10000,25000,3.15),(25000,40000,3.54),(40000,60000,4.72),(60000,math.inf,5.12)]},
    "Wisconsin":            {"type": "brackets", "brackets": [(0,13810,3.5),(13810,27630,4.4),(27630,304170,5.3),(304170,math.inf,7.65)]},
    "Wyoming":              {"type": "flat", "rate": 0},
}

def calc_bracket_tax(income, brackets):
    tax = 0.0
    for lo, hi, rate in brackets:
        if income > lo:
            tax += (min(income, hi) - lo) * rate / 100
    return tax

def calc_federal_effective_rate(taxable_income, filing_status):
    if taxable_income <= 0:
        return 0.0
    if filing_status == "Married Filing Jointly":
        brackets = FED_BRACKETS_MFJ
    elif filing_status == "Head of Household":
        brackets = FED_BRACKETS_HOH
    else:
        brackets = FED_BRACKETS_SINGLE
    tax = calc_bracket_tax(taxable_income, brackets)
    return (tax / taxable_income) * 100

def calc_state_effective_rate(income, state):
    if income <= 0 or state not in STATE_TAX:
        return 0.0
    data = STATE_TAX[state]
    if data["type"] == "flat":
        return data["rate"]
    tax = calc_bracket_tax(income, data["brackets"])
    return (tax / income) * 100

# ── Session state defaults ─────────────────────────────────────────────────────
_defaults = {
    "fed_rate": 0.0, "state_rate": 0.0,
    "ss_rate": 6.2,  "med_rate": 1.45,
    "sdi_rate": 0.0, "other_rate": 0.0,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Financial Planner & Investment Calculator")
st.caption("Track income, expenses, taxes, and grow your wealth")

tab_income, tab_expenses, tab_taxes, tab_investment, tab_dashboard = st.tabs(
    ["💰 Income", "💸 Expenses", "🏛️ Taxes", "📈 Investment", "📊 Dashboard"]
)

# ── Income ────────────────────────────────────────────────────────────────────
with tab_income:
    st.subheader("Monthly Income Sources")
    st.caption("Enter all monthly income (gross, before taxes)")

    col1, col2 = st.columns(2)
    with col1:
        monthly_salary = st.number_input("Monthly Salary / Wages ($)",   min_value=0.0, step=100.0, format="%.2f")
        freelance      = st.number_input("Freelance / Side Income ($)",   min_value=0.0, step=50.0,  format="%.2f")
        rental         = st.number_input("Rental Income ($)",             min_value=0.0, step=50.0,  format="%.2f")
    with col2:
        dividends      = st.number_input("Dividends & Interest ($)",      min_value=0.0, step=10.0,  format="%.2f")
        other_income   = st.number_input("Other Income ($)",              min_value=0.0, step=50.0,  format="%.2f")

    total_income = monthly_salary + freelance + rental + dividends + other_income
    st.success(f"**Total Monthly Gross Income: ${total_income:,.2f}**")

    with st.expander("💡 Tips"):
        st.markdown("""
- Enter **gross (pre-tax)** income — taxes are handled in the Taxes tab.
- For variable income use your **average** monthly amount.
- You can also enter your **annual salary** in the Taxes tab to auto-calculate all rates.
        """)

# ── Expenses ──────────────────────────────────────────────────────────────────
with tab_expenses:
    st.subheader("Monthly Expenses")

    st.markdown("#### 🏠 Essential")
    c1, c2, c3 = st.columns(3)
    with c1:
        housing        = st.number_input("Housing (Rent/Mortgage) ($)",            min_value=0.0, step=50.0, format="%.2f")
        utilities      = st.number_input("Utilities ($)",                           min_value=0.0, step=10.0, format="%.2f")
    with c2:
        groceries      = st.number_input("Groceries & Food ($)",                   min_value=0.0, step=10.0, format="%.2f")
        transportation = st.number_input("Transportation ($)",                      min_value=0.0, step=10.0, format="%.2f")
    with c3:
        insurance      = st.number_input("Insurance (Auto, Home, Life) ($)",       min_value=0.0, step=10.0, format="%.2f")
        healthcare     = st.number_input("Healthcare & Medical ($)",               min_value=0.0, step=10.0, format="%.2f")

    essential_total = housing + utilities + groceries + transportation + insurance + healthcare
    st.info(f"Essential Subtotal: **${essential_total:,.2f}**")

    st.markdown("#### 🎬 Lifestyle")
    c1, c2 = st.columns(2)
    with c1:
        subscriptions  = st.number_input("Subscriptions & Memberships ($)",  min_value=0.0, step=5.0,  format="%.2f")
        dining         = st.number_input("Dining Out & Takeout ($)",          min_value=0.0, step=10.0, format="%.2f")
    with c2:
        entertainment  = st.number_input("Entertainment & Hobbies ($)",       min_value=0.0, step=10.0, format="%.2f")
        clothing       = st.number_input("Clothing & Accessories ($)",        min_value=0.0, step=10.0, format="%.2f")

    lifestyle_total = subscriptions + dining + entertainment + clothing
    st.info(f"Lifestyle Subtotal: **${lifestyle_total:,.2f}**")

    st.markdown("#### 👶 Family & Personal")
    c1, c2, c3 = st.columns(3)
    with c1:
        education      = st.number_input("Education & Student Loans ($)",  min_value=0.0, step=10.0, format="%.2f")
        personal_care  = st.number_input("Personal Care & Grooming ($)",   min_value=0.0, step=5.0,  format="%.2f")
    with c2:
        childcare      = st.number_input("Childcare ($)",                   min_value=0.0, step=10.0, format="%.2f")
        pet_care       = st.number_input("Pet Care ($)",                    min_value=0.0, step=5.0,  format="%.2f")
    with c3:
        other_expenses = st.number_input("Other Expenses ($)",              min_value=0.0, step=10.0, format="%.2f")

    family_total = education + personal_care + childcare + pet_care + other_expenses
    st.info(f"Family & Personal Subtotal: **${family_total:,.2f}**")

    total_expenses = essential_total + lifestyle_total + family_total
    st.error(f"**Total Monthly Expenses: ${total_expenses:,.2f}**")

# ── Taxes ─────────────────────────────────────────────────────────────────────
with tab_taxes:
    st.subheader("Taxes & Withholdings")

    # ── Auto-Calculate Section ────────────────────────────────────────────────
    st.markdown("### 🧮 Auto-Calculate from Annual Income")
    st.caption("Enter your annual income and state to auto-fill all tax rates below")

    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        annual_income_input = st.number_input(
            "Annual Gross Income ($)",
            min_value=0.0,
            value=float(round(total_income * 12, 2)),
            step=1000.0,
            format="%.2f",
            help="Defaults to monthly income × 12 from the Income tab. Override freely.",
        )
    with ac2:
        filing_status = st.selectbox(
            "Filing Status",
            ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"],
        )
    with ac3:
        state_selected = st.selectbox(
            "State of Residence",
            sorted(STATE_TAX.keys()),
            index=sorted(STATE_TAX.keys()).index("Texas"),
        )

    # Calculate suggested rates from the annual income input
    std_ded = STANDARD_DEDUCTIONS[filing_status]
    taxable = max(0.0, annual_income_input - std_ded)

    sugg_federal = calc_federal_effective_rate(taxable, filing_status)
    sugg_state   = calc_state_effective_rate(annual_income_input, state_selected)
    sugg_ss      = (min(annual_income_input, SS_WAGE_BASE_2024) / annual_income_input * 6.2) if annual_income_input > 0 else 6.2
    sugg_med     = 1.45
    # Additional 0.9% Medicare surtax over $200K (single) / $250K (MFJ)
    med_threshold = 250_000 if filing_status == "Married Filing Jointly" else 200_000
    if annual_income_input > med_threshold:
        sugg_med += (annual_income_input - med_threshold) / annual_income_input * 0.9

    # Breakdown display
    if annual_income_input > 0:
        b1, b2, b3, b4, b5 = st.columns(5)
        b1.metric("Federal Effective Rate",  f"{sugg_federal:.2f}%", f"on ${taxable:,.0f} taxable")
        b2.metric("State Rate",              f"{sugg_state:.2f}%",   state_selected)
        b3.metric("Social Security",         f"{sugg_ss:.2f}%",      f"cap ${SS_WAGE_BASE_2024:,}")
        b4.metric("Medicare",                f"{sugg_med:.3f}%",     "+0.9% surtax >$200K")
        b5.metric("Standard Deduction",      f"${std_ded:,}",        filing_status)

        # Federal bracket visualizer
        with st.expander("📊 Federal Tax Bracket Breakdown"):
            brackets = FED_BRACKETS_MFJ if filing_status == "Married Filing Jointly" else (FED_BRACKETS_HOH if filing_status == "Head of Household" else FED_BRACKETS_SINGLE)
            b_cols = st.columns(len(brackets))
            for i, (lo, hi, rate) in enumerate(brackets):
                active = taxable > lo
                hi_str = "+" if hi == math.inf else f"–${hi/1000:.0f}K"
                b_cols[i].markdown(
                    f"{'🟦' if active else '⬜'} **{rate}%**  \n${lo/1000:.0f}K {hi_str}"
                )

        # Apply button
        if st.button("⬇️ Apply Auto-Calculated Rates to fields below", type="primary", use_container_width=True):
            st.session_state["fed_rate"]   = round(sugg_federal, 2)
            st.session_state["state_rate"] = round(sugg_state, 2)
            st.session_state["ss_rate"]    = round(sugg_ss, 3)
            st.session_state["med_rate"]   = round(sugg_med, 3)
            st.toast("✅ Tax rates applied!", icon="✅")

    st.divider()

    # ── Manual / Editable Rate Fields ────────────────────────────────────────
    st.markdown("### ✏️ Tax Rate Fields (editable)")
    st.caption("These are pre-filled by the calculator above. You can adjust any value manually.")

    c1, c2, c3 = st.columns(3)
    with c1:
        federal_rate     = st.number_input("Federal Income Tax Rate (%)",   min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="fed_rate")
        state_rate       = st.number_input("State Income Tax Rate (%)",     min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="state_rate")
    with c2:
        social_security  = st.number_input("Social Security / OASDI (%)",  min_value=0.0, max_value=100.0, step=0.01, format="%.3f", key="ss_rate")
        medicare         = st.number_input("Medicare / FICA (%)",           min_value=0.0, max_value=100.0, step=0.01, format="%.3f", key="med_rate")
    with c3:
        state_disability = st.number_input("State Disability Ins. (%)",    min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="sdi_rate")
        other_withholding= st.number_input("Other Withholdings (%)",        min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="other_rate",
                                           help="401k pre-tax, HSA, etc.")

    total_tax_rate = federal_rate + state_rate + social_security + medicare + state_disability + other_withholding
    monthly_taxes  = total_income * (total_tax_rate / 100)
    net_monthly    = total_income - monthly_taxes

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Withholding Rate",  f"{total_tax_rate:.2f}%")
    col2.metric("Annual Tax Estimate",     f"${monthly_taxes * 12:,.0f}")
    col3.metric("Monthly Taxes",           f"-${monthly_taxes:,.2f}")
    col4.metric("Net Monthly Take-Home",   f"${net_monthly:,.2f}")

    if annual_income_input > 0:
        st.caption(
            f"Estimated annual tax burden: **${monthly_taxes*12:,.0f}** "
            f"({total_tax_rate:.1f}% effective rate) on **${annual_income_input:,.0f}** gross income."
        )

# ── Investment ────────────────────────────────────────────────────────────────
with tab_investment:
    st.subheader("Investment Settings")
    st.caption("Configure how much of your net income to invest and your expected returns")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        invest_pct = st.number_input(
            f"Investment % of Net Income\n(Net: ${net_monthly:,.0f}/mo)",
            min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f"
        )
    with c2:
        arr = st.number_input(
            "Annual Rate of Return — ARR (%)\n(S&P 500 avg ~10%, Bonds ~4–5%)",
            min_value=0.0, max_value=50.0, value=7.0, step=0.1, format="%.1f"
        )
    with c3:
        years = st.number_input("Investment Duration (years)", min_value=1, max_value=60, value=30, step=1)
    with c4:
        freq_label = st.selectbox("Compounding Frequency", ["Daily", "Weekly", "Monthly", "Quarterly", "Annually"])

    freq_map         = {"Daily": 365, "Weekly": 52, "Monthly": 12, "Quarterly": 4, "Annually": 1}
    periods_per_year = freq_map[freq_label]
    monthly_investment  = net_monthly * (invest_pct / 100)
    total_contributions = monthly_investment * 12 * years
    r   = (arr / 100) / periods_per_year
    n   = years * periods_per_year
    pmt = monthly_investment * (periods_per_year / 12)

    future_value = pmt * ((math.pow(1 + r, n) - 1) / r) if (arr > 0 and monthly_investment > 0) else total_contributions
    total_gains  = future_value - total_contributions

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Investment",     f"${monthly_investment:,.0f}",    f"{invest_pct}% of net income")
    col2.metric("Total Contributions",    f"${total_contributions:,.0f}",   f"Over {years} years")
    col3.metric("Investment Gains",       f"${total_gains:,.0f}",           "Compound interest earned")
    col4.metric("Future Portfolio Value", f"${future_value:,.0f}",          f"In {years} yrs at {arr}% ARR")

    if monthly_investment > 0:
        chart_years, portfolio_vals, contrib_vals = list(range(years + 1)), [], []
        for y in chart_years:
            n_y  = y * periods_per_year
            fv_y = pmt * ((math.pow(1 + r, n_y) - 1) / r) if arr > 0 else monthly_investment * 12 * y
            portfolio_vals.append(round(fv_y))
            contrib_vals.append(round(monthly_investment * 12 * y))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=chart_years, y=portfolio_vals, name="Portfolio Value",
                                 fill="tozeroy", line=dict(color="#60a5fa", width=2.5)))
        fig.add_trace(go.Scatter(x=chart_years, y=contrib_vals, name="Total Contributed",
                                 fill="tozeroy", line=dict(color="#34d399", width=2)))
        fig.update_layout(
            title="📊 Portfolio Growth Over Time", xaxis_title="Year", yaxis_title="Value ($)",
            template="plotly_dark", height=380,
            yaxis=dict(tickprefix="$", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🎯 Milestones")
        milestones = [100_000, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000]
        m_cols = st.columns(len(milestones))
        for i, m in enumerate(milestones):
            if r > 0 and pmt > 0:
                yrs_to = math.log(1 + (m * r) / pmt) / math.log(1 + r) / periods_per_year
            elif pmt > 0:
                yrs_to = m / (pmt * periods_per_year)
            else:
                yrs_to = None
            label  = f"${m/1e6:.1f}M" if m >= 1e6 else f"${m//1000}K"
            status = (f"✅ {yrs_to:.1f} yrs" if yrs_to <= years else f"~{yrs_to:.1f} yrs") if yrs_to else "—"
            m_cols[i].metric(label, status)

# ── Dashboard ─────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.subheader("Financial Dashboard")

    monthly_surplus = net_monthly - total_expenses
    savings_rate    = (monthly_surplus / net_monthly * 100) if net_monthly > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Gross Income",     f"${total_income:,.0f}",      "per month")
    k2.metric("Net Take-Home",    f"${net_monthly:,.0f}",       f"after {total_tax_rate:.1f}% taxes")
    k3.metric("Total Expenses",   f"${total_expenses:,.0f}",    "per month")
    k4.metric("Monthly Surplus",  f"${monthly_surplus:,.0f}",   "after expenses & taxes")
    k5.metric("Monthly Invested", f"${monthly_investment:,.0f}", f"{invest_pct}% of net")
    k6.metric("Future Value",     f"${future_value:,.0f}",      f"{years} yrs @ {arr}% ARR")

    st.divider()
    col_left, col_right = st.columns(2)

    alloc_labels, alloc_vals = [], []
    if monthly_taxes      > 0: alloc_labels.append("Taxes");     alloc_vals.append(round(monthly_taxes))
    if total_expenses     > 0: alloc_labels.append("Expenses");  alloc_vals.append(round(total_expenses))
    if monthly_investment > 0: alloc_labels.append("Invested");  alloc_vals.append(round(monthly_investment))
    remaining = max(0, monthly_surplus - monthly_investment)
    if remaining          > 0: alloc_labels.append("Remaining"); alloc_vals.append(round(remaining))

    if alloc_vals:
        with col_left:
            fig_alloc = go.Figure(go.Pie(labels=alloc_labels, values=alloc_vals, hole=0.45, textinfo="label+percent"))
            fig_alloc.update_layout(title="💵 Income Allocation", template="plotly_dark", height=320)
            st.plotly_chart(fig_alloc, use_container_width=True)

    exp_data = {k: v for k, v in {
        "Housing": housing, "Utilities": utilities, "Groceries": groceries,
        "Transport": transportation, "Insurance": insurance, "Healthcare": healthcare,
        "Subscriptions": subscriptions, "Dining": dining, "Entertainment": entertainment,
        "Clothing": clothing, "Education": education, "Personal Care": personal_care,
        "Childcare": childcare, "Pets": pet_care, "Other": other_expenses,
    }.items() if v > 0}

    if exp_data:
        with col_right:
            fig_exp = go.Figure(go.Pie(labels=list(exp_data.keys()), values=list(exp_data.values()), hole=0.45))
            fig_exp.update_layout(title="💸 Expense Breakdown", template="plotly_dark", height=320)
            st.plotly_chart(fig_exp, use_container_width=True)

    if total_income > 0:
        bar_names  = ["Gross Income", "Net Income", "Expenses", "Taxes", "Invested", "Surplus"]
        bar_vals   = [total_income, net_monthly, total_expenses, monthly_taxes, monthly_investment, monthly_surplus]
        bar_colors = ["#60a5fa", "#34d399", "#f87171", "#fbbf24", "#a78bfa", "#2dd4bf"]
        fig_bar = go.Figure(go.Bar(x=bar_names, y=bar_vals, marker_color=bar_colors,
                                   text=[f"${v:,.0f}" for v in bar_vals], textposition="outside"))
        fig_bar.update_layout(title="📊 Monthly Financial Overview", template="plotly_dark", height=360,
                              yaxis=dict(tickprefix="$", tickformat=",.0f"))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 📋 Financial Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Income & Taxes**")
        st.markdown(f"Gross Monthly Income: **${total_income:,.2f}**")
        st.markdown(f"Annual Gross Income: **${total_income*12:,.2f}**")
        st.markdown(f"Total Withholdings ({total_tax_rate:.1f}%): **-${monthly_taxes:,.2f}/mo**")
        st.markdown(f"Net Monthly Income: **${net_monthly:,.2f}**")
    with c2:
        st.markdown("**Expenses & Cash Flow**")
        st.markdown(f"Total Monthly Expenses: **-${total_expenses:,.2f}**")
        st.markdown(f"Monthly Investment: **-${monthly_investment:,.2f}**")
        st.markdown(f"Monthly Surplus: **${monthly_surplus:,.2f}**")
        st.markdown(f"Savings Rate: **{savings_rate:.1f}%**")
    with c3:
        st.markdown("**Investment Projection**")
        st.markdown(f"Monthly Investment: **${monthly_investment:,.2f}**")
        st.markdown(f"Total Contributions ({years} yrs): **${total_contributions:,.2f}**")
        st.markdown(f"Compound Gains ({arr}% ARR): **+${total_gains:,.2f}**")
        st.markdown(f"Future Portfolio Value: **${future_value:,.2f}**")
