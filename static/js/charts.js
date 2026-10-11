/**
 * FinBuddy - Dashboard Chart.js Integration
 */

function initDashboardCharts(chartConfig) {
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js is not loaded.');
    return;
  }

  // Set Chart.js Defaults
  Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
  Chart.defaults.color = '#64748b';
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';

  // 1. Income vs Expense (Doughnut Chart)
  const incExpCanvas = document.getElementById('incExpChart');
  if (incExpCanvas && chartConfig.incExpData) {
    const total = chartConfig.incExpData.reduce((a, b) => a + b, 0);
    new Chart(incExpCanvas, {
      type: 'doughnut',
      data: {
        labels: chartConfig.incExpLabels || ['Income', 'Expense'],
        datasets: [{
          data: total === 0 ? [1, 0] : chartConfig.incExpData,
          backgroundColor: total === 0 ? ['#e2e8f0', '#cbd5e1'] : ['#10b981', '#f43f5e'],
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 16,
              font: { weight: '600', size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                if (total === 0) return 'No data yet';
                const val = context.raw || 0;
                return ` ${context.label}: $${val.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
              }
            }
          }
        }
      }
    });
  }

  // 2. Monthly Cashflow Trend (Bar Chart)
  const trendCanvas = document.getElementById('cashflowTrendChart');
  if (trendCanvas && chartConfig.monthsLabels) {
    new Chart(trendCanvas, {
      type: 'bar',
      data: {
        labels: chartConfig.monthsLabels,
        datasets: [
          {
            label: 'Income',
            data: chartConfig.monthlyIncome,
            backgroundColor: '#10b981',
            borderRadius: 6,
            maxBarThickness: 24,
          },
          {
            label: 'Expenses',
            data: chartConfig.monthlyExpense,
            backgroundColor: '#f43f5e',
            borderRadius: 6,
            maxBarThickness: 24,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 10,
              usePointStyle: true,
              font: { weight: '600' }
            }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ` ${ctx.dataset.label}: $${(ctx.raw || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: '500' } }
          },
          y: {
            grid: { color: '#f1f5f9' },
            ticks: {
              font: { size: 11 },
              callback: function (val) { return '$' + val.toLocaleString(); }
            }
          }
        }
      }
    });
  }

  // 3. Category Breakdown (Doughnut Chart)
  const categoryCanvas = document.getElementById('categoryBreakdownChart');
  if (categoryCanvas && chartConfig.catLabels && chartConfig.catData) {
    const hasData = chartConfig.catData.length > 0 && chartConfig.catData.some(v => v > 0);
    const vibrantColors = [
      '#0d9488', '#06b6d4', '#3b82f6', '#8b5cf6',
      '#ec4899', '#f59e0b', '#10b981', '#64748b'
    ];

    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: hasData ? chartConfig.catLabels : ['No Expenses Yet'],
        datasets: [{
          data: hasData ? chartConfig.catData : [1],
          backgroundColor: hasData ? vibrantColors.slice(0, chartConfig.catLabels.length) : ['#e2e8f0'],
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              padding: 12,
              font: { size: 11, weight: '500' }
            }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                if (!hasData) return 'No expenses recorded';
                return ` ${ctx.label}: $${(ctx.raw || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
              }
            }
          }
        }
      }
    });
  }
}
