import numpy as np
from enum import Enum


def exp_weighted_avg(prices, com, min_periods=100):
    return np.array(
        pd.DataFrame(prices).ewm(
            com=com,
            min_periods=min_periods).mean().values.flatten(),
        dtype=np.float32)


def get_pv(prices, com, beta, min_periods=100):
    forward_ma = np.flip(np.array(exp_weighted_avg(np.flip(prices), com)))
    # just need to trim prices, since it is what we are iterating over
    prices = prices[:-min_periods]
    all_peaks, all_valleys = get_all_pv_indexes(prices, forward_ma, beta)
    condensed_peaks, condensed_valleys = consdense_events(prices, all_peaks, all_valleys)
    return condensed_peaks, condensed_valleys


def get_all_pv_indexes(prices, forward_ma, beta):
    all_peaks = []
    all_valleys = []
    for idx, price in enumerate(prices):
        diff = price / forward_ma[idx] - 1
        if diff > beta:
            all_peaks.append(idx)
        elif diff < -beta:
            all_valleys.append(idx)
    return all_peaks, all_valleys


def consdense_events(prices, all_peaks, all_valleys):
    class Env(Enum):
        PEAK = 1
        VALLEY = 2

    mode = None
    best_event = (None, None)
    best_peaks = []
    best_valleys = []

    for idx, price in enumerate(prices):
        if mode is None:
            if idx in all_peaks:
                mode = Env.PEAK
                best_event = (idx, price)
            elif idx in all_valleys:
                mode = Env.VALLEY
                best_event = (idx, price)
            else:
                continue

        is_peak = False
        is_valley = False

        if len(all_peaks) > 0 and idx == all_peaks[0]:
            is_peak = True
            del all_peaks[0]
        elif len(all_valleys) > 0 and idx == all_valleys[0]:
            is_valley = True
            del all_valleys[0]

        if mode == Env.PEAK and is_peak:
            if price > best_event[1]:
                best_event = (idx, price)

        elif mode == Env.VALLEY and is_valley:
            if price < best_event[1]:
                best_event = (idx, price)

        elif mode == Env.PEAK and is_valley:
            best_peaks.append(best_event[0])
            mode = Env.VALLEY
            best_event = (idx, price)

        elif mode == Env.VALLEY and is_peak:
            best_valleys.append(best_event[0])
            mode = Env.PEAK
            best_event = (idx, price)
    return best_peaks, best_valleys
