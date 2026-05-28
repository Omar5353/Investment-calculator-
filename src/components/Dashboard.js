import React from 'react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';

const COLORS = ['#60a5fa', '#34d399', '#f87171', '#fbbf24', '#a78bfa', '#fb923c', '#38bdf8', '#4ade80', '#f472b6', '#facc15', '#818cf8', '#2dd4bf', '#e879f9', '#fb7185', '#84cc16'];

function fmt$(v) {
  return `$${v.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export default function Dashboard({ summary, incomeData, expenseData, taxData, investmentData }) {
  const {
    totalMonthlyIncome, totalMonthlyExpenses, monthlyTaxes,
    netMonthlyIncome, monthlySurplus, monthlyInvestment,
    futureValue, totalContributions, totalGains, taxRate, investPct, arr, years,
  } = summary;

  const savingsRate = netMonthlyIncome > 0 ? ((monthlySurplus / netMonthlyIncome) * 100).toFixed(1) : 0;

  const incomeBreakdown = [
    { name: 'Taxes', value: Math.round(monthlyTaxes) },
    { name: 'Expenses', value: Math.round(totalMonthlyExpenses) },
    { name: 'Invested', value: Math.round(monthlyInvestment) },
    { name: 'Remaining', value: Math.max(0, Math.round(monthlySurplus - monthlyInvestment)) },
  ].filter(d => d.value > 0);

  const expenseBreakdown = [
    { name: 'Housing', value: parseFloat(expenseData.housing) || 0 },
    { name: 'Utilities', value: parseFloat(expenseData.utilities) || 0 },
    { name: 'Groceries', value: parseFloat(expenseData.groceries) || 0 },
    { name: 'Transport', value: parseFloat(expenseData.transportation) || 0 },
    { name: 'Insurance', value: parseFloat(expenseData.insurance) || 0 },
    { name: 'Healthcare', value: parseFloat(expenseData.healthcare) || 0 },
    { name: 'Subscriptions', value: parseFloat(expenseData.subscriptions) || 0 },
    { name: 'Dining', value: parseFloat(expenseData.dining) || 0 },
    { name: 'Entertainment', value: parseFloat(expenseData.entertainment) || 0 },
    { name: 'Clothing', value: parseFloat(expenseData.clothing) || 0 },
    { name: 'Education', value: parseFloat(expenseData.education) || 0 },
    { name: 'Personal Care', value: parseFloat(expenseData.personalCare) || 0 },
    { name: 'Childcare', value: parseFloat(expenseData.childcare) || 0 },
    { name: 'Pets', value: parseFloat(expenseData.petCare) || 0 },
    { name: 'Other', value: parseFloat(expenseData.other) || 0 },
  ].filter(d => d.value > 0);

  const monthlyBar = [
    { name: 'Gross Income', value: Math.round(totalMonthlyIncome), fill: '#60a5fa' },
    { name: 'Net Income', value: Math.round(netMonthlyIncome), fill: '#34d399' },
    { name: 'Expenses', value: Math.round(totalMonthlyExpenses), fill: '#f87171' },
    { name: 'Taxes', value: Math.round(monthlyTaxes), fill: '#fbbf24' },
    { name: 'Invested', value: Math.round(monthlyInvestment), fill: '#a78bfa' },
    { name: 'Surplus', value: Math.round(monthlySurplus), fill: '#2dd4bf' },
  ];

  return (
    <div>
      <div className="dashboard-kpis">
        {[
          { label: 'Gross Income', value: fmt$(totalMonthlyIncome), color: 'blue', sub: 'per month' },
          { label: 'Net Take-Home', value: fmt$(netMonthlyIncome), color: 'green', sub: `after ${taxRate.toFixed(1)}% taxes` },
          { label: 'Total Expenses', value: fmt$(totalMonthlyExpenses), color: 'red', sub: 'per month' },
          { label: 'Monthly Surplus', value: fmt$(monthlySurplus), color: monthlySurplus >= 0 ? 'teal' : 'red', sub: 'income minus expenses & taxes' },
          { label: 'Monthly Invested', value: fmt$(monthlyInvestment), color: 'purple', sub: `${investPct}% of net income` },
          { label: 'Future Value', value: fmt$(futureValue), color: 'gold', sub: `in ${years} yrs at ${arr}% ARR` },
        ].map(({ label, value, color, sub }) => (
          <div key={label} className={`kpi-card kpi-${color}`}>
            <span className="kpi-label">{label}</span>
            <span className="kpi-value">{value}</span>
            <span className="kpi-sub">{sub}</span>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        {incomeBreakdown.length > 0 && (
          <div className="section-card">
            <h2 className="section-title">💵 Income Allocation</h2>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={incomeBreakdown} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  {incomeBreakdown.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => fmt$(v)} contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {expenseBreakdown.length > 0 && (
          <div className="section-card">
            <h2 className="section-title">💸 Expense Breakdown</h2>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={expenseBreakdown} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value">
                  {expenseBreakdown.map((_, i) => <Cell key={i} fill={COLORS[(i + 4) % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => fmt$(v)} contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
                <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {totalMonthlyIncome > 0 && (
        <div className="section-card">
          <h2 className="section-title">📊 Monthly Financial Overview</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyBar} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={v => `$${v >= 1000 ? `${(v / 1000).toFixed(0)}K` : v}`} />
              <Tooltip formatter={(v) => fmt$(v)} contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {monthlyBar.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="section-card">
        <h2 className="section-title">📋 Financial Summary</h2>
        <div className="summary-table">
          <div className="summary-section">
            <h3 className="summary-section-title">Income & Taxes</h3>
            <div className="summary-row"><span>Gross Monthly Income</span><span className="pos">{fmt$(totalMonthlyIncome)}</span></div>
            <div className="summary-row"><span>Total Withholdings ({taxRate.toFixed(1)}%)</span><span className="neg">-{fmt$(monthlyTaxes)}</span></div>
            <div className="summary-row bold"><span>Net Monthly Income</span><span className="pos">{fmt$(netMonthlyIncome)}</span></div>
          </div>
          <div className="summary-divider" />
          <div className="summary-section">
            <h3 className="summary-section-title">Expenses & Cash Flow</h3>
            <div className="summary-row"><span>Total Monthly Expenses</span><span className="neg">-{fmt$(totalMonthlyExpenses)}</span></div>
            <div className="summary-row"><span>Monthly Investment</span><span className="purple-txt">-{fmt$(monthlyInvestment)}</span></div>
            <div className="summary-row bold"><span>Monthly Surplus</span><span className={monthlySurplus >= 0 ? 'pos' : 'neg'}>{fmt$(monthlySurplus)}</span></div>
            <div className="summary-row"><span>Savings Rate</span><span className="pos">{savingsRate}%</span></div>
          </div>
          <div className="summary-divider" />
          <div className="summary-section">
            <h3 className="summary-section-title">Investment Projection</h3>
            <div className="summary-row"><span>Monthly Investment</span><span className="pos">{fmt$(monthlyInvestment)}</span></div>
            <div className="summary-row"><span>Total Contributions ({years} yrs)</span><span>{fmt$(totalContributions)}</span></div>
            <div className="summary-row"><span>Compound Gains ({arr}% ARR)</span><span className="pos">+{fmt$(totalGains)}</span></div>
            <div className="summary-row bold"><span>Future Portfolio Value</span><span className="accent">{fmt$(futureValue)}</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
