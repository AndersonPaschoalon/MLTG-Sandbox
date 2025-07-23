## ✅ How to Add a New Analysis Module in `trace_analyzer`

This guide shows how to implement a **new metric analysis + its plot**, and **register** both in the system. The framework is built with **separation of concerns** in mind.

---

### 🔧 1. Register the Metric Function (Analysis)

For each new metric to be measured, register it at `trace_analyzer/registers/analysis.py`:

```python
# File: trace_analyzer/registers/analysis.py
def register_all_analysis():
```

Add:

```python
AnalysisRegistry.register(
    name="hurst_periodogram",                          # Unique ID
    display_name="Hurst Periodogram Analysis",         # Human-readable name
    mem_attribute="hurstperiodogramdata_target",       # Atribute used internally to store the tuple (csv_file, target)
    csv_prefix="hurst_periodogram",                    # Prefix for CSV/plot file names
    metric_fn=metrics_scaling.calc_periodogram_as_df,  # Analysis logic function
    requires_min_time=False,                           # Set True if time alignment is required: if time scale needs to be truncated by the min maximum time. 
)
```

---

### 🧠 2. Implement the Metric Function

Once the new metric have been registered, you must implement the metric function. Place it inside a file at `trace_analyzer/metrics/`. The file must group all related metrics together. 

#### 🔹 Signature

```python
def your_analysis_function(
    ac: AlchemyConnector,
    flowID: int = 0,
    ...
) -> pd.DataFrame:
```

In this example we implement the periodogram metric as part of the scalling metrics:

```python
# File: trace_analyzer/metrics/scaling.py
def calc_periodogram_as_df(
    ac,
    flowID: int = 0,
    aggregation_levels: list = [1, 5, 10, 50, 100, 500, 1000],
    base_bin_width: float = 0.01,
) -> pd.DataFrame:
```

#### 🔹 Requirements

* **Strict signature**: Must accept at least `ac` and `flowID`, as mandatory parameters. Others parameters must have default values.
* **Returns**: A `pandas.DataFrame`. If the analysis does have many levels, the results must be  **stacked** in the output Dataframe (e.g., R/S, periodogram). This dataframe will be saved as a `csv` file by the framework.
* All logic for data extraction, transformation, and calculation must be **contained inside this function**.


➡️ Framework will automatically:

* Call this function once per experiment, for each target.
* Write results to CSV using `csv_prefix`, followed by the right target name.

---

### 📌 3. Register the Plot Function

As we did fot the analysis, we must register each new plot. There is no `1-1` requirement here. For a given set of analisis, you may implement as many plots you want. The oposite is true as well, you may implement a single plot using many analysis data. You must register the new plot in this file `trace_analyzer/registers/plots.py`:

```python
# File: trace_analyzer/registers/plots.py
def register_all_plotters():
```

In the example, we show how the periodogram was registered:

```python
import trace_analyzer.plotter.plotters.scaling as pltscl


PlotRegistry.register(
    name="hurst_periodogram",                          # Must match analysis name
    display_name="Periodogram Analysis",               # For CLI/report use
    plot_fn=pltscl.plot_periodogram_analysis,          # Calls the periodogram plotter
)
```

---

### 🎨 4. Implement the Plotter

Now, you must implement the plotter you have declared in the register. 

#### 🔹 Signature

```python
def plot_myplotname(target_list=None) -> list[str]:
```

#### 🔹 Responsibilities

* Fetches the target-specific DataFrames using the correct `mem_attribute`.
* Calls a generic **plot function** with each individual DataFrame (or df\_map).
* Generates one or more `.png` and `.csv` files and returns the paths.

Is advided to group all related plots in the same group. In the example we are using (periodogram), it is grouped as one of the scaling plots, into `scaling.py`.

```python
# File: trace_analyzer/plotter/plotters/scaling.py

def plot_periodogram_analysis(target_list=None):
```

To access the right analysis data to be plotted, you should use the following elements:
* `mem.<analysis_name>_df_map`: this will contain a dataframe map of all targets related with the giving analysis name (registered in the first step);
* `data_loader.filter_df_map_by_target()` if the dataframes does not need to have time alignment, or `data_loader.prepare_distribution_data()` owtherwise;
* If time alignment is need, you also will have to pass the attribute `mem.<analysis_name>_min_time_max` to `data_loader.prepare_distribution_data()`, and the column name of the dataframe where the time stamp is located.
* Both functions  `data_loader.filter_df_map_by_target()`  and `data_loader.prepare_distribution_data()` will return the map of dataframes that will be plotted, and the list of targets.

To generate the name of the plot, you must use the attibutte/method: `mem.pnf.mkname()`. Pass a single labal to it to make plot by target, or pass the complete lsit to plot for all targets at the same time.

Example:

```python
def plot_periodogram_analysis(target_list=None):
    df_map = data_loader.filter_df_map_by_target(mem.hurstperiodogramdata_target, target_list)
    saved = []

    for label, df in df_map.items():
        filename = mem.pnf.mkname("hurst_periodogram", [label])
        out = plot_functions.plot_scatter(
            df=df,
            x_column="log10_frequency",
            y_column="log10_power",
            xlabel="log10(Frequency)",
            ylabel="log10(Periodogram Power)",
            title=f"Periodogram - {label}",
            save_path_base=filename,
            loglog=True,
        )
        saved.extend(out)

    return saved
```
#### 🔹 Behavior

* Receives all plotting parameters explicitly.
* If plotting multiple targets together: receives `df_map: dict[str, pd.DataFrame]`.
* If plotting one per target: receives `df: pd.DataFrame`.
* **Saves both PNG and CSV** files with matching base names.

---

### 🧭 Rule of Thumb: Plotting Decision

| Target Behavior         | Plot Signature Input              | Who Decides?         |
| ----------------------- | --------------------------------- | -------------------- |
| All targets in 1 figure | `df_map: dict[str, pd.DataFrame]` | The plotter function |
| Each target gets a plot | `df: pd.DataFrame` per iteration  | The plotter function |


---

### 🛠 5. Implement the Generic Plot Function (if needed)

Inside the logic of the plotter, is advised to use one of the available plot functions, and to implement a new expleriment agnostic plot function. It most receive as parameter a DataFrame (for plots of single target) of a map of dataframes (for plots of many targets):

```python
# File: trace_analyzer/plotter/functions/plot_functions.py
```

Signature:

```python
def plot_scatter(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    xlabel: str,
    ylabel: str,
    title: str,
    save_path_base: str,
    loglog: bool = False,
) -> list[str]:
```

This function MUST:

* Plot the data as a scatter
* Apply log scales if needed
* Save both PNG and CSV with matching filenames

