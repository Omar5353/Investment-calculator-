import React from 'react';

const INCOME_FIELDS = [
  { key: 'monthlySalary', label: 'Monthly Salary / Wages' },
  { key: 'freelance', label: 'Freelance / Side Income' },
  { key: 'rental', label: 'Rental Income' },
  { key: 'dividends', label: 'Dividends & Interest' },
  { key: 'other', label: 'Other Income' },
];

export default function IncomeSection({ data, onChange }) {
  const total = Object.values(data).reduce((s, v) => s + (parseFloat(v) || 0), 0);

  return (
    <div>
      <div className="section-card">
        <h2 className="section-title">💰 Monthly Income Sources</h2>
        <p className="section-subtitle">Enter all monthly income sources (gross, before taxes)</p>
        <div className="fields-grid">
          {INCOME_FIELDS.map(({ key, label }) => (
            <div className="field-group" key={key}>
              <label className="field-label">{label}</label>
              <div className="field-input-wrap">
                <span className="currency-prefix">$</span>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className="field-input"
                  placeholder="0.00"
                  value={data[key]}
                  onChange={e => onChange(key, e.target.value)}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="section-total">
          <span className="section-total-label">Total Monthly Gross Income</span>
          <span className="section-total-value">
            ${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      <div className="info-card">
        <h3 className="info-title">💡 Tips</h3>
        <ul className="info-list">
          <li>Enter gross (pre-tax) income — taxes are handled in the Taxes tab.</li>
          <li>For variable income, use your average monthly amount.</li>
          <li>Include all recurring income streams for the most accurate picture.</li>
        </ul>
      </div>
    </div>
  );
}
