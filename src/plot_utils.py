import pandas as pd
import matplotlib.pyplot as plt

def load_slr_data(file_path: str, sheet_name: str = "Total") -> pd.DataFrame:
    """
    Load Sea Level Rise data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to load.
        
    Returns:
        pd.DataFrame: Loaded data.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)

def extract_scenario_data(df: pd.DataFrame, scenario: str, quantiles: list) -> dict:
    """
    Extract data for a given scenario and specific quantiles.
    
    Args:
        df (pd.DataFrame): The full SLR dataset.
        scenario (str): Scenario name (e.g., 'ssp126').
        quantiles (list): List of quantiles to extract (e.g., [0.17, 0.5, 0.83]).
        
    Returns:
        dict: A dictionary mapping each quantile to a pandas Series (index=years, values=SLR).
    """
    df_scenario = df[df['scenario'] == scenario].copy()
    
    # We want years from 2020 to 2100
    years = [str(y) for y in range(2020, 2110, 10)]
    
    scenario_data = {}
    for q in quantiles:
        q_row = df_scenario[df_scenario['quantile'] == q]
        if not q_row.empty:
            q_values = q_row[years].iloc[0].astype(float)
            scenario_data[q] = q_values
            
    return scenario_data

def plot_slr_projections(df: pd.DataFrame, scenarios_list: list, colors: dict, title: str = "SLR Projections (2020-2100)"):
    """
    Plot the median SLR and uncertainty bands for various scenarios.
    
    Args:
        df (pd.DataFrame): The dataset containing the SLR data.
        scenarios_list (list): Scenarios to plot (e.g., ['ssp126', 'ssp245', 'ssp370', 'ssp585']).
        colors (dict): Mapping scenario strings to colors (e.g., {'ssp126': 'blue', ...}).
        title (str): Title for the plot.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = range(2020, 2110, 10)
    # Filter years cols only up to 2100. Assume decades present in Excel (2020, 2030...2100)
    year_cols = [col for col in df.columns if isinstance(col, (int, str)) and str(col).isdigit() and 2020 <= int(col) <= 2100]
    years_int = [int(y) for y in year_cols]
    
    if 'confidence' in df.columns:
        df = df[df['confidence'] == 'medium']
        
    for scenario in scenarios_list:
        df_sc = df[df['scenario'] == scenario]
        if df_sc.empty:
            continue
            
        color = colors.get(scenario, 'black')
        
        try:
            val_050 = df_sc[df_sc['quantile'] == 0.5][year_cols].iloc[0].astype(float).values
            val_017 = df_sc[df_sc['quantile'] == 0.17][year_cols].iloc[0].astype(float).values
            val_083 = df_sc[df_sc['quantile'] == 0.83][year_cols].iloc[0].astype(float).values
        except IndexError:
            # skip if a quantile is missing
            continue

        # Plot median line
        label = f"{scenario.upper()} - Median (0.50)"
        ax.plot(years_int, val_050, label=label, linewidth=2, color=color)
        
        # Fill uncertainty band
        ax.fill_between(years_int, val_017, val_083, alpha=0.2, color=color, label='_nolegend_')

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Sea Level Rise (meters)")
    ax.set_xlim(2020, 2100)
    ax.grid(alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()
