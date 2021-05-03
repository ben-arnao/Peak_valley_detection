import numpy as np
from enum import Enum
import pandas as pd

# 'signal' is an array of floats

# 'com' is the factor that determines the time horizon for the exp moving avg
# see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html for more info

# 'beta' is the threshold the signal has to exceed to be marked as a peak/valley

# 'min_periods' is used for ensuring the integrity of the exp moving average in the beginning data points by
# not assigning a value to them, instead of just assigning a mostly incomplete value

# 'condense_events' is used for only taking the most extreme event from a group of consecutive events

# 'backwards' computes outliers for both directions. With backwards disabled, 
# a value will only be marked if there is a change of value *prior* to the current step.
# For example, if the signal plateaus and then drops off, the point of drop off will not be marked as a peak.


def get_event_indexes(signal, com, beta, min_periods, condense_events=True, backwards=True):
    forward_ma = np.flip(np.array(exp_weighted_avg(np.flip(signal), com, min_periods)))
    forward_peaks, forward_valleys = get_all_indexes_above_threshold(signal[:-min_periods], forward_ma, beta)
    
    if backwards:
        backward_ma = np.array(exp_weighted_avg(signal, com, min_periods))
        backward_peaks, backward_valleys = get_all_indexes_above_threshold(signal[min_periods:], backward_ma, beta)
    
        all_peaks = forward_peaks + backward_peaks
        all_valleys = forward_valleys + backward_valleys
    else:
        all_peaks = forward_peaks
        all_valleys = forward_valleys
    
    if condense_events:
        condensed_peaks, condensed_valleys = consdense_events(signal, all_peaks, all_valleys)
        return condensed_peaks, condensed_valleys
    else:
        return all_peaks, all_valleys


def exp_weighted_avg(signal, com, min_periods):
    return np.array(
        pd.DataFrame(signal).ewm(
            com=com,
            min_periods=min_periods).mean().values.flatten(),
        dtype=np.float32)


def get_all_indexes_above_threshold(signal, moving_average, beta):
    all_peaks = []
    all_valleys = []
    for idx, val in enumerate(signal):
        diff = val / moving_average[idx] - 1
        if diff > beta:
            all_peaks.append(idx)
        elif diff < -beta:
            all_valleys.append(idx)
    return all_peaks, all_valleys


def consdense_events(signal, all_peaks, all_valleys):
    class Env(Enum):
        PEAK = 1
        VALLEY = 2

    mode = None
    best_event = (None, None)
    best_peaks = []
    best_valleys = []

    for idx, val in enumerate(signal):
        if mode is None:
            if idx in all_peaks:
                mode = Env.PEAK
                best_event = (idx, val)
            elif idx in all_valleys:
                mode = Env.VALLEY
                best_event = (idx, val)
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
            if val > best_event[1]:
                best_event = (idx, val)

        elif mode == Env.VALLEY and is_valley:
            if val < best_event[1]:
                best_event = (idx, val)

        elif mode == Env.PEAK and is_valley:
            best_peaks.append(best_event[0])
            mode = Env.VALLEY
            best_event = (idx, val)

        elif mode == Env.VALLEY and is_peak:
            best_valleys.append(best_event[0])
            mode = Env.PEAK
            best_event = (idx, val)
    return best_peaks, best_valleys
