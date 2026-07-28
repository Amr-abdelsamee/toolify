# Plotting

`line_plotter` saves one or more equal-length series as a line plot:

```python
from toolify.plots import line_plotter

line_plotter(
    data_list=[
        [1, 2, 3],
        [3, 2, 1],
    ],
    save_name="plot.png",
    legend_list=["Increasing", "Decreasing"],
    x_values=[0, 1, 2],
    x_label="Step",
    y_label="Value",
    title="Example",
    size=(10, 6),
)
```

When `x_values` is omitted, Toolify uses sequential indices beginning at zero.
All series must have the same length, and the number of legend labels must
match the number of series.
