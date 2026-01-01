# simulation.py
"""
EMS Simulation (Data-Free Demo)

This file contains the EMS simulation and the fitness function used by the GA.

- fitness_function(primary_list, th, AMBULANCE_NUMBER, STATIONS_NUMBER, iterations)
  returns a dictionary of performance metrics.
- This demo uses synthetic calls/locations to avoid sharing private datasets.
"""

import math
import bisect
import random
import numpy as np

SEED = 31
random.seed(SEED)
np.random.seed(SEED)


# -----------------------------
# Core helpers
# -----------------------------
def distance_km(lat1, lon1, lat2, lon2):
    """Haversine distance (km)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    r = 6371.0
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def get_travel_time_minutes(d_km, b0=0.336, b1=0.000058, b2=0.0388):
    """Travel time model (minutes) based on your original structure."""
    if d_km <= 0.1:
        return 0.0
    if d_km <= 4.13:
        md = 2.42 * math.sqrt(d_km)
    else:
        md = 2.46 + 0.596 * d_km
    cd = math.sqrt((b0 * (b2 + 1) + b1 * (b2 + 1) * md + b2 * md ** 2)) / md
    return md * math.exp(cd)


def build_table(primary_list):
    """Convert GA chromosome into a repositioning table."""
    table = []
    for i in range(len(primary_list) + 1):
        table.append(primary_list[:i])
    return table


# -----------------------------
# Fixed stations/hospitals
# -----------------------------
def fixed_location_generator(ambulance_n=16, stations_n=17, hospitals_n=5):
    station_lat = [
        53.560819, 53.459373, 53.596919, 53.458361, 53.540513, 53.524711, 53.501455,
        53.616200, 53.576052, 53.496447, 53.599942, 53.548177, 53.491966, 53.493017,
        53.553621, 53.548412, 53.570662
    ]
    station_lon = [
        -113.493309, -113.591074, -113.420168, -113.393060, -113.593065, -113.456783, -113.628936,
        -113.539335, -113.459060, -113.517286, -113.465073, -113.565264, -113.494986, -113.417560,
        -113.525529, -113.500589, -113.407889
    ]

    stations = [{"id": i + 1, "latitude": station_lat[i], "longitude": station_lon[i]} for i in range(stations_n)]

    home_station = [2, 2, 3, 4, 4, 6, 7, 7, 8, 8, 9, 11, 12, 13, 13, 15]
    assert len(home_station) >= ambulance_n

    ambulances = []
    for i in range(ambulance_n):
        hs = home_station[i]
        ambulances.append({
            "id": i,
            "availability": 1,     # 1=available, 0=busy, 3=repositioning (demo keeps it minimal)
            "latitude": station_lat[hs],
            "longitude": station_lon[hs],
        })

    hospital_lat = [53.55696, 53.52071, 53.60444, 53.461583, 53.521115]
    hospital_lon = [-113.496566, -113.523769, -113.417621, -113.429724, -113.613514]
    hospitals = [{"id": i, "latitude": hospital_lat[i], "longitude": hospital_lon[i]} for i in range(hospitals_n)]

    return ambulances, stations, hospitals


# -----------------------------
# Synthetic calls (no private data)
# -----------------------------
def generate_interarrivals(total_days=35):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    LAMBDA_BASE = {"Shift 1": 0.2967, "Shift 2": 0.2967, "Shift 3": 0.1483}
    day_mult = {"Monday": 1.0, "Tuesday": 0.8, "Wednesday": 0.8, "Thursday": 1.0, "Friday": 1.2, "Saturday": 1.2, "Sunday": 1.0}

    total_sim = total_days * 24 * 60
    t = 0.0
    interarrivals = []

    while t < total_sim:
        day = days[int((t // (24 * 60)) % 7)]
        time_in_day = t % (24 * 60)
        if 5 * 60 <= time_in_day < 13 * 60:
            shift = "Shift 1"
        elif 13 * 60 <= time_in_day < 21 * 60:
            shift = "Shift 2"
        else:
            shift = "Shift 3"

        lam = LAMBDA_BASE[shift] * day_mult[day]
        ia = np.random.exponential(1 / lam)
        t += ia
        interarrivals.append(ia)

    return interarrivals


def synthetic_call_locations(n):
    # Edmonton-ish bounding box (demo)
    min_lat, max_lat = 53.35, 53.70
    min_lon, max_lon = -113.75, -113.25
    lats = np.random.uniform(min_lat, max_lat, size=n)
    lons = np.random.uniform(min_lon, max_lon, size=n)
    return list(zip(lats, lons))


# -----------------------------
# FITNESS FUNCTION
# -----------------------------
def fitness_function(primary_list, th, AMBULANCE_NUMBER, STATIONS_NUMBER, iterations=3):
    """
    Fitness function used by the GA.

    Input:
      primary_list: GA chromosome (list of station IDs)
      th: threshold (if available ambulances < th -> reposition logic triggers)
    Output:
      dict of metrics (median response time is the default GA objective here).
    """
    reposition_table = build_table(primary_list)

    medians, coverages, losts = [], [], []

    for _ in range(iterations):
        ambulances, stations, hospitals = fixed_location_generator(AMBULANCE_NUMBER, STATIONS_NUMBER, hospitals_n=5)

        interarrivals = generate_interarrivals(total_days=35)
        treat_times = np.random.exponential(1 / 15, size=len(interarrivals))
        coords = synthetic_call_locations(len(interarrivals))
        hospital_req = [1 if random.random() < 0.7 else 0 for _ in range(len(interarrivals))]

        # Build calls: (time, treat, lat, lon, hos_req)
        t = 0.0
        calls = []
        for i, ia in enumerate(interarrivals):
            t += ia
            lat, lon = coords[i]
            calls.append((t, float(treat_times[i]), float(lat), float(lon), float(hospital_req[i])))

        warmup = 7 * 24 * 60

        # Event list
        events = []
        for c in calls:
            bisect.insort(events, {"time": c[0], "type": "call", "treat": c[1], "lat": c[2], "lon": c[3], "hos": c[4]},
                          key=lambda x: x["time"])

        current_state = AMBULANCE_NUMBER
        travel_times = []
        lost = 0

        while events:
            e = events.pop(0)

            if e["type"] == "call":
                if current_state == 0:
                    if e["time"] >= warmup:
                        lost += 1
                    continue

                free = [a for a in ambulances if a["availability"] == 1]
                # if none are marked free but state says we have, just fallback
                if not free:
                    free = ambulances

                dists = [distance_km(a["latitude"], a["longitude"], e["lat"], e["lon"]) for a in free]
                amb = free[int(np.argmin(dists))]

                amb["availability"] = 0
                current_state -= 1
                amb["latitude"], amb["longitude"] = e["lat"], e["lon"]

                t1 = get_travel_time_minutes(min(dists))
                if e["time"] >= warmup:
                    travel_times.append(t1)

                if e["hos"] == 1:
                    hd = [distance_km(e["lat"], e["lon"], h["latitude"], h["longitude"]) for h in hospitals]
                    t2 = get_travel_time_minutes(min(hd))
                    if e["time"] >= warmup:
                        travel_times.append(t2)
                    hosp_treat = np.random.exponential(35)
                    finish = e["time"] + t1 + e["treat"] + t2 + hosp_treat
                else:
                    finish = e["time"] + t1 + e["treat"]

                bisect.insort(events, {"time": finish, "type": "free", "amb_id": amb["id"]}, key=lambda x: x["time"])

            elif e["type"] == "free":
                amb = ambulances[e["amb_id"]]
                amb["availability"] = 1
                current_state += 1

                # Demo reposition trigger: when available < th, choose a candidate station and "move" there
                if current_state < th:
                    idx = min(len(reposition_table) - 1, current_state)
                    candidates = reposition_table[idx] if reposition_table[idx] else [1, 2, 3]
                    candidates = [c for c in candidates if 1 <= c <= len(stations)]
                    if not candidates:
                        candidates = [1, 2, 3]

                    # Move to nearest candidate station
                    ds = []
                    for cid in candidates:
                        st = stations[cid - 1]
                        ds.append(distance_km(amb["latitude"], amb["longitude"], st["latitude"], st["longitude"]))
                    target_station = candidates[int(np.argmin(ds))]
                    st = stations[target_station - 1]
                    amb["latitude"], amb["longitude"] = st["latitude"], st["longitude"]

            else:
                raise ValueError("Unknown event type")

        if travel_times:
            med = float(np.median(travel_times))
            cov = float(np.mean([t <= 9 for t in travel_times]))
        else:
            med, cov = 999.0, 0.0

        medians.append(med)
        coverages.append(cov)
        losts.append(lost)

    return {
        "median_response_time": float(np.mean(medians)),  # default GA objective (minimize)
        "coverage": float(np.mean(coverages)),
        "lost_calls": float(np.mean(losts)),
    }
