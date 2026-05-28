import React, { useState, useCallback } from 'react';
import IncomeSection from './components/IncomeSection';
import ExpensesSection from './components/ExpensesSection';
import TaxesSection from './components/TaxesSection';
import InvestmentSection from './components/InvestmentSection';
import Dashboard from './components/Dashboard';
import './App.css';

const defaultState = {
  income: {
    monthlySalary: '',
    freelance: '',
    rental: '',
    dividends: '',
    other: '',
  },
  expenses: {
    housing: '',
    utilities: '',
    groceries: '',
    transportation: '',
    insurance: '',
    healthcare: '',
    subscriptions: '',
    dining: '',
    entertainment: '',
    clothing: '',
    education: '',
    personalCare: '',
    childcare: '',
    petCare: '',
    other: '',
  },
  taxes: {
    federalTaxRate: '',
    stateTaxRate: '',
    socialSecurity: '',
    medicare: '',
    stateDisability: '',
    otherWithholding: '',
  },
  investment: {
    investmentPercentage: '',
    annualReturnRate: '',
    years: '',
    compoundFrequency: 'monthly',
  },
};

const TABS = ['Income', 'Expenses', 'Taxes', 'Investment', 'Dashboard'];

export default function App() {
  const [data, setData] = useState(defaultState);
  const [activeTab, setActiveTab] = useState('Income');

  const updateSection = useCallback((section, field, value) => {
    setData(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: value },
    }));
  }, []);

  const totalMonthlyIncome = Object.values(data.income).reduce(
    (sum, v) => sum + (parseFloat(v) || 0), 0
  );

  const totalMonthlyExpenses = Object.values(data.expenses).reduce(
    (sum, v) => sum + (parseFloat(v) || 0), 0
  );

  const taxRate =
    (parseFloat(data.taxes.federalTaxRate) || 0) +
    (parseFloat(data.taxes.stateTaxRate) || 0) +
    (parseFloat(data.taxes.socialSecurity) || 0) +
    (parseFloat(data.taxes.medicare) || 0) +
    (parseFloat(data.taxes.stateDisability) || 0) +
    (parseFloat(data.taxes.otherWithholding) || 0);

  const monthlyTaxes = totalMonthlyIncome * (taxRate / 100);
  const netMonthlyIncome = totalMonthlyIncome - monthlyTaxes;
  const monthlySurplus = netMonthlyIncome - totalMonthlyExpenses;

  const investPct = parseFloat(data.investment.investmentPercentage) || 0;
  const monthlyInvestment = netMonthlyIncome * (investPct / 100);
  const arr = parseFloat(data.investment.annualReturnRate) || 0;
  const years = parseInt(data.investment.years) || 0;
  const freq = data.investment.compoundFrequency;

  const periodsPerYear = freq === 'daily' ? 365 : freq === 'weekly' ? 52 : freq === 'monthly' ? 12 : freq === 'quarterly' ? 4 : 1;
  const ratePerPeriod = arr / 100 / periodsPerYear;
  const totalPeriods = years * periodsPerYear;
  const futureValue = monthlyInvestment > 0 && arr > 0 && years > 0
    ? monthlyInvestment * (periodsPerYear / 12) * ((Math.pow(1 + ratePerPeriod, totalPeriods) - 1) / ratePerPeriod)
    : 0;
  const totalContributions = monthlyInvestment * 12 * years;
  const totalGains = futureValue - totalContributions;

  const summary = {
    totalMonthlyIncome,
    totalMonthlyExpenses,
    monthlyTaxes,
    netMonthlyIncome,
    monthlySurplus,
    monthlyInvestment,
    futureValue,
    totalContributions,
    totalGains,
    taxRate,
    investPct,
    arr,
    years,
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">📊</span>
            Financial Planner & Investment Calculator
          </h1>
          <p className="app-subtitle">Track income, expenses, taxes, and grow your wealth</p>
        </div>
        <div className="quick-stats">
          <div className="quick-stat">
            <span className="qs-label">Net Monthly</span>
            <span className={`qs-value ${netMonthlyIncome >= 0 ? 'positive' : 'negative'}`}>
              ${netMonthlyIncome.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </span>
          </div>
          <div className="quick-stat">
            <span className="qs-label">Monthly Surplus</span>
            <span className={`qs-value ${monthlySurplus >= 0 ? 'positive' : 'negative'}`}>
              ${monthlySurplus.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </span>
          </div>
          <div className="quick-stat">
            <span className="qs-label">Future Value</span>
            <span className="qs-value accent">
              ${futureValue.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </span>
          </div>
        </div>
      </header>

      <nav className="tab-nav">
        {TABS.map(tab => (
          <button
            key={tab}
            className={`tab-btn${activeTab === tab ? ' active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === 'Income' && (
          <IncomeSection data={data.income} onChange={(f, v) => updateSection('income', f, v)} />
        )}
        {activeTab === 'Expenses' && (
          <ExpensesSection data={data.expenses} onChange={(f, v) => updateSection('expenses', f, v)} />
        )}
        {activeTab === 'Taxes' && (
          <TaxesSection data={data.taxes} onChange={(f, v) => updateSection('taxes', f, v)} totalIncome={totalMonthlyIncome} />
        )}
        {activeTab === 'Investment' && (
          <InvestmentSection data={data.investment} onChange={(f, v) => updateSection('investment', f, v)} summary={summary} />
        )}
        {activeTab === 'Dashboard' && (
          <Dashboard summary={summary} incomeData={data.income} expenseData={data.expenses} taxData={data.taxes} investmentData={data.investment} />
        )}
      </main>
    </div>
  );
}
