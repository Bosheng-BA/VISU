# Points types
STAND = "Stand"
DEICING = "Deicing"
RUNWAY = "Runway"
LINEPOINT = "Linepoint"

# Wake turbulence categories
LIGHT = "Light"
MEDIUM = "Medium"
HEAVY = "Heavy"

# Speeds parameters
VMIN = 3      # m/s
VMAX = 10     # m/s
RADIUS = 100  # Min turn radius for VMAX

class Point(object):
    """Named point of the airport"""
    def __init__(self, name, ptype, xy):
        self.name = name    # Point name (str)
        self.ptype = ptype  # Point type (STAND | DEICING | RUNWAY)
        self.xy = xy        # (x, y) coordinates (meters)
    

class Line(object):
    """Taxiway portion of the airport"""
    def __init__(self, taxiway, speed, oneway, xys):
        self.taxiway = taxiway  # Taxiway name (str)
        self.speed = speed      # Average speed (m/s)
        self.oneway = oneway    # One way portion ? (bool)
        self.xys = xys          # [(x, y), ...] coordinates (meters)


class Runway(object):
    """Runway of the airport"""
    def __init__(self, name, points, xys):
        qfus = name.split('-')
        self.name = name      # Runway name (str)
        self.qfu1 = qfus[0]   # QFU1 name (str)
        self.qfu2 = qfus[1]   # QFU2 name (str)
        self.points = points  # [pt_name, ...] Runway points
        self.xys = xys        # [(x1, y1), (x2, y2)] coordinates (meters)


class Airport(object):
    """Airport description"""
    def __init__(self, name, points, lines, runways):
        self.name = name        # Name
        self.points = points    # Named points
        self.lines = lines      # Lines
        self.runways = runways  # Runways
        # Points index by name and Runway index by QFU name
        self.points_dict = {point.name: i for (i, point) in enumerate(points)}
        self.qfu_dict = {qfu: i
                         for (i, runway) in enumerate(runways)
                         for qfu in (runway.qfu1, runway.qfu2)}
        
# Load an airport description file

def get_xy(str_xy):
    """ Convert a x,y string 'str_xy' to coordinates """
    (str_x, str_y) = str_xy.split(',')
    return int(float(str_x)), int(float(str_y))


def get_xys(str_xy_list):
    """ Convert a x,y string list 'str_xy_list' to coordinates """
    return [get_xy(str_xy) for str_xy in str_xy_list]


def load(filename):
    """Load an airport description 'file' and return the airport"""
    print('Loading airport:', filename + '...', end='')
    file = open(filename)
    points, lines, runways = [], [], []
    name = "ZBTJ"
    for line in file:
        words = line[:-1].strip().split(' ')
        if words[0] == "p":  # Point description
            ptype = STAND if words[3] == "Parking" else RUNWAY
            point = Point(words[1], ptype, get_xy(words[2]))
            points.append(point)
        elif words[0] == 'l':  # Line description
            taxiway = "" if words[1] == "tw" else words[1]
            radius = float(words[4])
            if words[2] == "pushback": speed = -VMIN
            elif radius == 0 or RADIUS < radius: speed = VMAX
            else: speed = max(VMIN, min(VMAX, int(VMAX * radius / RADIUS)))
            oneway = words[3] == 'S'
            line = Line(taxiway, speed, oneway, get_xys(words[5:]))
            lines.append(line)
        elif words[0] == "runway":  # Runway description
            runway = Runway(words[1], [], get_xys(words[2:]))
            runways.append(runway)
        elif words[0] in ("", "#", "qfu"): pass
        else:
            print("\""+words[0]+"\"")
            raise Exception("airport.load: unexpected line\n" + line)
    file.close()
    airport = Airport(name, points, lines, runways)
    # loadRSA(airport)
    print('Done.')
    return airport


def load2(filename):
    """Load an airport description 'file' and return the airport"""
    print('Loading airport:', filename + '...', end='')
    file = open(filename)
    points, lines, runways = [], [], []
    name = "ZBTJ"
    for line in file:
        words = line[:-1].strip().split(' ')
        if words[0] == "p":  # Point description
            ptype = STAND if words[3] == "Parking" else RUNWAY
            point = Point(words[1], ptype, get_xy(words[2]))
            points.append(point)
        elif words[0] == 'l':  # Line description
            ptype = words[2]  # Add the points of lines
            point1 = Point(words[1], ptype, get_xy(words[5]))
            point2 = Point(words[1], ptype, get_xy(words[-1]))
            points.append(point1)
            points.append(point2)
            taxiway = "" if words[1] == "tw" else words[1]
            radius = float(words[4])
            if words[2] == "pushback": speed = -VMIN
            elif radius == 0 or RADIUS < radius: speed = VMAX
            else: speed = max(VMIN, min(VMAX, int(VMAX * radius / RADIUS)))
            oneway = words[3] == 'S'
            # change all line to straight line
            extreme_points = [words[5], words[-1]]
            line = Line(taxiway, speed, oneway, get_xys(extreme_points))
            lines.append(line)
        elif words[0] == "runway":  # Runway description
            runway = Runway(words[1], [], get_xys(words[2:]))
            runways.append(runway)
            ptype = RUNWAY  # Add the points of runways
            # point = points
            point1 = Point(words[1], ptype, get_xy(words[2]))
            point2 = Point(words[1], ptype, get_xy(words[3]))  # 名字处理的有点问题
            points.append(point1)
            points.append(point2)
        elif words[0] in ("", "#", "qfu"): pass
        else:
            print("\""+words[0]+"\"")
            raise Exception("airport.load: unexpected line\n" + line)
        """New part"""  # 处理重复的Point，因为每一条line的端点被计算两遍
        grouped_points = {}
        for p in points:
            if p.xy in grouped_points:
                if p.ptype in 'Stand':
                    grouped_points[p.xy] = p
                    # print(p.xy)
                elif p.ptype in ('Runway', 'pushback') and grouped_points[p.xy].ptype not in 'Stand':
                    grouped_points[p.xy] = p
                    # print(p.xy)
            else:
                grouped_points[p.xy] = p
        points = list(grouped_points.values())
    file.close()

    airport = Airport(name, points, lines, runways)
    print('Done.')
    return airport

