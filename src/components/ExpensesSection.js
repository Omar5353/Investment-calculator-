import React from 'react';

const EXPENSE_FIELDS = [
  { key: 'housing', label: 'Housing (Rent/Mortgage)', emoji: '🏠' },
  { key: 'utilities', label: 'Utilities (Electric, Gas, Water)', emoji: '⚡' },
  { key: 'groceries', label: 'Groceries & Food', emoji: '🛒' },
  { key: 'transportation', label: 'Transportation (Car, Gas, Transit)', emoji: '🚗' },
  { key: 'insurance', label: 'Insurance (Auto, Home, Life)', emoji: '🛡️' },
  { key: 'healthcare', label: 'Healthcare & Medical', emoji: '🏥' },
  { key: 'subscriptions', label: 'Subscriptions & Memberships', emoji: '📱' },
  { key: 'dining', label: 'Dining Out & Takeout', emoji: '🍽️' },
  { key: 'entertainment', label: 'Entertainment & Hobbies', emoji: '🎬' },
  { key: 'clothing', label: 'Clothing & Accessories', emoji: '👕' },
  { key: 'education', label: 'Education & Student Loans', emoji: '📚' },
  { key: 'personalCare', label: 'Personal Care & Grooming', emoji: '💇' },
  { key: 'childcare', label: 'Childcare & Education', emoji: '👶' },
  { key: 'petCare', label: 'Pet Care', emoji: '🐾' },
  { key: 'other', label: 'Other Expenses', emoji: '📦' },
];

export default function ExpensesSection({ data, onChange }) {
  const total = Object.values(data).reduce((s, v) => s + (parseFloat(v) || 0), 0);

  const categories = {
    'Essential': ['housing', 'utilities', 'groceries', 'transportation', 'insurance', 'healthcare'],
    'Lifestyle': ['subscriptions', 'dining', 'entertainment', 'clothing'],
    'Family & Personal': ['education', 'personalCare', 'childcare', 'petCare', 'other'],
  };

  return (
    <div>
      {Object.entries(categories).map(([cat, keys]) => {
        const fields = EXPENSE_FIELDS.filter(f => keys.includes(f.key));
        const catTotal = keys.reduce((s, k) => s + (parseFloat(data[k]) || 0), 0);
        return (
          <div className="section-card" key={cat}>
            <h2 className="section-title">{cat} Expenses</h2>
            <div className="fields-grid">
              {fields.map(({ key, label, emoji }) => (
                <div className="field-group" key={key}>
                  <label className="field-label">{emoji} {label}</label>
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
            {catTotal > 0 && (
              <div className="section-total">
                <span className="section-total-label">{cat} Subtotal</span>
                <span className="section-total-value">
                  ${catTotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
            )}
          </div>
        );
      })}

      <div className="section-total-bar">
        <span>Total Monthly Expenses</span>
        <span>${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
      </div>
    </div>
  );
}
