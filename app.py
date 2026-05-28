import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
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
        monthly_salary   = st.number_input("Monthly Salary / Wages ($)",      min_value=0.0, step=100.0, format="%.2f")
        freelance        = st.number_input("Freelance / Side Income ($)",      min_value=0.0, step=50.0,  format="%.2f")
        rental           = st.number_input("Rental Income ($)",                min_value=0.0, step=50.0,  format="%.2f")
    with col2:
        dividends        = st.number_input("Dividends & Interest ($)",         min_value=0.0, step=10.0,  format="%.2f")
        other_income     = st.number_input("Other Income ($)",                 min_value=0.0, step=50.0,  format="%.2f")

    total_income = monthly_salary + freelance + rental + dividends + other_income
    st.success(f"**Total Monthly Gross Income: ${total_income:,.2f}**")

    with st.expander("💡 Tips"):
        st.markdown("""
- Enter **gross (pre-tax)** income — taxes are handled in the Taxes tab.
- For variable income, use your **average** monthly amount.
- Include all recurring income streams for the most accurate picture.
        """)

# ── Expenses ──────────────────────────────────────────────────────────────────
with tab_expenses:
    st.subheader("Monthly Expenses")

    st.markdown("#### 🏠 Essential")
    c1, c2, c3 = st.columns(3)
    with c1:
        housing        = st.number_input("Housing (Rent/Mortgage) ($)",             min_value=0.0, step=50.0, format="%.2f")
        utilities      = st.number_input("Utilities (Electric, Gas, Water) ($)",    min_value=0.0, step=10.0, format="%.2f")
    with c2:
        groceries      = st.number_input("Groceries & Food ($)",                    min_value=0.0, step=10.0, format="%.2f")
        transportation = st.number_input("Transportation (Car, Gas, Transit) ($)",  min_value=0.0, step=10.0, format="%.2f")
    with c3:
        insurance      = st.number_input("Insurance (Auto, Home, Life) ($)",        min_value=0.0, step=10.0, format="%.2f")
        healthcare     = st.number_input("Healthcare & Medical ($)",                min_value=0.0, step=10.0, format="%.2f")

    essential_total = housing + utilities + groceries + transportation + insurance + healthcare
    st.info(f"Essential Subtotal: **${essential_total:,.2f}**")

    st.markdown("#### 🎬 Lifestyle")
    c1, c2 = st.columns(2)
    with c1:
        subscriptions  = st.number_input("Subscriptions & Memberships ($)",  min_value=0.0, step=5.0,  format="%.2f")
        dining         = st.number_input("Dining Out & Takeout ($)",          min_value=0.0, step=10.0, format="%.2f")
    with c2:
        entertainment  = st.number_input("Entertainment & Hobbies ($)",       min_value=0.0, step=10.0, format="%.2f")
        clothing       = st.number_input("Clothing & Accessories ($)",         min_value=0.0, step=10.0, format="%.2f")

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
    st.caption("Enter percentage rates (not dollar amounts)")

    # 2024 bracket estimator
    BRACKETS_2024 = [
        (0,       11_600,  10),
        (11_600,  47_150,  12),
        (47_150,  100_525, 22),
        (100_525, 191_950, 24),
        (191_950, 243_725, 32),
        (243_725, 609_350, 35),
        (609_350, math.inf, 37),
    ]

    annual_income = total_income * 12
    if annual_income > 0:
        tax_amt = 0.0
        for lo, hi, rate in BRACKETS_2024:
            if annual_income > lo:
                taxable = min(annual_income, hi) - lo
                tax_amt += taxable * rate / 100
        suggested_federal = (tax_amt / annual_income) * 100

        st.info(
            f"📋 **2024 Federal Tax Bracket Estimate** — "
            f"Based on **${annual_income:,.0f}** annual income, your effective federal rate is "
            f"approximately **{suggested_federal:.1f}%**. Enter this below."
        )

        bracket_cols = st.columns(len(BRACKETS_2024))
        for i, (lo, hi, rate) in enumerate(BRACKETS_2024):
            active = annual_income > lo
            label = f"**{rate}%**" if active else f"{rate}%"
            hi_str = "+" if hi == math.inf else f"–${hi/1000:.0f}K"
            bracket_cols[i].markdown(
                f"{'🟦' if active else '⬜'} {label}  \n${lo/1000:.0f}K {hi_str}",
                unsafe_allow_html=False,
            )

    c1, c2, c3 = st.columns(3)
    with c1:
        federal_rate    = st.number_input("Federal Income Tax Rate (%)",    min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
        state_rate      = st.number_input("State Income Tax Rate (%)",      min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
    with c2:
        social_security = st.number_input("Social Security / OASDI (%)",   min_value=0.0, max_value=100.0, value=6.2, step=0.1, format="%.2f")
        medicare        = st.number_input("Medicare / FICA (%)",            min_value=0.0, max_value=100.0, value=1.45, step=0.1, format="%.2f")
    with c3:
        state_disability = st.number_input("State Disability Ins. (%)",    min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
        other_withholding = st.number_input("Other Withholdings (%)",       min_value=0.0, max_value=100.0, step=0.1, format="%.1f", help="HSA, 401k pre-tax, etc.")

    total_tax_rate   = federal_rate + state_rate + social_security + medicare + state_disability + other_withholding
    monthly_taxes    = total_income * (total_tax_rate / 100)
    net_monthly      = total_income - monthly_taxes

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Withholding Rate",  f"{total_tax_rate:.2f}%")
    col2.metric("Monthly Taxes",           f"-${monthly_taxes:,.2f}")
    col3.metric("Net Monthly Take-Home",   f"${net_monthly:,.2f}")

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
        years = st.number_input(
            "Investment Duration (years)",
            min_value=1, max_value=60, value=30, step=1
        )
    with c4:
        freq_label = st.selectbox(
            "Compounding Frequency",
            ["Daily", "Weekly", "Monthly", "Quarterly", "Annually"]
        )

    freq_map = {"Daily": 365, "Weekly": 52, "Monthly": 12, "Quarterly": 4, "Annually": 1}
    periods_per_year = freq_map[freq_label]

    monthly_investment  = net_monthly * (invest_pct / 100)
    total_contributions = monthly_investment * 12 * years

    r = (arr / 100) / periods_per_year
    n = years * periods_per_year
    pmt = monthly_investment * (periods_per_year / 12)

    if arr > 0 and monthly_investment > 0:
        future_value = pmt * ((math.pow(1 + r, n) - 1) / r)
    else:
        future_value = total_contributions

    total_gains = future_value - total_contributions

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Investment",      f"${monthly_investment:,.0f}",    f"{invest_pct}% of net income")
    col2.metric("Total Contributions",     f"${total_contributions:,.0f}",   f"Over {years} years")
    col3.metric("Investment Gains",        f"${total_gains:,.0f}",           "Compound interest earned")
    col4.metric("Future Portfolio Value",  f"${future_value:,.0f}",          f"In {years} yrs at {arr}% ARR")

    # Growth chart
    if monthly_investment > 0:
        chart_years  = list(range(years + 1))
        portfolio_vals, contrib_vals = [], []
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
            title="📊 Portfolio Growth Over Time",
            xaxis_title="Year", yaxis_title="Value ($)",
            template="plotly_dark", height=380,
            yaxis=dict(tickprefix="$", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Milestones
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
            if yrs_to:
                reached = yrs_to <= years
                status  = f"✅ {yrs_to:.1f} yrs" if reached else f"~{yrs_to:.1f} yrs"
            else:
                status  = "—"
            m_cols[i].metric(label, status)

# ── Dashboard ─────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.subheader("Financial Dashboard")

    monthly_surplus = net_monthly - total_expenses
    savings_rate    = (monthly_surplus / net_monthly * 100) if net_monthly > 0 else 0

    # KPI row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Gross Income",      f"${total_income:,.0f}",       "per month")
    k2.metric("Net Take-Home",     f"${net_monthly:,.0f}",        f"after {total_tax_rate:.1f}% taxes")
    k3.metric("Total Expenses",    f"${total_expenses:,.0f}",     "per month")
    k4.metric("Monthly Surplus",   f"${monthly_surplus:,.0f}",    "after expenses & taxes",
              delta_color="normal" if monthly_surplus >= 0 else "inverse")
    k5.metric("Monthly Invested",  f"${monthly_investment:,.0f}", f"{invest_pct}% of net")
    k6.metric("Future Value",      f"${future_value:,.0f}",       f"{years} yrs @ {arr}% ARR")

    st.divider()

    col_left, col_right = st.columns(2)

    # Income allocation pie
    alloc_labels, alloc_vals = [], []
    if monthly_taxes      > 0: alloc_labels.append("Taxes");     alloc_vals.append(round(monthly_taxes))
    if total_expenses     > 0: alloc_labels.append("Expenses");  alloc_vals.append(round(total_expenses))
    if monthly_investment > 0: alloc_labels.append("Invested");  alloc_vals.append(round(monthly_investment))
    remaining = max(0, monthly_surplus - monthly_investment)
    if remaining          > 0: alloc_labels.append("Remaining"); alloc_vals.append(round(remaining))

    if alloc_vals:
        with col_left:
            fig_alloc = go.Figure(go.Pie(
                labels=alloc_labels, values=alloc_vals,
                hole=0.45, textinfo="label+percent",
            ))
            fig_alloc.update_layout(title="💵 Income Allocation", template="plotly_dark", height=320)
            st.plotly_chart(fig_alloc, use_container_width=True)

    # Expense breakdown pie
    exp_data = {
        "Housing": housing, "Utilities": utilities, "Groceries": groceries,
        "Transport": transportation, "Insurance": insurance, "Healthcare": healthcare,
        "Subscriptions": subscriptions, "Dining": dining, "Entertainment": entertainment,
        "Clothing": clothing, "Education": education, "Personal Care": personal_care,
        "Childcare": childcare, "Pets": pet_care, "Other": other_expenses,
    }
    exp_data = {k: v for k, v in exp_data.items() if v > 0}

    if exp_data:
        with col_right:
            fig_exp = go.Figure(go.Pie(
                labels=list(exp_data.keys()), values=list(exp_data.values()),
                hole=0.45, textinfo="label+percent",
            ))
            fig_exp.update_layout(title="💸 Expense Breakdown", template="plotly_dark", height=320)
            st.plotly_chart(fig_exp, use_container_width=True)

    # Monthly bar chart
    if total_income > 0:
        bar_names  = ["Gross Income", "Net Income", "Expenses", "Taxes", "Invested", "Surplus"]
        bar_vals   = [total_income, net_monthly, total_expenses, monthly_taxes, monthly_investment, monthly_surplus]
        bar_colors = ["#60a5fa",    "#34d399",    "#f87171",    "#fbbf24", "#a78bfa",  "#2dd4bf"]

        fig_bar = go.Figure(go.Bar(
            x=bar_names, y=bar_vals,
            marker_color=bar_colors,
            text=[f"${v:,.0f}" for v in bar_vals],
            textposition="outside",
        ))
        fig_bar.update_layout(
            title="📊 Monthly Financial Overview",
            template="plotly_dark", height=360,
            yaxis=dict(tickprefix="$", tickformat=",.0f"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Summary table
    st.markdown("#### 📋 Financial Summary")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Income & Taxes**")
        st.markdown(f"Gross Monthly Income: **${total_income:,.2f}**")
        st.markdown(f"Total Withholdings ({total_tax_rate:.1f}%): **-${monthly_taxes:,.2f}**")
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
