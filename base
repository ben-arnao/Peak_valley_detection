def get_peak_valley(arr, threshold, window_size, overlap, req_angles):

    #Note: Because of the nature of this method, and for the purposes of integrity, data points before window_length and after (len(arr) - window_length) * 2 should not be considered as potential pak/valley candidates.
    #-- better way to handle this?

    #threshold: the amount of standard deviations for a point to be considered a peak/valley
    #-- add option to make % above mean as well as std for a different approach to detection.
    
    #window_size: size of chunks to break the signal down into. smaller chunks are better for more non-staionary signals
    #-- possiby want to come up with a method to make windowsize adaptable
    
    
    #overlap: the percentage of shared data points from one window to the next
    #req_angles: the number of windows a point needs to be detected in
    #-- add a parameter for forward/bidirectional detection
    #-- add param to detect the best of consecutive, or all
    
    #The method i believe gives you two-way peak detection as opposed to moving average methods which might not. Through overlap and requiring that a peak be deteced in multiple windows, this allows you to fine tune whether certain types of peaks should be detected.
    
    # do param validation here

    # get all points that classify as a peak/valley
    ind = 0
    peak_inds, valley_inds = [], []

    while ind + window_size <= len(arr):
        flattened = detrend(arr[ind:ind + window_size])
        std, avg = np.std(flattened), np.mean(flattened)
        lower_b = avg - std * threshold
        upper_b = avg + std * threshold
        for idx, val in enumerate(flattened):
            if val < lower_b:
                valley_inds.append(idx + ind)
            elif val > upper_b:
                peak_inds.append(idx + ind)
        ind += window_step

    # discard points that have counts below the threshold
    peak_counts = Counter(peak_inds)
    pk_inds = [c for c in peak_counts.keys() if peak_counts[c] >= req_angles]

    valley_counts = Counter(valley_inds)
    vly_inds = [c for c in valley_counts.keys() if valley_counts[c] >= req_angles]

    # initialize iterator to find to best peak/valley for consecutive detections
    
    # set first event
    if pk_inds[0] < vly_inds[0]:
        curr_event = 'peak'
        value = arr[pk_inds[0]]
    else:
        curr_event = 'valley'
        value = arr[vly_inds[0]]

    #iterate through points and only carry forward the index that has the highest or lowest value from the current group
    best_ind, new_vly_inds, new_pk_inds = 0, [], []

    event_inds = pk_inds + vly_inds
    event_inds = sorted(event_inds)

    for x in event_inds:
        if x in pk_inds:
            is_peak = True
        else:
            is_peak = False

        if is_peak and curr_event == 'valley':
            new_vly_inds.append(best_ind)
            curr_event = 'peak'
            value = arr[x]
            best_ind = x
            continue
        if not is_peak and curr_event == 'peak':
            new_pk_inds.append(best_ind)
            curr_event = 'valley'
            value = arrs[x]
            best_ind = x
            continue

        if is_peak and curr_event == 'peak' and close_prices[x] > value:
            value = arr[x]
            best_ind = x
        elif not is_peak and curr_event == 'valley' and close_prices[x] < value:
            value = arr[x]
            best_ind = x

    if curr_event == 'valley':
        new_vly_inds.append(best_ind)
    if curr_event == 'peak':
        new_pk_inds.append(best_ind)

return new_pk_inds, new_vly_inds
