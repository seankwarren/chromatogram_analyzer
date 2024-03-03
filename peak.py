from numpy.typing import NDArray
from scipy.integrate import simpson
import matplotlib.pyplot as plt
import numpy as np

class Peak:
    def __init__(
        self,
        index: int,
        time: float,
        left_threshold: float,
        left_threshold_index: int,
        right_threshold:float,
        right_threshold_index: int,
        height: float,
        x_data: NDArray,
        y_data: NDArray
    ):
        self.index = index
        self.time = time
        self.left_threshold = left_threshold
        self.right_threshold = right_threshold
        self.left_threshold_index = left_threshold_index
        self.right_threshold_index = right_threshold_index
        self.height = height
        self.x = x_data
        self.y = y_data

    def __str__(self):
        return f"""Peak(
            index={self.index},
            time={self.time},
            left_threshold={self.left_threshold},
            right_threshold={self.right_threshold},
            left_threshold_index={self.left_threshold_index},
            right_threshold_index={self.right_threshold_index},
            height={self.height})
            volume={self.integrate()}"""

    def plot(self, full_x_data = None, full_y_data = None):
        if (full_x_data is not None and full_y_data is None) or (full_x_data is None and full_y_data is not None):
            raise ValueError("Both full_x_data and full_y_data must be provided")

        if full_x_data is not None and full_y_data is not None:
            plt.plot(full_x_data, full_y_data, 'grey', linewidth=0.5)

        plt.title(f"Peak {self.index}")
        plt.xlabel('Time (min)')
        plt.ylabel('Value (EU)')
        plt.plot(self.x, self.y, 'b')
        # peak marker
        plt.plot (self.time, self.height, 'ro', markersize=3)
        # threshold markers
        plt.axvline(self.left_threshold, color='gray', linestyle='--', linewidth=0.5)
        plt.axvline(self.right_threshold, color='gray', linestyle='--', linewidth=0.5)

        plt.show()

    def integrate(self):
        return simpson(y=self.y, x=self.x)
