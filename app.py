import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shiny import ui, render, App
import locale

locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')

# Function to calculate yearly monetary savings
def calculate_time_saved(data, from_format, to_format, time_type='total'):
    format_idx = {'csv': 0, 'feather': 1, 'parquet': 2}

    from_format_idx = format_idx[from_format]
    to_format_idx = format_idx[to_format]

    if time_type == 'saving':
        time_from = data.loc[from_format_idx, 'save_time']
        time_to = data.loc[to_format_idx, 'save_time']
    elif time_type == 'loading':
        time_from = data.loc[from_format_idx, 'load_time']
        time_to = data.loc[to_format_idx, 'load_time']
    else:
        save_time_from = data.loc[from_format_idx, 'save_time']
        load_time_from = data.loc[from_format_idx, 'load_time']
        save_time_to = data.loc[to_format_idx, 'save_time']
        load_time_to = data.loc[to_format_idx, 'load_time']
        time_from = save_time_from + load_time_from
        time_to = save_time_to + load_time_to

    total_time_saved = time_from - time_to

    return total_time_saved

def calculate_yearly_monetary_savings(data, from_format, to_format, read_per_week, write_per_week, persons=1, daily_wage=0, time_unit='seconds'):
    days_per_week = 7
    weeks_per_year = 52

    read_time_saved = calculate_time_saved(data, from_format, to_format, time_type='loading') * read_per_week
    write_time_saved = calculate_time_saved(data, from_format, to_format, time_type='saving') * write_per_week

    total_time_saved_per_week = read_time_saved + write_time_saved
    total_time_saved_per_year = total_time_saved_per_week * weeks_per_year * persons

    if time_unit == 'minutes':
        total_time_saved_per_year /= 60
    elif time_unit == 'hours':
        total_time_saved_per_year /= 3600

    monetary_savings_per_year = total_time_saved_per_year * daily_wage

    return monetary_savings_per_year

# Create a pandas DataFrame with your data
data = pd.DataFrame({
    'format': ['csv', 'feather', 'parquet'],
    'size_mb': [768.2180, 225.6625, 125.5905],
    'save_ram_delta_mb': [0.950000, 794.471875, 157.387695],
    'save_time': [21.607429, 1.223743, 2.264781],
    'load_ram_delta_mb': [494.735156, 503.852539, 1367.403125],
    'load_time': [7.973257, 0.561361, 0.814259]
})

# Generate data for the plots
reads_range = np.arange(1, 11)  # Number of reads per week from 1 to 10
writes_range = np.arange(1, 11)  # Number of writes per week from 1 to 10
combined_savings_reshaped = np.random.rand(10, 10)  # Replace with your real data

app_ui = ui.page_fixed(
    ui.h2("Interactive Savings Calculator"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("reads_slider", "Number of Reads per Week", 1, 10, value=5, step=1),
            ui.input_slider("writes_slider", "Number of Writes per Week", 1, 10, value=5, step=1),
            ui.input_slider("persons_slider", "Number of People", 1, 20, value=10, step=1),
            ui.input_numeric("wage_input", "Daily Wage (MXN)", value=2000)
        ),
        ui.panel_main(
            ui.output_plot("savings_graph")
        )
    )
)

def server(input, output, session):
    @output
    @render.plot
    def savings_graph():
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        
        # # Get values from inputs
        # reads = input.reads_slider()
        # writes = input.writes_slider()
        # persons = input.persons_slider()
        # wage = input.wage_input()
        
def server(input, output, session):
    @output
    @render.plot
    def savings_graph():
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        
        # Get values from inputs (this part is optional if these values are not used)
        reads = input.reads_slider()
        writes = input.writes_slider()
        persons = input.persons_slider()
        wage = input.wage_input()
        
        # Generate data for the combined savings plot
        combined_savings = []

        for r in reads_range:
            for w in writes_range:
                # Replace the following function call with your real calculation logic
                combined_savings.append(calculate_yearly_monetary_savings(data, 'csv', 'parquet', r, w, persons, wage, 'hours'))

        combined_savings_reshaped = np.array(combined_savings).reshape(len(reads_range), len(writes_range))

        X, Y = np.meshgrid(writes_range, reads_range)
        
        ax.plot_surface(X, Y, combined_savings_reshaped, cmap='viridis')
        
        ax.set_xlabel('Number of Writes')
        ax.set_ylabel('Number of Reads')
        ax.set_zlabel(f'Yearly Monetary Savings (MXN) from {persons} analysts')
        ax.ticklabel_format(style='plain', axis='z', useLocale=True)  # Add thousands separator to y-axis

        
        return fig


app = App(app_ui, server)
