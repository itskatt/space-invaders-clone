def clamp(min, max, value):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value
