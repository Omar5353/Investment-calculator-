import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function buildGrowthData(monthlyInvestment, arrRate, years, freq) {
  const periodsPerYear = freq === 'daily' ? 365 : freq === 'weekly' ? 52 : freq === 'monthly' ? 12 : freq === 'quarterly' ? 4 : 1;
  const ratePerPeriod = arrRate / 100 / periodsPerYear;
  const data = [];
  for (let y = 0; y <= years; y++) {
    const n = y * periodsPerYear;
    const fv = monthlyInvestment > 0 && arrRate > 0
      ? monthlyInvestment * (periodsPerYear / 12) * ((Math.pow(1 + ratePerPeriod, n) - 1) / ratePerPeriod)
      : monthlyInvestment * 12 * y;
    const contributions = monthlyInvestment * 12 * y;
    data.push({
      year: y,
      'Portfolio Value': Math.round(fv),
      'Total Contributed': Math.round(contributions),
      'Investment Gains': Math.round(Math.max(0, fv - contributions)),
    });
  }
  return data;
}

const fmt = v => `$${v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(0) + 'K' : v}`;

export default function InvestmentSection({ data, onChange, summary }) {
  const { monthlyInvestment, futureValue, totalContributions, totalGains, netMonthlyIncome, investPct, arr, years } = summary;

  const chartData = buildGrowthData(
    monthlyInvestment,
    arr,
    Math.max(years, 1),
    data.compoundFrequency
  );

  const milestones = [100000, 250000, 500000, 1000000, 2000000, 5000000].filter(m => m <= futureValue * 1.5);

  return (
    <div>
      <div className="section-card">
        <h2 className="section-title">📈 Investment Settings</h2>
        <p className="section-subtitle">Configure how much of your net income to invest and your expected returns</p>

        <div className="fields-grid">
          <div className="field-group">
            <label className="field-label">Investment % of Net Income</label>
            <p className="field-hint">
              Net take-home: ${netMonthlyIncome.toLocaleString('en-US', { maximumFractionDigits: 0 })}/mo
            </p>
            <div className="field-input-wrap">
              <input
                type="number"
                min="0"
                max="100"
                step="0.5"
                className="field-input pct"
                placeholder="15"
                value={data.investmentPercentage}
                onChange={e => onChange('investmentPercentage', e.target.value)}
              />
              <span className="percent-suffix">%</span>
            </div>
          </div>

          <div className="field-group">
            <label className="field-label">Annual Rate of Return (ARR)</label>
            <p className="field-hint">S&P 500 avg ~10%, Bonds ~4-5%</p>
            <div className="field-input-wrap">
              <input
                type="number"
                min="0"
                max="50"
                step="0.1"
                className="field-input pct"
                placeholder="7"
                value={data.annualReturnRate}
                onChange={e => onChange('annualReturnRate', e.target.value)}
              />
              <span className="percent-suffix">%</span>
            </div>
          </div>

          <div className="field-group">
            <label className="field-label">Investment Duration</label>
            <p className="field-hint">How many years to invest</p>
            <div className="field-input-wrap">
              <input
                type="number"
                min="1"
                max="60"
                step="1"
                className="field-input"
                placeholder="30"
                value={data.years}
                onChange={e => onChange('years', e.target.value)}
                style={{ paddingLeft: '12px' }}
              />
              <span className="percent-suffix">yrs</span>
            </div>
          </div>

          <div className="field-group">
            <label className="field-label">Compounding Frequency</label>
            <p className="field-hint">How often returns compound</p>
            <select
              className="select-input"
              value={data.compoundFrequency}
              onChange={e => onChange('compoundFrequency', e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="annually">Annually</option>
            </select>
          </div>
        </div>
      </div>

      {monthlyInvestment > 0 && (
        <>
          <div className="results-grid">
            <div className="result-card blue">
              <span className="result-label">Monthly Investment</span>
              <span className="result-value">${monthlyInvestment.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              <span className="result-sub">{investPct}% of net income</span>
            </div>
            <div className="result-card green">
              <span className="result-label">Total Contributions</span>
              <span className="result-value">${totalContributions.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              <span className="result-sub">Over {years} years</span>
            </div>
            <div className="result-card purple">
              <span className="result-label">Investment Gains</span>
              <span className="result-value">${totalGains.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              <span className="result-sub">Compound interest earned</span>
            </div>
            <div className="result-card gold">
              <span className="result-label">Future Portfolio Value</span>
              <span className="result-value">${futureValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              <span className="result-sub">In {years} years at {arr}% ARR</span>
            </div>
          </div>

          {chartData.length > 1 && (
            <div className="section-card">
              <h2 className="section-title">📊 Portfolio Growth Over Time</h2>
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                  <defs>
                    <linearGradient id="colorPV" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorContrib" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#34d399" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
                  <XAxis dataKey="year" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} label={{ value: 'Year', position: 'insideBottom', fill: '#64748b', dy: 15 }} />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={fmt} width={70} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                    labelStyle={{ color: '#94a3b8' }}
                    formatter={(v, n) => [`$${v.toLocaleString()}`, n]}
                  />
                  <Legend wrapperStyle={{ color: '#94a3b8', paddingTop: 16 }} />
                  <Area type="monotone" dataKey="Portfolio Value" stroke="#60a5fa" strokeWidth={2.5} fill="url(#colorPV)" dot={false} />
                  <Area type="monotone" dataKey="Total Contributed" stroke="#34d399" strokeWidth={2} fill="url(#colorContrib)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {milestones.length > 0 && (
            <div className="section-card">
              <h2 className="section-title">🎯 Milestones</h2>
              <div className="milestones-grid">
                {milestones.map(m => {
                  const periodsPerYear = data.compoundFrequency === 'daily' ? 365 : data.compoundFrequency === 'weekly' ? 52 : data.compoundFrequency === 'monthly' ? 12 : data.compoundFrequency === 'quarterly' ? 4 : 1;
                  const r = arr / 100 / periodsPerYear;
                  const pmt = monthlyInvestment * (periodsPerYear / 12);
                  let yearsToMilestone = null;
                  if (r > 0 && pmt > 0) {
                    const n = Math.log(1 + (m * r) / pmt) / Math.log(1 + r);
                    yearsToMilestone = n / periodsPerYear;
                  } else if (pmt > 0) {
                    yearsToMilestone = m / (pmt * periodsPerYear);
                  }
                  const reached = yearsToMilestone && yearsToMilestone <= years;
                  return (
                    <div key={m} className={`milestone-item${reached ? ' reached' : ''}`}>
                      <span className="milestone-amount">${m >= 1e6 ? `${m / 1e6}M` : `${m / 1e3}K`}</span>
                      {yearsToMilestone
                        ? <span className="milestone-year">{reached ? '✓ ' : '~'}{yearsToMilestone.toFixed(1)} yrs</span>
                        : <span className="milestone-year">—</span>
                      }
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
