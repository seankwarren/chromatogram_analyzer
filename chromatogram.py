from numpy.typing import NDArray
from peak import Peak
from utils import normalize, parse_key_value_pairs
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np
import re

class ChromatogramRun:

    # Default peak finding parameters (see: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html)
    DISTANCE: int = 75 # number of data points between peaks
    MIN_HEIGHT: float = .15 # number of standard deviations above the mean
    MIN_WIDTH: int = 10 # number of data points
    MAX_WIDTH: int = 1000 # number of data points
    RELATIVE_HEIGHT: float = .95 # number between 0 and 1

    # Default integration parameters
    NORMALIZE: bool = False # normalize y values to be >= 0 before peak detection

    # Default plotting parameters
    SHOW_WIDTHS: bool = True # show the widths of the peaks on the plot
    SHOW_ELUSTION_VOLUMES: bool = True # show the integrals of the peaks on the plot

    def __init__(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # split the file into sections based on section titles
                sections = re.split(r'^(.+?:)\n', content, flags=re.MULTILINE)

                self.metadata = {
                    **parse_key_value_pairs(sections[0].strip()),
                    "injection_info": parse_key_value_pairs(sections[2].strip()),
                    "chromatogram_data_info": parse_key_value_pairs(sections[4].strip()),
                    "signal_parameter_info": parse_key_value_pairs(sections[6].strip()),
                }

                self.data = self.parse_chromatogram_data(sections[8].strip())

        except FileNotFoundError:
            print(f"File {filepath} not found.")
            return None

    @staticmethod
    def parse_chromatogram_data(content: str) -> NDArray:
        """
        Parses the chromatogram data from the file content. The data is expected
        to be in a tab-delimited format with columns for time, step, and value.
        'n.a.' values are converted to 0.

        Args:
        - content: The content of the chromatogram data section of the file.

        Returns:
        - A structured NumPy array with columns for time, step, and value.
        """
        lines = content.strip().split("\n")[1:] # skip the header with the column names
        data_tuples = []
        for line in lines:
            columns = line.split('\t')
            if len(columns) == 3:
                time, step, value = columns
                try:
                    step = float(step.replace('n.a.', "0.0"))  # Convert 'n.a.' to 0 for scipy handling
                    time, value = float(time), float(value)
                    data_tuples.append((time, step, value))
                except ValueError: # Handle lines that cannot be converted to float
                    print(f"Skipping invalid line: {line}")
            else:
                print(f"Skipping malformed line: {line}, expected 3 columns, got {len(columns)}.")

        # Convert the list of tuples to a structured NumPy array with named columns
        data_array = np.array(data_tuples, dtype=[('time', 'f4'), ('step', 'f4'), ('value', 'f4')])
        # NOTE: assumes higher float precision will not needed
        return data_array

    def find_peaks(
        self,
        normalize: bool = False,
        min_height: float | None = None,
        distance: int | None = None,
        min_width: int | None = None,
        max_width: int | None = None,
        relative_height: float | None = None
    ) -> list[Peak]:
        """
        Identifies peaks in the chromatogram data. The input peak finding
        parameters override the default parameters defined on the class.

        Args:
        - normalize: Whether to normalize the y values to be >= 0 before peak detection.
        - min_height: Minimum height of peaks as number of standard deviations above the mean.
        - distance: Minimum number of samples between successive peaks.
        - min_width: Minimum width of peaks in number of samples.
        - max_width: Maximum width of peaks in number of samples.
        - relative_height: The height of peaks as a fraction of the maximum peak height.

        Returns:
        List of peak instances
        """
        # update normalization parameter
        if normalize: self.NORMALIZE = normalize

        # set the peak finding parameters based on the input and defaults
        height = (min_height if min_height else self.MIN_HEIGHT) * np.std(self.y) + np.mean(self.y)
        distance = distance if distance else self.DISTANCE
        min_width = min_width if min_width else self.MIN_WIDTH
        max_width = max_width if max_width else self.MAX_WIDTH
        width = [min_width, max_width]

        # find the peaks
        peaks, properties = find_peaks(
            x=self.y,
            height=height,
            distance=distance,
            width=width,
            rel_height=self.RELATIVE_HEIGHT
        )

        # convert returned peaks to list of peak instances
        peaks_list = []
        for i, peak in enumerate(peaks):
            left_threshold_index = round(properties["left_ips"][i])
            right_threshold_index = round(properties["right_ips"][i])
            peak_instance = Peak(
                index = peak,
                time = float(self.x[peak]),
                left_threshold = float(self.x[left_threshold_index]),
                right_threshold =  float(self.x[right_threshold_index]),
                left_threshold_index = left_threshold_index,
                right_threshold_index = right_threshold_index,
                height = float(self.y[peak]),
                x_data = self.x[left_threshold_index:right_threshold_index+1],
                y_data = self.y[left_threshold_index:right_threshold_index+1]
            )

            peaks_list.append(peak_instance)
        return peaks_list

    @property
    def x(self):
        """
        Returns the x values of the chromatogram data.
        """
        return self.data['time']

    @property
    def y(self):
        """
        Returns the y values of the chromatogram data. Optionally normalizes the
        values to be >= 0.
        """
        return normalize(self.data['value']) if self.NORMALIZE else self.data['value']

    @property
    def elution_volumes(self):
        """
        Returns the elution volumes of each peaks in the chromatogram.
        """
        peaks = self.find_peaks()
        elution_volumes = [peak.integrate() for peak in peaks]
        return elution_volumes

    @property
    def total_elution_volume(self):
        """
        Returns the total elution volume of the peaks in the chromatogram.
        """
        return sum(self.elution_volumes)

    def plot(
        self,
        peaks: list[Peak] | None = None,
        show_widths: bool = False,
        show_elution_volumes: bool = False
    ):
        """
        Plots the chromatogram data and optionally the detected peaks.

        Args:
        - peaks: A list of peak instances to plot.
        - show_widths: Whether to show the peak widths.
        - show_elution_volumes: Whether to show the elution volumes.
        """
        peaks = peaks if peaks else self.find_peaks()
        peak_x = [peak.time for peak in peaks]
        peak_y = [peak.height for peak in peaks]
        elution_volumes = self.elution_volumes
        for i, peak in enumerate(peaks):
            if show_widths or self.SHOW_ELUSTION_VOLUMES:
                plt.text(peak.time + 0.1, peak.height + 0.1, f"{elution_volumes[i]:.2f}", fontsize=6)
            if show_elution_volumes or self.SHOW_WIDTHS:
                plt.axvline(peak.left_threshold, color='grey', linestyle='--', linewidth=0.5)
                plt.axvline(peak.right_threshold, color='grey', linestyle='--', linewidth=0.5)

        plt.plot(self.x, self.y)
        plt.plot(peak_x, peak_y, 'ro', markersize=3)
        plt.xlabel('Time (min)')
        plt.ylabel('Value (EU)')
        plt.title(f'Chromatogram (Elution Volume: {self.total_elution_volume:.2f})')

        plt.show()

    def __str__(self):
        return f"ChromatogramData(metadata={self.metadata}, data={self.data})"
