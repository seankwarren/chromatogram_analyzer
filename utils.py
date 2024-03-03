from numpy.typing import NDArray
from scipy.integrate import simpson
from slugify import slugify
import numpy as np


def integrate(
    x_data: NDArray[np.float32],
    y_data: NDArray[np.float32],
    method: str = 'simpson'
) -> np.float32:
    """
    Returns the area under the peak using Simpson's rule.
    see: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.simpson.html

    Args:
    - x_data: The x values of the peak.
    - y_data: The y values of the peak.
    - method: The integration method to use. Currently only 'simpson' is supported.

    Returns:
    -  The area under the peak.

    Raises:
    - ValueError: If the integration method is not supported.
    """
    match method:
        case 'simpson':
            return np.float32(simpson(x=x_data, y=y_data))
        case _:
            raise ValueError(f"Unsupported integration method: {method}")

def parse_key_value_pairs(content: str) -> dict:
    """
    Parses a tab-delimited string of key-value pairs into a dictionary. Assumes
    each line is a key-value pair separated by a tab. If a line has no tab, the
    entire line is considered the key and the value is set to None.

    Args:
    - content: String with key-value pairs separated by tabs.

    Returns:
    - dict: Dictionary with key-value pairs
    """
    lines = content.split("\n")
    data = {}
    for line in lines:
        kv = line.split("\t") # split line into key-value pair
        if len(kv) == 2:
            data[slugify_key(kv[0])] = kv[1]
        elif len(kv) == 1: # TODO: decide how to handle key-value pairs with no value
            data[slugify_key(kv[0])] = None
        else:
            print(f"Unknown line format: {line}")
    return data

def slugify_key(text: str, separator: str = '_') -> str:
    """
    Slugifies a string and replaces spaces with the specified separator.

    Args:
    - text: String to slugify
    - separator: Separator to use in place of spaces

    Returns:
    - Slugified string
    """
    return slugify(text, separator=separator)

def normalize(values: NDArray[np.float32]) -> NDArray[np.float32]:
    """
    Normalizes a list of values to the range [0, inf].

    Args:
    - values: List of values to normalize

    Returns:
    - List of normalized values
    """
    min = np.min(values)
    return np.array([value - min for value in values])
