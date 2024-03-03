from io import StringIO
from numpy.typing import NDArray
from peak import Peak
import matplotlib.pyplot as plt
import numpy as np
import re
import scipy.signal
import utils

# Default peak-finding parameters
DEFAULT_PEAK_NORMALIZE = False # whether to normalize the y values to be >= 0 before peak detection
DEFAULT_PEAK_DISTANCE = 75 # number of data points between peaks
DEFAULT_PEAK_PROMINENCE = .15 # minimum peak prominence
DEFAULT_PEAK_MIN_WIDTH = 10 # minimum number of data points
DEFAULT_PEAK_MAX_WIDTH = 1000 # maximum number of data points
DEFAULT_PEAK_RELATIVE_HEIGHT = .95 # number between 0 and 1. used for determining left and right peak thresholds

class ChromatogramRun:
    """
    A class for parsing and analyzing chromatogram data.
    """

    def __init__(self, filepath: str):
        """
        Args:
        - filepath: The path to the file containing the chromatogram data.
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                self._parse_file(content)
                self._normalized = DEFAULT_PEAK_NORMALIZE

        except FileNotFoundError:
            print(f"File {filepath} not found.")
            return None

    def _parse_file(self, content: str):
        """
        Parses the file content into metadata and chromatogram data.

        Args:
        - content: The content of the file.

        Side effects:
        - Sets the metadata and data attributes of the ChromatogramRun instance.
        """

        section_title_regex = r'^(.+?:)\n' # match any line ending with a colon
        # split the file into sections based on section titles
        sections = re.split(section_title_regex, content, flags=re.MULTILINE)
        # extract all key value pair sections into a metadata dictionary
        self.metadata = {
            **utils.parse_key_value_pairs(sections[0].strip()),
            "injection_info": utils.parse_key_value_pairs(sections[2].strip()),
            "chromatogram_data_info": utils.parse_key_value_pairs(sections[4].strip()),
            "signal_parameter_info": utils.parse_key_value_pairs(sections[6].strip()),
        }

        # parse the chromatogram data into a structured NumPy array
        self.data = self.parse_chromatogram_data(sections[8].strip())

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
        content_io = StringIO(content)

        # Define a converter for the 'step' column to handle 'n.a.' values
        filter_na = lambda s: np.float32(s.decode('utf-8').replace('n.a.', '0.0'))

        # see https://numpy.org/doc/stable/reference/generated/numpy.genfromtxt.html
        dtype = [('time', 'f4'), ('step', 'f4'), ('value', 'f4')]
        data_array = np.genfromtxt(content_io, delimiter='\t', skip_header=1,
                                    converters={0: filter_na, 1: filter_na, 2: filter_na}, dtype=dtype,
                                    missing_values='', filling_values=0.0)
        return data_array

    def find_peaks(
        self,
        normalize: bool = DEFAULT_PEAK_NORMALIZE,
        distance: int = DEFAULT_PEAK_DISTANCE,
        prominence: float = DEFAULT_PEAK_PROMINENCE,
        min_width: int = DEFAULT_PEAK_MIN_WIDTH,
        max_width: int = DEFAULT_PEAK_MAX_WIDTH,
        relative_height: float = DEFAULT_PEAK_RELATIVE_HEIGHT,
    ) -> list[Peak]:
        """
        Identifies peaks in the chromatogram data. The input peak finding
        parameters override the default parameters defined on the class. See
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
        for more information on the peak finding parameters.

        Args:
        - normalize: Whether to normalize the y values to be >= 0 before peak
            detection.
        - distance: Minimum number of samples between successive peaks.
        - prominence: Minimum peak prominence.
        - min_width: Minimum width of peaks in number of samples.
        - max_width: Maximum width of peaks in number of samples.
        - relative_height: The height of peaks as a fraction of the maximum peak
            height. Used to determine the left and right thresholds.

        Returns:
        List of peak instances
        """
        if normalize: self._normalized = True

        peaks, properties = scipy.signal.find_peaks(
            x=self.values,
            prominence=prominence,
            distance=distance,
            width=[min_width, max_width],
            rel_height=relative_height,
        )

        self.peaks = [Peak(
            index=peak,
            left_threshold_index=round(properties["left_ips"][i]), # NOTE: round the threshold indices to ints
            right_threshold_index=round(properties["right_ips"][i]),
            x_data=self.times,
            y_data=self.values if normalize else self.values,
        ) for i, peak in enumerate(peaks)]
        return self.peaks

    @property
    def times(self) -> NDArray[np.float32]:
        return self.data['time']

    @property
    def values(self) -> NDArray[np.float32]:
        return utils.normalize(self.data['value']) if self._normalized else self.data['value']


    def elution_volumes(self) -> list[np.float32]:
        """
        Returns the elution volumes of each peaks.
        """
        return [peak.area for peak in self.peaks]

    def plot(
        self,
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
        peak_times = [peak.time for peak in self.peaks]
        peak_values = [peak.height for peak in self.peaks]

        # plot each peak, optionally with widths and elution volumes
        for i, peak in enumerate(self.peaks):
            if show_elution_volumes:
                plt.text(peak.time, peak.height, f"{self.elution_volumes()[i]:.2f}", fontsize=6)
            if show_widths:
                plt.axvline(peak.left_threshold, color='grey', linestyle='--', linewidth=0.5)
                plt.axvline(peak.right_threshold, color='grey', linestyle='--', linewidth=0.5)

        plt.plot(self.times, self.values) # full chromatogram data
        plt.plot(peak_times, peak_values, 'ro', markersize=3) # peak data
        plt.xlabel('Time (min)')
        plt.ylabel('Value (EU)')
        plt.title(f'Chromatogram data')
        plt.show()

    def __str__(self):
        return f"ChromatogramData(metadata={self.metadata}, data={self.data})"
