import geo
import airport

DEP = 'DEP'             # Departure
ARR = 'ARR'             # Arrival
STEP = 5                # Minimal time step (seconds)
LAND_D = 40 // STEP     # Landing duration (time steps)
TAKEOF_D = 60 // STEP  # Take-of duration (time steps)
RUNWAY_WIDTH = 90       # Runway area width (meters)
SEP = 70                # Minimal distance separation (meters)
SEP2 = SEP * SEP


class Flight(object):
    """ Flight data """
    def __init__(self, callsign, dep, cat, stand, runway, qfu, time, slot):
        self.callsign = callsign  # Flight call-sign (str)
        self.dep = dep            # Departure ? (bool)
        self.cat = cat            # Aircraft wake vortex category
        self.stand = stand        # Used stand index
        self.runway = runway      # Used Runway index
        self.qfu = qfu            # Used QFU index
        self.time = time          # Beginning time (time steps)
        self.slot = slot          # NMOC slot (time steps)
        self.route = []           # Followed route [((x, y), loc), ...]

    def get_position(self, t):
        """ Return the (x, y) position of the flight at time 't'"""
        return self.route[t - self.time][0]

    def stop(self, t):
        dt = t - self.time
        return (0 < dt and self.route[dt - 1][1] != 'P' and
                self.route[dt - 1] == self.route[dt])


class Traffic(object):
    """ Traffic description """
    def __init__(self, name, flights):
        self.name = name
        self.flights = flights
        self.t_min = 0
        self.t_max = 0
        self.ids = []
        if flights != []:
            self.t_min = min(flight.time for flight in flights)
            t_max = max(flight.time + len(flight.route) for flight in flights)
            self.ids = [[] for _ in range(t_max - self.t_min)]
            for (i, flight) in enumerate(self.flights):
                t0 = flight.time - self.t_min
                for t in range(t0, t0 + len(flight.route)):
                    self.ids[t].append(i)

    def get_plots(self, t):
        """ Extract the list of plots (i, (x, y)) at time step 't'"""
        if self.t_min <= t < self.t_min + len(self.ids):
            ids = self.ids[t - self.t_min]
            return [(i, self.flights[i].get_position(t)) for i in ids]
        return []

# Time string conversions

def to_hms(t):
    """ Formatted HH:MM:SS string representing time step 't'"""
    time = t * STEP
    h = time // 3600
    m = time % 3600 // 60
    s = time % 60
    return '{:02d}:{:02d}:{:02d}'.format(h, m, s)


def to_time(str_hms):
    """ Time step corresponding to a string 'hms'"""
    hms = str_hms.replace(':', ' ').split()
    h = 0 if len(hms) < 1 else int(hms[0])
    m = 0 if len(hms) < 2 else int(hms[1])
    s = 0 if len(hms) < 3 else int(hms[2])
    return (h * 3600 + m * 60 + s) // STEP


# Load a traffic file

def get_xys(str_xy_list):
    """ Convert an x,y string list 'str_xy_list' to coordinates """
    str_xys = [s.split('.')[:3] for s in str_xy_list]
    return [((int(p[0]), int(p[1])), p[2]) for p in str_xys]


def load(apt, filename):
    """ Load a traffic file 'filename' on airport 'apt': return the traffic """
    print('Loading traffic:', filename + '...', end='')
    cat_dict = {'L': airport.LIGHT, 'M': airport.MEDIUM, 'H': airport.HEAVY}
    flights = []
    with open(filename) as file:
        for line in file:
            words = line.strip().split()
            dep = words[0] == "D"
            callsign = words[1]
            cat = cat_dict[words[2][1]]
            stand = apt.points_dict.get(words[3], None)
            qfu = words[4]
            runway = apt.qfu_dict.get(qfu, None)
            time = int(words[5]) // STEP
            slot = int(words[6]) // STEP if words[6] != "_" else None
            fpl = Flight(callsign, dep, cat, stand, runway, qfu, time, slot)
            track = file.readline().strip().split()
            fpl.route = get_xys(track[2:])
            flights.append(fpl)
    file.close()
    traffic = Traffic(filename, flights)
    print('Done.')
    return traffic

