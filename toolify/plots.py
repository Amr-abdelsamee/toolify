from itertools import cycle
from typing import List, Tuple

def line_plotter(
    data_list: List[List[float]],
    save_name: str,
    legend_list: List[str] = [],
    x_values: List[float] = [],
    x_label: str = "",
    y_label: str = "",
    title: str = "",
    size: Tuple[int, int] = (10, 6),
) -> None:
    """Saves a line plot for each list in data_list.

    Args:
        data_list: List of data lists to plot.
        save_name: File path to save the plot.
        legend_list: List of legend labels for each data list. If empty, no legend is shown.
        x_values: Values for the x-axis. If empty, uses range(len(data_list[0])).
        x_label: Label for the x-axis. Defaults to empty string.
        y_label: Label for the y-axis. Defaults to empty string.
        title: Title of the plot. Defaults to empty string.
        size: Figure size as (width, height). Defaults to (10, 6).

    Raises:
        ValueError: If data_list is empty, legend_list length mismatches, or data lists have different sizes.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed.")
        return

    if not data_list:
        raise ValueError("data_list cannot be empty")
    if legend_list and len(data_list) != len(legend_list):
        raise ValueError("Length of data_list must match length of legend_list")

    data_lengths = {len(data) for data in data_list}
    if len(data_lengths) > 1:
        raise ValueError("All lists in data_list must have the same size")

    plt.figure(figsize=size)
    if not x_values:
        x_values = list(range(len(data_list[0])))

    colors = cycle(["blue", "red", "green", "purple", "orange", "cyan", "magenta"])
    markers = cycle(["o", "s", "^", "D", "v", "<", ">"])
    linestyles = cycle(["-", "--", ":", "-."])

    for data, color, marker, linestyle in zip(data_list, colors, markers, linestyles):
        if legend_list:
            plt.plot(
                x_values,
                data,
                marker=marker,
                linestyle=linestyle,
                color=color,
                label=legend_list[0],
            )
            legend_list = legend_list[1:]  # Avoid mutating original list
        else:
            plt.plot(x_values, data, marker=marker, linestyle=linestyle, color=color)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if legend_list:
        plt.legend()

    plt.grid(True, linestyle="--", alpha=0.7)
    plt.savefig(save_name, dpi=300, bbox_inches="tight")
    plt.close()

