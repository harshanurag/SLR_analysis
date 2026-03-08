import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

text = """\
# IPCC AR6 Sea Level Rise (SLR) Projections Plot (2020-2100)

This notebook loads the local SLR data extracted from `ipcc_ar6_sea_level_projection_25_54.xlsx`.
We plot the median Sea Level Rise (SLR) projections for various scenarios (`ssp126`, `ssp245`, `ssp370`, `ssp585`). 
Then, we plot each scenario individually with its uncertainty band.
"""

code_imports = """\
import pandas as pd
import matplotlib.pyplot as plt

# Setup data path and configurations
file_path = '../data/ipcc_ar6_sea_level_projection_25_54.xlsx'
sheet_name = 'Total'

# Load Full Data
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Quick Look
print(f"Data Loaded: {len(df)} rows.")
df.head(3)
"""

code_settings = """\
scenarios = ['ssp126', 'ssp245', 'ssp370', 'ssp585']
scenario_colors = {
    'ssp126': 'blue',
    'ssp245': 'orange',
    'ssp370': 'red',
    'ssp585': 'purple'
}
years_to_plot = list(range(2020, 2101, 10))

# Filter for medium confidence
if 'confidence' in df.columns:
    df = df[df['confidence'] == 'medium']

import os
os.makedirs('../output', exist_ok=True)
"""

code_plot_all_no_uncertainty = """\
fig, ax = plt.subplots(figsize=(10, 6))

for scenario in scenarios:
    df_sc = df[df['scenario'] == scenario]
    if df_sc.empty:
        continue
        
    color = scenario_colors.get(scenario, 'black')
    
    try:
        val_050 = df_sc[df_sc['quantile'] == 50][years_to_plot].iloc[0].astype(float).values
        ax.plot(years_to_plot, val_050, label=f"{scenario.upper()}", linewidth=2, color=color)
    except IndexError:
        print(f"Missing median data for {scenario}")

ax.set_title("Projected Sea Level Rise (2020-2100) - All Scenarios (Median Only)", fontsize=14)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Sea Level Rise (meters)", fontsize=12)
ax.set_xlim(2020, 2100)
ax.set_ylim(0, 1.2)
from matplotlib.ticker import MultipleLocator
ax.yaxis.set_major_locator(MultipleLocator(0.2))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
ax.grid(alpha=0.3)
ax.legend(loc='upper left')

plt.tight_layout()
plt.savefig('../output/all_scenarios_median.png', dpi=300, bbox_inches='tight')
plt.show()
"""

cells = [
    nbf.v4.new_markdown_cell(text),
    nbf.v4.new_code_cell(code_imports),
    nbf.v4.new_code_cell(code_settings),
    nbf.v4.new_markdown_cell("## All Scenarios Combined"),
    nbf.v4.new_code_cell(code_plot_all_no_uncertainty),
    nbf.v4.new_markdown_cell("## Individual Scenarios with Uncertainty Bands")
]

# Generate a cell for each scenario
for scenario in ['ssp126', 'ssp245', 'ssp370', 'ssp585']:
    code_scenario = f"""\
scenario = '{scenario}'
color = scenario_colors.get(scenario, 'black')
df_sc = df[df['scenario'] == scenario]

fig, ax = plt.subplots(figsize=(8, 5))

try:
    val_050 = df_sc[df_sc['quantile'] == 50][years_to_plot].iloc[0].astype(float).values
    val_017 = df_sc[df_sc['quantile'] == 17][years_to_plot].iloc[0].astype(float).values
    val_083 = df_sc[df_sc['quantile'] == 83][years_to_plot].iloc[0].astype(float).values

    ax.plot(years_to_plot, val_050, label=f"{{scenario.upper()}} (Median)", linewidth=2, color=color)
    ax.fill_between(years_to_plot, val_017, val_083, alpha=0.2, color=color, label='Uncertainty Band (17th-83rd)')
except IndexError:
    print(f"Missing quantile data for {{scenario}}")

ax.set_title(f"Projected Sea Level Rise (2020-2100) - {{scenario.upper()}}", fontsize=14)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Sea Level Rise (meters)", fontsize=12)
ax.set_xlim(2020, 2100)
ax.set_ylim(0, 1.2)
from matplotlib.ticker import MultipleLocator
ax.yaxis.set_major_locator(MultipleLocator(0.2))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
ax.grid(alpha=0.3)
ax.legend(loc='upper left')

plt.tight_layout()
plt.savefig(f'../output/{{scenario.lower()}}_with_uncertainty.png', dpi=300, bbox_inches='tight')
plt.show()
"""
    cells.append(nbf.v4.new_markdown_cell(f"### Scenario: {scenario.upper()}"))
    cells.append(nbf.v4.new_code_cell(code_scenario))

nb['cells'] = cells

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/slr_plot_analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
