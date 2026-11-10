import sys
import csv
import math



R = 6371000          
ARRIVE_DIST = 3.0    
STOP_SPEED = 0.5     
GREEN_TIME = 5       


def haversine(lat1, lon1, lat2, lon2):
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def to_number(text):
    try:
        value = float(text)
    except (ValueError, TypeError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def good_position(lat, lon):
    if lat is None or lon is None:
        return False
    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        return False
    if lat == 0 and lon == 0:
        return False
    return True


def read_targets(filename):
    targets = []
    try:
        file = open(filename, newline="", encoding="utf-8-sig")
    except OSError:
        return targets
    for row in csv.reader(file):
        if len(row) < 3:
            continue
        lat = to_number(row[1])
        lon = to_number(row[2])
        if good_position(lat, lon):     
            targets.append((lat, lon))
    file.close()
    return targets


def main():
    if len(sys.argv) < 2:
        print("usage: python light.py mission_log.csv targets.csv")
        return

    log_name = sys.argv[1]
    targets = []
    if len(sys.argv) > 2:
        targets = read_targets(sys.argv[2])

    try:
        file = open(log_name, newline="", encoding="utf-8-sig")
    except OSError:
        print("cannot open", log_name)
        return

    current_target = 0       
    green_until = None     
    mode = "MANUAL"        
    last_time = None        
    last_lat = None
    last_lon = None

    for row in csv.reader(file):
        if len(row) == 0:
            continue

        t = to_number(row[0])
        if t is None:
            continue        

        if len(row) > 1:
            m = row[1].strip().upper()
            if m == "AUTO" or m == "MANUAL":
                mode = m

        lat = None
        lon = None
        if len(row) > 3:
            lat = to_number(row[2])
            lon = to_number(row[3])

        speed = None
        if good_position(lat, lon):
            
            if last_time is not None and t > last_time:
                dist = haversine(last_lat, last_lon, lat, lon)
                speed = dist / (t - last_time)
            if last_time is None or t > last_time:
                last_time = t
                last_lat = lat
                last_lon = lon

        if green_until is not None and t < green_until:
            light = "green"
        else:
            light = "blue"
            if mode == "AUTO":
                light = "red"

            if mode == "AUTO" and speed is not None and current_target < len(targets):
                tlat, tlon = targets[current_target]
                d = haversine(lat, lon, tlat, tlon)
                if d <= ARRIVE_DIST and speed < STOP_SPEED:
                    light = "green"
                    green_until = t + GREEN_TIME
                    current_target += 1

        if t == int(t):
            t = int(t)
        print(str(t) + "," + light)

    file.close()


main()
