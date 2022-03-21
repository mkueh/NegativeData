import matplotlib
import matplotlib.pyplot as plt


def plot(distribution, path, basename):
    """Generates a histogram of a distribution using matplotlib.pyplot.
    Saves the distribution as a png file.

    Parameters:
        distribution (Distribution): Distribution object to be visualized
        path (str): Path to the target file name
        basename (str): Base name of the distribution

    Returns:
        None
    """
    fig = plt.subplot()
    plt.ylabel("Relative Occurence", fontdict={'fontsize': 12, 'weight': 'heavy'})
    fig.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    plt.xticks(fontweight='heavy')
    plt.yticks(fontweight='heavy')
    fig.bar(list(distribution.probabilities.keys()), list(distribution.probabilities.values()), width=distribution.binsize, align='edge', color=(202/255, 206/255, 225/255), edgecolor=(37/255, 50/255, 125/255), linewidth=2)
    plt.savefig("{}/{}_Distribution.png".format(path, basename), dpi=300, format='png', transparent=True)
    plt.close()

