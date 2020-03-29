# Histograms

Here we plot the distributions of the increments of confirmed and
deaths for each single country. We consider the observations since the first
one, then we plot the histograms, and the kernel density estimates.

We calculate the number of bins for each histogram using the Doane's formula:

    n_bins = 1 + log(n) + log(1 + abs(g1 / sigma(data))
    sigma(data) = sqrt(6(n - 2) / (n + 1)(n + 3)
where g1 is the estimated 3rd-moment-skewness of the distribution and
n is the total number of observations.

For the kernel density estimation we decide to use the well-known gaussian
kernel, that is implemented as the default one in matplotlib library. 
Since for some country we have very few data, the kernel estimate
could miss in some plots.

In each histogram we also show, with a blue line, where the observation 
of yesterday is collocated in the distribution.
