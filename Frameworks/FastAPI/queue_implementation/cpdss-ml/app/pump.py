def estimatePumpRates(count, std_dev, mean_dev, theoretical):
    # Estimate pump rates using standard deviation and mean of deviation of mean historical pump rates form
    # theoretical maximum

    # Parameters:
    #   count: count of number of historical pump rates
    #   std_dev: standard deviation of deviation of mean from theoretical
    #   mean_dev: mean of deviation of mean from theoretical
    #   mean: mean of historical pump rates
    #   theoretical: theoretical maximum pump rates

    # Returns:
    #   Estimated pump rates

    # Benchmarks
    mean_benchmark = 10
    std_benchmark = 5
    count_benchmark = 10

    # Get mean from average deviation
    mean = getMeanFromDeviation(theoretical, mean_dev)

    if std_dev is None:
        return theoretical
    elif (mean_dev <= mean_benchmark) and (std_dev <= std_benchmark):  # Low deviation with low variance
        return theoretical
    elif (mean_dev <= mean_benchmark) and (std_dev >= std_benchmark):  # Low deviation with high variance
        return weighted(mean, theoretical, 0.1)
    elif mean_dev >= mean_benchmark:  # High deviation
        if (std_dev <= std_benchmark) & (count >= count_benchmark):  # low variance with high counts
            return mean
        else:  # high variance/low counts
            return weighted(mean, theoretical, 0.3)


def getMeanFromDeviation(maximum, dev):
    return maximum - ((dev / 100) * maximum)


def deviationFromMax(maximum, trend):
    mean_trend = trend.mean()
    dev = ((maximum - mean_trend) / maximum) * 100
    return dev, mean_trend


def weighted(mean, theoretical, weight):
    # Find a weighted average of historical mean and theoretical maximum

    # Parameters:
    #   mean: historical mean
    #   theoretical: theoretical maximum
    #   weight: weight of historical mean

    # Returns:
    #   Weighted Average
    return weight * mean + (1 - weight) * theoretical
