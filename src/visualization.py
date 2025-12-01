import matplotlib.pyplot
import seaborn
import pandas
import numpy as np
from shapely.coordinates import transform


# sample dataframe to test
# df = pandas.read_csv("../data/output/csv_dataframe_flagged/flagged_plates.csv")

def plot_anomaly_visualization(df: pandas.DataFrame,
                               x_axis_col: str,
                               y_axis_col: str) -> matplotlib.pyplot.Figure:
    """
    .. note::
        Generates a 2-subplot figure with the given columns as axes.

        1/ Histogram of Anomaly Score: It shows the distribution and cut-offs of anomaly scores.

        2/ Scatter Plot of two selected features: It shows spatial, geometric separation.

    :param df:
        The input (passed result) DataFrame which contains the *AnomalyScore*, *AnomalyFlag* and feature columns.
    :param x_axis_col:
        Name of the column to use for the X-axis on the scatter plot.
    :param y_axis_col:
        Name of the column to use for the Y-axis on the scatter plot.

    :return: ``fig``: **matplotlib.pyplot.Figure**
        The figure object to be rendered in Streamlit UI.
    """

    # 0. BASIC DATA CHECKS - no meaningful visualization with data samples < 3
    scores_series = df["AnomalyScore"].dropna()

    if scores_series.shape[0] < 3:
        fig, axes = matplotlib.pyplot.subplots()
        axes.text(0.5, 0.5, "Not enough data to create visualization.", ha="center", va="center", transform=axes.transAxes)
        axes.set_axis_off()
        return fig

    # 0. STYLE SETTINGS
    seaborn.set_style("whitegrid")
    # seaborn.set_theme(style="whitegrid")

    # 0. FRAME: 1 row, 2 columns
    # two variables because 'matplotlib.pyplot.subplots()' returns a tuple
    fig, axes = matplotlib.pyplot.subplots(
        nrows=1,
        ncols=2,
        figsize=(15, 4)
    )

    # 1. HISTOGRAM OF ANOMALY SCORES
    # This histogram depicts how well the algorithm was able to separate anomalies from normal data points.
    # Decide if KDE is numerically safe and statistically meaningful
    scores = scores_series.to_numpy()
    kde_ok = (scores.size >= 10) and (np.std(scores) > 1e-9)

    seaborn.histplot(
        data=df,
        x="AnomalyScore",
        hue="AnomalyFlag",
        palette={1: "skyblue", -1: "red"},
        kde=kde_ok, # or True if blowing up is ok, False for turning of the smoothness
        bins=30,
        ax=axes[0], # index of the subplot
        element="bars" # type of histogram
    )

    # 1.2. DECLARING DECISION BOUNDARIES = [0]
    # axes[0].axvline(x=0, color="black", linestyle="--", linewidth=2, label="Decision Boundary (0)") # this is a line of decision boundary
    axes[0].set_title("Anomaly Score Distribution")
    axes[0].set_xlabel("Anomaly Score (< 0: Anomaly, > 0: Normal)")
    axes[0].set_ylabel("Count")
    # axes[0].legend(title="Legend", ) # legend for the histogram

    # 2. SCATTER PLOT OF FEATURES
    # This scatter plot shows the spatial separation between normal and anomalous data points.
    seaborn.scatterplot(
        data=df,
        x=x_axis_col,
        y=y_axis_col,
        hue="AnomalyFlag", # color by label, which means that the points will be colored according to their label
        style="AnomalyFlag",
        palette={1: "skyblue", -1: "red"},
        markers={1: "o", -1: "s"},
        s=100, # point size
        ax=axes[1], # index of the subplot
        alpha=0.7 # transparency
    )

    axes[1].set_title(f"Anomaly Map: {x_axis_col} vs. {y_axis_col}")
    axes[1].set_xlabel(x_axis_col)
    axes[1].set_ylabel(y_axis_col)

    matplotlib.pyplot.tight_layout()
    # matplotlib.pyplot.show()
    return fig

# run the sample
# plot_anomaly_visualization(df, "anomaly_score", "anomaly_label")