import React from 'react';

const TAX_FIELDS = [
  { key: 'federalTaxRate', label: 'Federal Income Tax Rate', hint: 'e.g. 22 for 22%' },
  { key: 'stateTaxRate', label: 'State Income Tax Rate', hint: 'e.g. 5 for 5%' },
  { key: 'socialSecurity', label: 'Social Security (OASDI)', hint: 'Default: 6.2%' },
  { key: 'medicare', label: 'Medicare (FICA)', hint: 'Default: 1.45%' },
  { key: 'stateDisability', label: 'State Disability Insurance', hint: 'e.g. 0.9%' },
  { key: 'otherWithholding', label: 'Other Withholdings', hint: 'HSA, 401k, etc. %' },
];

const FEDERAL_BRACKETS_2024 = [
  { min: 0, max: 11600, rate: 10 },
  { min: 11600, max: 47150, rate: 12 },
  { min: 47150, max: 100525, rate: 22 },
  { min: 100525, max: 191950, rate: 24 },
  { min: 191950, max: 243725, rate: 32 },
  { min: 243725, max: 609350, rate: 35 },
  { min: 609350, max: Infinity, rate: 37 },
];

export default function TaxesSection({ data, onChange, totalIncome }) {
  const annualIncome = totalIncome * 12;

  const suggestedFederal = (() => {
    if (!annualIncome) return 0;
    let tax = 0;
    for (const b of FEDERAL_BRACKETS_2024) {
      if (annualIncome > b.min) {
        const taxable = Math.min(annualIncome, b.max) - b.min;
        tax += taxable * (b.rate / 100);
      }
    }
    return ((tax / annualIncome) * 100).toFixed(1);
  })();

  const totalRate = Object.values(data).reduce((s, v) => s + (parseFloat(v) || 0), 0);
  const monthlyTax = totalIncome * (totalRate / 100);

  return (
    <div>
      {annualIncome > 0 && (
        <div className="info-card accent-blue">
          <h3 className="info-title">📋 2024 Federal Tax Bracket Estimate</h3>
          <p className="info-text">
            Based on ${annualIncome.toLocaleString()} annual income, your estimated effective federal tax rate is approximately{' '}
            <strong style={{ color: '#60a5fa' }}>{suggestedFederal}%</strong>. Enter this in the Federal Tax Rate field below.
          </p>
          <div className="brackets-grid">
            {FEDERAL_BRACKETS_2024.map((b, i) => (
              <div key={i} className={`bracket-item${annualIncome > b.min ? ' active' : ''}`}>
                <span className="bracket-rate">{b.rate}%</span>
                <span className="bracket-range">
                  ${b.min.toLocaleString()}
                  {b.max === Infinity ? '+' : ` – $${b.max.toLocaleString()}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="section-card">
        <h2 className="section-title">🏛️ Taxes & Withholdings</h2>
        <p className="section-subtitle">Enter percentage rates for each withholding (not dollar amounts)</p>
        <div className="fields-grid">
          {TAX_FIELDS.map(({ key, label, hint }) => (
            <div className="field-group" key={key}>
              <label className="field-label">{label}</label>
              <p className="field-hint">{hint}</p>
              <div className="field-input-wrap">
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  className="field-input pct"
                  placeholder="0.0"
                  value={data[key]}
                  onChange={e => onChange(key, e.target.value)}
                />
                <span className="percent-suffix">%</span>
              </div>
            </div>
          ))}
        </div>

        <div className="tax-summary">
          <div className="tax-summary-row">
            <span>Total Withholding Rate</span>
            <span className="highlight-red">{totalRate.toFixed(2)}%</span>
          </div>
          <div className="tax-summary-row">
            <span>Monthly Taxes (on ${totalIncome.toLocaleString()})</span>
            <span className="highlight-red">
              -${monthlyTax.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <div className="tax-summary-row highlight-row">
            <span>Monthly Net Take-Home</span>
            <span className="highlight-green">
              ${(totalIncome - monthlyTax).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
