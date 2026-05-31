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
    "annual_income_calc": 0.0,
    "filing_status_key": "Single",
    "state_selector_key": "Texas",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def auto_calc_taxes():
    """Recalculate all tax rates from annual income, filing status and state — called on any change."""
    income = st.session_state.get("annual_income_calc", 0.0)
    filing = st.session_state.get("filing_status_key", "Single")
    state  = st.session_state.get("state_selector_key", "Texas")
    if income <= 0:
        return
    std_ded = STANDARD_DEDUCTIONS[filing]
    taxable = max(0.0, income - std_ded)
    st.session_state["fed_rate"]   = round(calc_federal_effective_rate(taxable, filing), 2)
    st.session_state["state_rate"] = round(calc_state_effective_rate(income, state), 2)
    ss = min(income, SS_WAGE_BASE_2024) / income * 6.2
    st.session_state["ss_rate"]    = round(ss, 3)
    med_threshold = 250_000 if filing == "Married Filing Jointly" else 200_000
    med = 1.45 + ((income - med_threshold) / income * 0.9 if income > med_threshold else 0)
    st.session_state["med_rate"]   = round(med, 3)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Financial Planner & Investment Calculator")
st.caption("Track income, expenses, taxes, and grow your wealth")

tab_income, tab_expenses, tab_taxes, tab_investment, tab_dashboard = st.tabs(
    ["💰 Income", "💸 Expenses", "🏛️ Taxes", "📈 Investment", "📊 Dashboard"]
)

# ── Income ────────────────────────────────────────────────────────────────────
with tab_income:
    st.subheader("💰 Income & Tax Details")

    # ── Primary: Annual salary + tax setup ────────────────────────────────────
    st.markdown("### Annual Salary")
    st.caption("Enter your annual gross salary along with your filing status and state — net monthly is calculated automatically.")

    ai1, ai2, ai3 = st.columns(3)
    with ai1:
        st.number_input(
            "Annual Gross Salary ($)",
            min_value=0.0,
            step=1000.0,
            format="%.2f",
            key="annual_income_calc",
            on_change=auto_calc_taxes,
            help="Your total pre-tax annual salary.",
        )
    with ai2:
        st.selectbox(
            "Filing Status",
            ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"],
            key="filing_status_key",
            on_change=auto_calc_taxes,
        )
    with ai3:
        st.selectbox(
            "🗺️ State of Residence",
            sorted(STATE_TAX.keys()),
            key="state_selector_key",
            on_change=auto_calc_taxes,
        )

    # Derive values from annual input
    annual_salary   = st.session_state["annual_income_calc"]
    monthly_salary  = annual_salary / 12
    filing_status_inc = st.session_state["filing_status_key"]
    state_inc         = st.session_state["state_selector_key"]

    # Show quick after-tax preview immediately below the inputs
    if annual_salary > 0:
        _std   = STANDARD_DEDUCTIONS[filing_status_inc]
        _tax   = calc_federal_effective_rate(max(0, annual_salary - _std), filing_status_inc)
        _st    = calc_state_effective_rate(annual_salary, state_inc)
        _ss    = min(annual_salary, SS_WAGE_BASE_2024) / annual_salary * 6.2
        _med   = 1.45
        _total = _tax + _st + _ss + _med
        _net_monthly = (annual_salary * (1 - _total / 100)) / 12

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Monthly Gross",        f"${monthly_salary:,.2f}",  "annual ÷ 12")
        p2.metric("Est. Monthly Taxes",   f"-${monthly_salary * _total / 100:,.2f}", f"{_total:.1f}% total rate")
        p3.metric("Net Monthly Take-Home",f"${_net_monthly:,.2f}",    f"after {state_inc} taxes")
        p4.metric("State",                state_inc, STATE_TAX[state_inc]["type"].title() +
                  (f" {STATE_TAX[state_inc]['rate']}%" if STATE_TAX[state_inc]["type"] == "flat" else " brackets"))

    st.divider()

    # ── Additional income sources ──────────────────────────────────────────────
    st.markdown("### Additional Income Sources")
    st.caption("Optional — add any other monthly income on top of your salary.")

    col1, col2 = st.columns(2)
    with col1:
        freelance  = st.number_input("Freelance / Side Income ($/mo)",  min_value=0.0, step=50.0,  format="%.2f")
        rental     = st.number_input("Rental Income ($/mo)",             min_value=0.0, step=50.0,  format="%.2f")
    with col2:
        dividends  = st.number_input("Dividends & Interest ($/mo)",      min_value=0.0, step=10.0,  format="%.2f")
        other_income = st.number_input("Other Income ($/mo)",            min_value=0.0, step=50.0,  format="%.2f")

    total_income = monthly_salary + freelance + rental + dividends + other_income
    st.success(f"**Total Monthly Gross Income: ${total_income:,.2f}** &nbsp;&nbsp;(salary ${monthly_salary:,.2f} + additional ${freelance+rental+dividends+other_income:,.2f})")

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
    st.subheader("🏛️ Taxes & Withholdings")
    st.caption("Annual salary, filing status, and state are set in the **Income tab**. Rates update automatically.")

    # Read values set in the Income tab
    annual_income_input = st.session_state["annual_income_calc"]
    filing_status       = st.session_state["filing_status_key"]
    state_selected      = st.session_state["state_selector_key"]
    std_ded             = STANDARD_DEDUCTIONS[filing_status]
    taxable             = max(0.0, annual_income_input - std_ded)

    if annual_income_input == 0:
        st.info("👈 Go to the **Income tab** and enter your Annual Gross Salary to see your tax breakdown here.")

    # ── Step 1: State Tax Breakdown ────────────────────────────────────────────
    st.markdown(f"### Step 1 — State Tax: **{state_selected}**")

    state_data  = STATE_TAX[state_selected]
    state_rate_val = calc_state_effective_rate(annual_income_input, state_selected)

    col_info, col_chart = st.columns([1, 2])
    with col_info:
        if state_data["type"] == "flat":
            if state_data["rate"] == 0:
                st.success(f"**{state_selected} has NO state income tax** 🎉")
            else:
                st.info(f"**{state_selected}** uses a **flat {state_data['rate']}%** rate on all income.")
        else:
            st.info(f"**{state_selected}** uses **progressive brackets** (rates rise with income).")

        st.metric("Your Effective State Rate",
                  f"{state_rate_val:.2f}%",
                  f"${annual_income_input * state_rate_val / 100:,.0f} / yr" if annual_income_input > 0 else "—")
        if annual_income_input > 0 and state_data["type"] == "brackets":
            # Find marginal rate
            marginal = 0
            for lo, hi, rate in state_data["brackets"]:
                if annual_income_input > lo:
                    marginal = rate
            st.metric("Marginal Rate (top bracket)", f"{marginal:.2f}%")

    with col_chart:
        if state_data["type"] == "brackets" and annual_income_input > 0:
            brackets = state_data["brackets"]
            b_labels, b_rates, b_colors = [], [], []
            for lo, hi, rate in brackets:
                hi_str = "No limit" if hi == math.inf else f"${hi:,.0f}"
                b_labels.append(f"${lo:,.0f}–{hi_str}")
                b_rates.append(rate)
                b_colors.append("#60a5fa" if annual_income_input > lo else "#334155")
            fig_st = go.Figure(go.Bar(
                x=b_labels, y=b_rates,
                marker_color=b_colors,
                text=[f"{r}%" for r in b_rates],
                textposition="outside",
            ))
            fig_st.update_layout(
                title=f"{state_selected} — Tax Brackets",
                template="plotly_dark", height=280,
                yaxis=dict(ticksuffix="%", title="Rate"),
                xaxis=dict(title="Income Range"),
                margin=dict(t=40, b=60),
                showlegend=False,
            )
            st.plotly_chart(fig_st, use_container_width=True)
        elif state_data["type"] == "flat":
            # Show a simple comparison of no-tax vs flat-tax vs progressive states for context
            compare = {
                "No Tax\n(TX, FL, NV…)": 0,
                f"{state_selected}\n({state_data['rate']}%)": state_data["rate"],
                "CA Top\n(13.3%)": 13.3,
            }
            fig_cmp = go.Figure(go.Bar(
                x=list(compare.keys()), y=list(compare.values()),
                marker_color=["#34d399", "#60a5fa", "#f87171"],
                text=[f"{v}%" for v in compare.values()],
                textposition="outside",
            ))
            fig_cmp.update_layout(
                title="State Rate Comparison", template="plotly_dark", height=280,
                yaxis=dict(ticksuffix="%"), margin=dict(t=40),
            )
            st.plotly_chart(fig_cmp, use_container_width=True)

    # ── Step 2: Federal Bracket Visualizer ────────────────────────────────────
    st.divider()
    st.markdown("### Step 2 — Federal Tax Brackets")
    if annual_income_input > 0:
        brackets = (FED_BRACKETS_MFJ if filing_status == "Married Filing Jointly"
                    else FED_BRACKETS_HOH if filing_status == "Head of Household"
                    else FED_BRACKETS_SINGLE)
        fed_labels, fed_rates, fed_colors, fed_amounts = [], [], [], []
        for lo, hi, rate in brackets:
            hi_str = "No limit" if hi == math.inf else f"${hi:,.0f}"
            fed_labels.append(f"${lo:,.0f}–{hi_str}\n({rate}%)")
            fed_rates.append(rate)
            fed_colors.append("#60a5fa" if taxable > lo else "#334155")
            amt = max(0, (min(taxable, hi) - lo) * rate / 100) if taxable > lo else 0
            fed_amounts.append(round(amt))

        fig_fed = go.Figure()
        fig_fed.add_trace(go.Bar(name="Tax Rate", x=fed_labels, y=fed_rates,
                                 marker_color=fed_colors, yaxis="y",
                                 text=[f"{r}%" for r in fed_rates], textposition="outside"))
        fig_fed.add_trace(go.Bar(name="Tax Amount ($)", x=fed_labels, y=fed_amounts,
                                 marker_color=["#fbbf24" if c == "#60a5fa" else "#1e3a5f" for c in fed_colors],
                                 yaxis="y2", opacity=0.7,
                                 text=[f"${a:,}" if a > 0 else "" for a in fed_amounts], textposition="inside"))
        fig_fed.update_layout(
            title=f"Federal Brackets — {filing_status} | Taxable Income: ${taxable:,.0f} (after ${std_ded:,} std. deduction)",
            template="plotly_dark", height=340, barmode="group",
            yaxis=dict(title="Rate (%)", ticksuffix="%"),
            yaxis2=dict(title="Tax Amount ($)", overlaying="y", side="right", tickprefix="$"),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_fed, use_container_width=True)

        # Summary metrics row
        sugg_federal = calc_federal_effective_rate(taxable, filing_status)
        sugg_ss      = min(annual_income_input, SS_WAGE_BASE_2024) / annual_income_input * 6.2
        med_threshold = 250_000 if filing_status == "Married Filing Jointly" else 200_000
        sugg_med     = 1.45 + ((annual_income_input - med_threshold) / annual_income_input * 0.9 if annual_income_input > med_threshold else 0)
        total_calculated = sugg_federal + state_rate_val + sugg_ss + sugg_med

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Federal Effective",   f"{sugg_federal:.2f}%",     f"${annual_income_input*sugg_federal/100:,.0f}/yr")
        m2.metric("State Effective",     f"{state_rate_val:.2f}%",   f"${annual_income_input*state_rate_val/100:,.0f}/yr")
        m3.metric("Social Security",     f"{sugg_ss:.2f}%",          f"cap ${SS_WAGE_BASE_2024:,}")
        m4.metric("Medicare",            f"{sugg_med:.3f}%",         "+0.9% surtax >$200K")
        m5.metric("Total Calculated",    f"{total_calculated:.2f}%", f"${annual_income_input*total_calculated/100:,.0f}/yr")

    st.divider()

    # ── Step 3: Editable Rate Fields ──────────────────────────────────────────
    st.markdown("### Step 3 — Review & Adjust Rates")
    st.caption("Rates auto-filled from the calculator above. Edit any field to override.")

    c1, c2, c3 = st.columns(3)
    with c1:
        federal_rate     = st.number_input("Federal Income Tax Rate (%)",  min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="fed_rate")
        state_rate       = st.number_input("State Income Tax Rate (%)",    min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="state_rate")
    with c2:
        social_security  = st.number_input("Social Security / OASDI (%)", min_value=0.0, max_value=100.0, step=0.01, format="%.3f", key="ss_rate")
        medicare         = st.number_input("Medicare / FICA (%)",          min_value=0.0, max_value=100.0, step=0.01, format="%.3f", key="med_rate")
    with c3:
        state_disability = st.number_input("State Disability Ins. (%)",   min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="sdi_rate")
        other_withholding= st.number_input("Other Withholdings (%)",       min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="other_rate",
                                           help="401k pre-tax, HSA, etc.")

    total_tax_rate = federal_rate + state_rate + social_security + medicare + state_disability + other_withholding
    monthly_taxes  = total_income * (total_tax_rate / 100)
    net_monthly    = total_income - monthly_taxes

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Withholding Rate", f"{total_tax_rate:.2f}%")
    col2.metric("Annual Tax Estimate",    f"${monthly_taxes * 12:,.0f}")
    col3.metric("Monthly Taxes",          f"-${monthly_taxes:,.2f}")
    col4.metric("Net Monthly Take-Home",  f"${net_monthly:,.2f}")

# ── Investment ────────────────────────────────────────────────────────────────
with tab_investment:
    st.subheader("📈 Investment Settings")

    # ── Surplus banner ────────────────────────────────────────────────────────
    monthly_surplus = net_monthly - total_expenses
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Net Monthly Income",   f"${net_monthly:,.2f}")
    s2.metric("Total Expenses",       f"-${total_expenses:,.2f}")
    s3.metric("Monthly Surplus",      f"${monthly_surplus:,.2f}",
              delta="available to invest" if monthly_surplus > 0 else "deficit — reduce expenses")
    s4.metric("Surplus %",
              f"{(monthly_surplus / net_monthly * 100):.1f}%" if net_monthly > 0 else "—",
              "of net income")

    st.divider()

    # ── Auto-invest toggle ────────────────────────────────────────────────────
    if "auto_invest_surplus" not in st.session_state:
        st.session_state["auto_invest_surplus"] = False

    auto_invest = st.toggle(
        "🔄 Automatically invest all remaining surplus (net income − expenses)",
        key="auto_invest_surplus",
    )

    if auto_invest:
        if monthly_surplus > 0:
            monthly_investment = monthly_surplus
            invest_pct = (monthly_investment / net_monthly * 100) if net_monthly > 0 else 0
            st.success(
                f"Investing your full surplus: **${monthly_investment:,.2f}/mo** "
                f"({invest_pct:.1f}% of net income)"
            )
        else:
            monthly_investment = 0.0
            invest_pct = 0.0
            st.warning("⚠️ No surplus to invest — your expenses exceed your net income. Reduce expenses first.")
    else:
        c1_inv, _ = st.columns([1, 3])
        with c1_inv:
            invest_pct = st.number_input(
                f"Investment % of Net Income  (Net: ${net_monthly:,.0f}/mo)",
                min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f",
            )
        monthly_investment = net_monthly * (invest_pct / 100)
        if monthly_investment > monthly_surplus and monthly_surplus > 0:
            st.warning(
                f"⚠️ You're investing **${monthly_investment:,.2f}** but your surplus is only "
                f"**${monthly_surplus:,.2f}**. Consider reducing your investment % or expenses."
            )

    st.divider()

    # ── Return & duration settings ────────────────────────────────────────────
    c2, c3, c4 = st.columns(3)
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
    total_contributions = monthly_investment * 12 * years
    r   = (arr / 100) / periods_per_year
    n   = years * periods_per_year
    pmt = monthly_investment * (12 / periods_per_year)

    future_value = pmt * ((math.pow(1 + r, n) - 1) / r) if (arr > 0 and monthly_investment > 0) else total_contributions
    total_gains  = future_value - total_contributions

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Investment",     f"${monthly_investment:,.0f}",    f"{invest_pct:.1f}% of net income")
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

    # ── House Purchase Goal ────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🏠 House Purchase Goal")

    if "house_goal_on" not in st.session_state:
        st.session_state["house_goal_on"] = False

    house_goal_on = st.toggle("Enable house purchase goal", key="house_goal_on")

    if house_goal_on:
        # Auto-suggest capital gains rate from income + filing status
        ann_inc   = st.session_state.get("annual_income_calc", 0.0)
        filing    = st.session_state.get("filing_status_key", "Single")
        CG_THRESHOLDS = {
            "Single":                    [(47_025, 0), (518_900, 15), (math.inf, 20)],
            "Married Filing Jointly":    [(94_050, 0), (583_750, 15), (math.inf, 20)],
            "Married Filing Separately": [(47_025, 0), (291_850, 15), (math.inf, 20)],
            "Head of Household":         [(63_000, 0), (551_350, 15), (math.inf, 20)],
        }
        suggested_cg = 15  # default
        for threshold, rate in CG_THRESHOLDS.get(filing, CG_THRESHOLDS["Single"]):
            if ann_inc <= threshold:
                suggested_cg = rate
                break

        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            house_price = st.number_input(
                "Target House Price / Down Payment ($)",
                min_value=0.0, step=10_000.0, format="%.0f",
                help="The amount you need after paying capital gains tax on your investment gains.",
            )
        with hc2:
            cg_rate_pct = st.number_input(
                "Capital Gains Tax Rate (%)",
                min_value=0.0, max_value=40.0,
                value=float(suggested_cg), step=1.0, format="%.1f",
                help=f"2024 long-term rate suggested for your income: {suggested_cg}%",
            )
        with hc3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"**2024 suggested rate: {suggested_cg}%**  \n"
                    f"Based on ${ann_inc:,.0f} income ({filing})")

        if house_price > 0 and monthly_investment > 0:
            cg_rate = cg_rate_pct / 100

            # ── Phase 1: find the year portfolio (after tax) reaches house_price
            sell_year = None
            sell_fv = sell_contributions = sell_gains = sell_tax = after_tax_proceeds = 0.0

            # Search beyond `years` too (up to 60) so we can report even if outside window
            max_search = max(years, 60)
            for y in range(1, max_search + 1):
                n_y   = y * periods_per_year
                fv_y  = pmt * ((math.pow(1 + r, n_y) - 1) / r) if arr > 0 else monthly_investment * 12 * y
                c_y   = monthly_investment * 12 * y
                g_y   = max(0.0, fv_y - c_y)
                # After-tax = contributions (basis, no tax) + gains after CGT
                at_y  = c_y + g_y * (1 - cg_rate)
                if at_y >= house_price:
                    sell_year          = y
                    sell_fv            = fv_y
                    sell_contributions = c_y
                    sell_gains         = g_y
                    sell_tax           = g_y * cg_rate
                    after_tax_proceeds = at_y
                    break

            if sell_year is None:
                st.error(
                    f"❌ Your portfolio won't reach **${house_price:,.0f}** (after {cg_rate_pct:.0f}% CGT) "
                    f"even in 60 years at {arr}% ARR. "
                    f"Try increasing your monthly investment, ARR, or lowering the target."
                )
            else:
                within_window = sell_year <= years
                remaining_years = max(0, years - sell_year)

                # Phase 2: restart from $0 for remaining years
                n2   = remaining_years * periods_per_year
                phase2_fv = (pmt * ((math.pow(1 + r, n2) - 1) / r)
                             if (arr > 0 and remaining_years > 0) else monthly_investment * 12 * remaining_years)
                phase2_contribs = monthly_investment * 12 * remaining_years
                phase2_gains    = max(0.0, phase2_fv - phase2_contribs)

                import datetime
                current_year = datetime.date.today().year
                purchase_year = current_year + sell_year

                # ── Summary metrics
                if within_window:
                    st.success(
                        f"🏠 You can buy the house in **Year {sell_year}** ({purchase_year})  |  "
                        f"Portfolio value: **${sell_fv:,.0f}**  →  "
                        f"After {cg_rate_pct:.0f}% CGT: **${after_tax_proceeds:,.0f}**  |  "
                        f"Tax paid: **${sell_tax:,.0f}**"
                    )
                else:
                    st.warning(
                        f"🏠 Target reachable in **Year {sell_year}** ({purchase_year}) — "
                        f"outside your {years}-yr window. Extend duration or raise ARR."
                    )

                r1c1, r1c2, r1c3, r1c4 = st.columns(4)
                r1c1.metric("Year of Purchase",       f"Year {sell_year} ({purchase_year})")
                r1c2.metric("Portfolio at Sale",      f"${sell_fv:,.0f}")
                r1c3.metric("Capital Gains Tax",      f"-${sell_tax:,.0f}", f"{cg_rate_pct:.0f}% on ${sell_gains:,.0f} gains")
                r1c4.metric("Net After-Tax Proceeds", f"${after_tax_proceeds:,.0f}")

                if within_window and remaining_years > 0:
                    st.markdown(f"**Phase 2** — After buying, you restart investing for the remaining **{remaining_years} years**:")
                    r2c1, r2c2, r2c3 = st.columns(3)
                    r2c1.metric("Phase 2 Monthly Investment", f"${monthly_investment:,.0f}")
                    r2c2.metric("Phase 2 Total Contributions", f"${phase2_contribs:,.0f}")
                    r2c3.metric("Phase 2 Final Portfolio",    f"${phase2_fv:,.0f}",
                                f"+${phase2_gains:,.0f} gains")

                # ── Dual-phase chart
                phase1_years = list(range(sell_year + 1))
                phase1_vals  = []
                for y in phase1_years:
                    n_y  = y * periods_per_year
                    fv_y = pmt * ((math.pow(1 + r, n_y) - 1) / r) if arr > 0 else monthly_investment * 12 * y
                    phase1_vals.append(round(fv_y))

                phase2_x, phase2_vals = [], []
                if within_window and remaining_years > 0:
                    for y in range(remaining_years + 1):
                        n_y  = y * periods_per_year
                        fv_y = (pmt * ((math.pow(1 + r, n_y) - 1) / r)
                                if arr > 0 else monthly_investment * 12 * y)
                        phase2_x.append(sell_year + y)
                        phase2_vals.append(round(fv_y))

                fig_house = go.Figure()
                fig_house.add_trace(go.Scatter(
                    x=phase1_years, y=phase1_vals, name="Phase 1 — Save for House",
                    fill="tozeroy", line=dict(color="#60a5fa", width=2.5)
                ))
                if phase2_vals:
                    fig_house.add_trace(go.Scatter(
                        x=phase2_x, y=phase2_vals, name="Phase 2 — Resume Investing",
                        fill="tozeroy", line=dict(color="#34d399", width=2.5)
                    ))
                # House target line
                fig_house.add_hline(
                    y=house_price, line_dash="dash", line_color="#fbbf24",
                    annotation_text=f"House Target ${house_price:,.0f}",
                    annotation_position="top left",
                )
                # Sell marker
                fig_house.add_vline(
                    x=sell_year, line_dash="dot", line_color="#f87171",
                    annotation_text=f"🏠 Sell Yr {sell_year}",
                    annotation_position="top right",
                )
                fig_house.update_layout(
                    title="📈 Two-Phase Investment Plan",
                    xaxis_title="Year", yaxis_title="Portfolio Value ($)",
                    template="plotly_dark", height=420,
                    yaxis=dict(tickprefix="$", tickformat=",.0f"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_house, use_container_width=True)

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
