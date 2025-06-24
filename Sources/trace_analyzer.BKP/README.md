# ✅ **How to Add a New Analysis to the Pipeline**

The purpose of this tutorial is to explain how to add new analyses to the `trace_analyzer` pipeline. We will use the addition of Wavelet Multiresolution Energy Analysis (WMEA) as an example.

---

## ✅ **Overview of the Pipeline Steps**

1. **Register** the analysis in the environment (`core.py`).
2. **Analyze and export** the analysis as a CSV (`analyzer.py`).
3. **Load** the CSV for later plotting (`data_loader.py`).
4. **Implement metric extraction** (`metrics_estimator.py`) — already done!
5. **Add plotting** capabilities (`plot_functions.py` + `plotter.py`).
6. **Run the complete cycle**.

---

## ✅ **1. Register Analysis in `core.py`**

First, in `analysis_data_name_formatter.py`, add a constant to represent the wavelet analysis. This will be used as the prefix for the CSV file used to store the data.

```python
class AnalysisDataNameFormatter(ReprMixin):
    ...
    
    # Analysis identifiers (add more as needed)
    
    WAVELET = "wavelet"
```

Then, in `load_env()`, there is a section where **all analysis types** are registered to load their corresponding CSVs.

Each entry is a **tuple**:

```python
(<ANALYSIS_IDENTIFIER>, <mem_attribute_name>)
```

For Wavelet, add:

```python
data_types = [
    (ADNF.BW_PPS_FPS, "bwdata_target"),
    (ADNF.INTERARRIVAL, "interdata_target"),
    (ADNF.BURST_DURATIONS, "burstdurdata_target"),
    (ADNF.BURST_INTERVALS, "burstinterdata_target"),
    (ADNF.BURST_SIZES, "burstsizesdata_target"),
    (ADNF.WAVELET, "waveletdata_target"),  # ✅ <- Add this!
]
```

This ensures that after `load_env()` is called, `mem.waveletdata_target` is populated with all file paths and target names for wavelet CSVs.

---

## ✅ **2. Analyze and Export to CSV in `analyzer.py`**

Now edit the function `analyze_experiment_and_store()` in `analyzer.py`.

### ✔️ Add an internal function

Inside `analyze_experiment_and_store()`, add an internal function responsible for:

* Calling the metric estimator responsible for extracting raw data from the database, processing it, and transforming it into a DataFrame (step #4);
* Generating a file name for the calculated data using the `mem.anf` object;
* Saving the data as a CSV file.

```python
def wavelet_analysis(target: str, ac: AlchemyConnector):
    """
    Perform wavelet analysis for given trace, export to CSV.
    """
    df = metrics_estimator.calc_wavelet_as_df(ac)
    csv_file = mem.anf.mknameext(ADNF.WAVELET, target, "csv")
    df.to_csv(csv_file, index=False)
    return csv_file
```

### ✔️ Integrate the function into the main loop of `analyze_experiment_and_store()`:

```python
for trace, target in mem.traces_target:
    print(f"Loading DB connector for trace {trace}")
    ac: AlchemyConnector = mem.sniffer.flowdb_connector(trace)
    
    bw_pps_fps(target, ac)
    interarrival(target, ac)
    burst_metrics(target, ac)
    
    wavelet_analysis(target, ac)  # ✅ <- Add here!
```

**What happens:**

* For each trace and target, we compute the wavelet features.
* We store them as `<experiment_dir>/analysis/wavelet.<target>.csv`.

---

## ✅ **3. Load the Wavelet Data in `data_loader.py`**

In `load_stored_analysis_data()` add:

```python
mem.wavelet_df_map = _load_data_map(mem.waveletdata_target, target_list)
```

Now, after running `data_loader.load_stored_analysis_data()`, we can access the wavelet data using:

```python
mem.wavelet_df_map  # -> {target: DataFrame}
```

This is critical because all plot functions use these pre-loaded maps.

For plots where the **minimum of the maximum time** is needed (e.g., when we need all time series to have the same time range), we can use the utility function `_load_data_with_min_time()`:

```python
mem.inter_df_map, mem.inter_min_time_max = _load_data_with_min_time(
    mem.interdata_target, target_list, "time"
)
```

In this example the function returns two values:

* The DataFrame map;
* The minimum value of the maximum "time" column across all loaded DataFrames.

> **Note:** Any variable may be stored in the `mem` object. The purpose of this pipeline is to normalize the naming convention across all steps. That being said, take care when setting new variables, like `mem.inter_df_map` and `mem.inter_min_time_max`.
> * Ensure names do not conflict — if the same name is added twice, it will be overwritten, and the pipeline will break.
> * Follow naming conventions: for instance, DataFrame maps should end with the `df_map` suffix. This reduces the chance of conflicts.

---

## ✅ **4. Metric Extraction in `metrics_estimator.py`**

Here you must implement a function in `metrics_estimator.py`.

This function will be called by `analyze_experiment_and_store()` and will be responsible for **loading the data** and **executing the actual computation** of the desired metric.

You don’t need to worry about connecting to the *right* database — the pipeline does that for you.

For Wavelet Multiresolution Energy Analysis we have this function:

```python
def calc_wavelet_as_df(ac: AlchemyConnector, ...) -> pd.DataFrame:
```

It:

* Loads packets from DB;
* Bins them into time windows;
* Applies Wavelet Transform;
* Returns a DataFrame like:

```
scale, log2_energy, energy_abs
0,     10.5,        1200.0
1,     8.2,         500.0
...
```

---

## ✅ **5. Add Plot Functionality**

### ✔️ In `plot_functions.py`: Add or reuse a generic plotting function:

Since the wavelet plot is a **multiline plot** of `log2_energy` over `scale` for different targets, we can use:

```python
def plot_multiline_metric(df_map, x_column, y_column, title, xlabel, ylabel, save_path_base) -> str
```

If none of the available plotting functions fits the requirements, implement a new one.

Key considerations:

* First argument: A DataFrame dictionary. Each key of the dictionary can be used as a label; the corresponding DataFrame provides the data.
* The function should return the name (or names) of the generated plot files.
* Add any additional options as needed. In `plot_multiline_metric()`, the options represent:

  * `x_column`: DataFrame column for x-axis.
  * `y_column`: DataFrame column for y-axis.
  * `title`: Plot title.
  * `xlabel`: X-axis label.
  * `ylabel`: Y-axis label.
  * `save_path_base`: Output file name (without extension).

---

### ✔️ In `plotter.py`: Wrap it for Wavelet

Finally, wrap it into a new function `plot_wavelet_energy()`:

* Use `data_loader.filter_df_map_by_target()` to select only the DataFrames to be plotted. If `target_list` is empty, all DataFrames will be used.
* Generate the plot file name using `mem.pnf()`.
* Call the appropriate plot function.

```python
def plot_wavelet_energy(target_list=None):
    """
    Plot wavelet multiresolution energy for each target.
    """
    filtered_df_map = data_loader.filter_df_map_by_target(
        mem.wavelet_df_map, target_list or []
    )
    compared_targets = list(filtered_df_map.keys())
    filename = mem.pnf.mkname("wavelet_energy", compared_targets)

    plot_functions.plot_multiline_metric(
        df_map=filtered_df_map,
        x_column="scale",
        y_column="log2_energy",
        title="Wavelet Multiresolution Energy Analysis",
        xlabel="Time Scale j",
        ylabel="log2(Energy(j))",
        save_path_base=filename,
    )
```

Now you can call:

```python
plot_wavelet_energy(target_list=target_list)
```

to generate the wavelet energy plot comparing all selected targets.

---

## ✅ **6. Running the Full Cycle**

```python
# Step 1: Setup experiment
core.create_env("scripts/xml/<experiment-list-config>.xml", "<Experiment-Name>")
analyzer.load_into_snifferdb()
analyzer.analyze_experiment_and_store()

# Step 2: Load data and plot
target_list = []  # Empty → all targets
data_loader.load_stored_analysis_data(target_list=target_list)

plot_wavelet_energy(target_list=target_list)
```

---

## ✅ **7. What You Get**:

✅ All wavelet CSVs saved in `/analysis`.
✅ All wavelet plots saved in `/plot`.
✅ Plots automatically named based on experiment + compared targets.

---

## ✅ **Key Points Recap**

| **Step**               | **Purpose**                                    |
| ---------------------- | ---------------------------------------------- |
| `core.py`              | Register new analysis for environment tracking |
| `analyzer.py`          | Implement computation and CSV export           |
| `data_loader.py`       | Register DataFrame maps for plotting           |
| `metrics_estimator.py` | Extract metrics from DB                        |
| `plot_functions.py`    | Define or reuse plot function                  |
| `plotter.py`           | Add wrapper for user-friendly plotting         |

