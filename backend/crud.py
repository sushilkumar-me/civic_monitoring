def detect_ward(lat, lon):
    if 22.28 <= lat <= 22.31:
        return 1
    elif 22.31 < lat <= 22.34:
        return 2
    else:
        return 3
