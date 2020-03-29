# Scripts

Code to preprocess and analyze COVID-19 data. The preprocessing is implemented
in Python code, while the analysis part has some part in R and other in Python.

The bash scripts are used to automate the preprocessing and analysis in order
to be performed every day at a specific hour. In particular:

- **update_dataset.sh:** Download the new data from all the data sources
and preprocess it.

- **download_data.sh:** Helper script to download data from a specific data source.

- **update_analysis.sh:** Update the results with the new data.