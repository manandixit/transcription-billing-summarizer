# Transcription Billing & QA Summarizer

This is a Python and Pandas script that merges multiple daily transcription logs, cleans up inconsistent entries, and creates a client-wise billing and accuracy summary.

It is routine to encounter complex, sensitive, oftentimes messy medical/patient data in the healthcare industry that needs handling with care and caution.  I built this utility to combine multiple CSV logs automatically, catch duplicate job entries, handle and flag missing line counts, and calculate total lines, accuracy rates, and billing amounts per client.

## What it does

* **Merges multiple CSV files:** Reads all daily `.csv` log files inside the `sample_logs/` folder and combines them into a single table.
* **Cleans and deduplicates records:** Standardizes client names, flags missing line counts, fills missing numeric values with `0`, and removes duplicate `job_id` entries.
* **Calculates job metrics:** Computes total line charges and weighted percentage accuracy for each client.
* **Exports two CSV reports:** Saves the full cleaned dataset to `merged_cleaned_jobs.csv` and a grouped client summary to `client_billing_summary.csv`.

## Setup and usage

Install Pandas (required):

```bash
pip install -r requirements.txt
```

Run the script from the project folder:

```bash
python summarize_logs.py
```

## Example summary output

From the included sample files in `sample_logs/`, the script generates `client_billing_summary.csv`:

```text
          client_name  total_jobs  missing_line_jobs  total_lines  total_errors  weighted_accuracy_pct  total_billed
City General Hospital           2                  0          410             1                  99.76         39.20
  Metro Health Clinic           2                  0          355             2                  99.44         30.50
 Westside Orthopedics           2                  1          180             0                 100.00         21.60
```

I developed this using Python 3.13 and Pandas on Windows 11.
