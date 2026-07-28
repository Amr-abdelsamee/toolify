# Quick Start

## Terminal output

```python
from toolify.tools import pct

pct("Completed", color="green", emoji="success")
pct("Plain output", ec=False)
```

## Arabic text

```python
from toolify.tools import pat, strip_tashkeel

pat("مرحبا بالعالم", color="blue", emoji="heart")
print(strip_tashkeel("مُحَمَّدٌ"))
```

## Tables

```python
from toolify.tools import print_table

print_table(
    headers=["Name", "Score"],
    rows=[["Ali", 95], ["Sara", 88]],
    style=2,
)
```

## Plotting

```python
from toolify.plots import line_plotter

line_plotter(
    data_list=[[1, 2, 3], [3, 2, 1]],
    save_name="plot.png",
    legend_list=["Increasing", "Decreasing"],
)
```

See the individual guides for audio, Hugging Face, and YouTube workflows.
