

def epoch_to_x_ago_date(past_epoch, current_epoch):

    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
    SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR
    SECONDS_IN_MONTH = 30 * SECONDS_IN_DAY  # roughly.
    SECONDS_IN_YEAR = 365.25 * SECONDS_IN_DAY

    diff = current_epoch - past_epoch

    def _get_return_str(divider, ago_str):
        nonlocal diff
        nbr = int(diff/divider)
        if nbr > 1:
            ago_str = ago_str + "s"
        return "{} {} ago".format(nbr, ago_str)

    if diff < 0:
        return "apparently in the future?"
    elif diff < SECONDS_IN_MINUTE:
        return "less than a minute ago"
    elif diff < SECONDS_IN_HOUR:
        return _get_return_str(SECONDS_IN_MINUTE, "minute")
    elif diff < SECONDS_IN_DAY:
        return _get_return_str(SECONDS_IN_HOUR, "hour")
    elif diff < SECONDS_IN_MONTH:
        return _get_return_str(SECONDS_IN_DAY, "day")
    elif diff < SECONDS_IN_YEAR:
        return _get_return_str(SECONDS_IN_MONTH, "month")
    else:
        return _get_return_str(SECONDS_IN_YEAR, "year")
