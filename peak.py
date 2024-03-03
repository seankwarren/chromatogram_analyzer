from numpy.typing import NDArray
from utils import integrate
import matplotlib.pyplot as plt
import numpy as np

class Peak:
    """
    A class for representing a peak in chromatogram data.
    """

    def __init__(
        self,
        index: int,
        left_threshold_index: int,
        right_threshold_index: int,
        x_data: NDArray[np.float32],
        y_data: NDArray[np.float32]
    ):
        """
        Args:
        - index: The index of the peak in the chromatogram data.
        - left_threshold_index: The index of the left threshold of the peak.
        - right_threshold_index: The index of the right threshold of the peak.
        - x_data: The x values of the peak.
        - y_data: The y values of the peak.
        """
        self.index = index
        self.time = x_data[index]
        self.left_threshold = x_data[left_threshold_index]
        self.right_threshold =  x_data[right_threshold_index]
        self.height = y_data[index]
        self.times = x_data[left_threshold_index:right_threshold_index+1]
        self.values = y_data[left_threshold_index:right_threshold_index+1]
        self.area = integrate(self.times, self.values)

    def __repr__(self):
        return f"""Peak(
    time={self.time} (min),
    height={self.height} (EU),
    left_threshold={self.left_threshold} (min),
    right_threshold={self.right_threshold} (min),
    area={self.area} (EU * min)
)"""

    def plot(self, full_time_data: NDArray[np.float32], full_value_data: NDArray[np.float32]):
        """
        Plots the peak on top of the full chromatogram data.

        Args:
        - full_time_data: The x values of the full chromatogram data.
        - full_value_data: The y values of the full chromatogram data.
        """
        plt.plot(full_time_data, full_value_data, 'grey', linewidth=0.5) # full data
        plt.plot(self.times, self.values, 'b') # peak data
        plt.plot (self.time, self.height, 'ro', markersize=3) # peak marker
        plt.axvline(self.left_threshold, color='gray', linestyle='--', linewidth=0.5) # left threshold
        plt.axvline(self.right_threshold, color='gray', linestyle='--', linewidth=0.5) # right threshold
        plt.title(f"Peak (@ t={self.time} min)")
        plt.xlabel('Time (min)')
        plt.ylabel('Value (EU)')
        plt.show()
