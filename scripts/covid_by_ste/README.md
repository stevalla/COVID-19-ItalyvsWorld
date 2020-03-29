# Python analysis

Simple python project to preprocess and analyse COVID-19 data.

## Python packages

-**data_preparation:** Used to preprocess the data coming from different data
sources and in different formats and aggregate it together. To add a new
dataset you should just create your proper data_preprocessing subclass
and implement all the requested methods (reshape_data, make_consistent, check_data)

-**covid_analysis:** Used to analyse and plot the cleaned data.
