# Description

This project includes a set of Python classes designed to analyze chromatogram data, identify peaks, calculate elution volumes, and visualize the results. The core functionality is encapsulated in two main classes: ChromatogramRun and Peak.

# Classes and Methods

### ChromatogramRun

Responsible for loading chromatogram data from a file, finding peaks, and plotting the chromatogram.

`find_peaks()`: Identifies peaks in the chromatogram data based on specified criteria.
`plot()`: Plots the chromatogram and optionally displays peak widths and elution volumes.
`total_elution_volume`: The total elution volume of all peaks in the chromatogram.

### Peak

Represents a single peak in the chromatogram, including its properties and methods to visualize and integrate the peak.

`plot()`: Plots the peak against the full chromatogram data.
`integrate()`: Calculates the elution volume of the peak using Simpson method.

### How to Use

##### Set Up Your Environment

```bash
python -m venv .venv
```

Install required packages:

```bash
pip install -r requirements.txt
```

##### Prepare Your Data

Place your chromatogram data file(s) in a known directory. Data files should be formatted according to the expectations of ChromatogramRun.

##### Analyze Your Data

Instantiate a `ChromatogramRun` with the path to your data file.
Use the `find_peaks()` method to identify peaks.
Plot the chromatogram and peaks using the `plot()` method.
View the total elution volume via the `total_elution_volume` property.

### Running the Main Script

The main script demonstrates how to use the `ChromatogramRun` class to load data, find peaks, and visualize the results.

To run the main script:

```bash
python main.py
```

### MacOS Users:

    You may need to replace all python commands with python3.
