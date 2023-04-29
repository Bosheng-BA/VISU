import tkinter
import airport
import traffic

# Items tags
SCALE = 'Scale'
POINT = 'Point'
LINE = 'Line'
RUNWAY = 'Runway'
PLOT = 'Plot'
POPUP = 'Popup'
ROUTE = 'Route'
CONFLICT = 'Conflict'

# Colors
DEP_COLOR = 'blue'
ARR_COLOR = 'magenta'
STOP_COLOR = "red"


class HMI(tkinter.Tk):
    """ HMI state """
    def __init__(self, the_airport, the_traffic):
        super().__init__()
        self.airport = the_airport      # Airport
        self.traffic = the_traffic      # Traffic
        self.time = self.traffic.t_min  # Current time in time steps
        self.last_xy = (0, 0)           # Last mouse position
        self.loop = False               # Animation loop ? (False | True)
        self.delay = 20                 # Animation steps (ms)
        # Create widgets
        self.title("ATOS {} {}".format(the_airport.name, the_traffic.name))
        self.canvas = tkinter.Canvas(self, width=1000, height=600,
                                     background='white')
        self.popup = tkinter.Label(self.canvas, background='yellow')
        cmd_frame = tkinter.Frame(self)
        self.time_entry = tkinter.Entry(cmd_frame)
        texts = ('<<', ' <', ' >', '>>')
        buttons = [tkinter.Button(cmd_frame, text=text) for text in texts]
        # Pack widgets
        cmd_frame.pack(side=tkinter.BOTTOM)
        self.canvas.pack(expand=True, fill=tkinter.BOTH)
        for button in buttons[:2]: button.pack(side=tkinter.LEFT)
        self.time_entry.pack(side=tkinter.LEFT)
        for button in buttons[2:]: button.pack(side=tkinter.LEFT)
        # Bind events
        self.canvas.bind('<Motion>', lambda event: mouse_motion(self, event))
        self.canvas.bind('<Button-1>', lambda event: select(self, event))
        self.canvas.bind('<Button1-Motion>', lambda event: drag(self, event))
        self.canvas.bind('<Double-ButtonPress-1>', lambda _: rescale(self))
        self.canvas.bind('<Button-4>', lambda event: scale(self, 1.1, event))
        self.canvas.bind('<Button-5>', lambda event: scale(self, 1/1.1, event))
        self.canvas.bind('<MouseWheel>', lambda event: wheelscale(self, event))
        self.canvas.bind('<KeyPress>', lambda event: key(self, event))
        buttons[0].configure(command=lambda: switch_loop(self, -1))
        buttons[1].configure(command=lambda: forward(self, -1))
        buttons[2].configure(command=lambda: forward(self, 1))
        buttons[3].configure(command=lambda: switch_loop(self, 1))
        self.time_entry.bind('<Return>', lambda event: set_time(self))
        self.canvas.focus_set()
        # Canvas scale reference
        self.canvas.create_line(((0.0, 0.0), (1.0, -1.0)), fill='', tag=SCALE)


def item_tags(tag, i):
    """ Tags for a canvas item representing ('tag', 'i') """
    return [' '.join([tag, str(i)]), tag]


def tag_i(tags):
    """ Extract (tag, i) from a canvas item with tags 'tags' """
    try:
        (tag, str_i) = tags[0].split(' ')
        return tag, int(str_i)
    except (IndexError, ValueError):
        return '', 0


def map_xys(hmi, xys):
    """ Convert world 'xys' to the 'hmi' canvas coordinates """
    (x0, y0, x1, y1) = hmi.canvas.coords(SCALE)
    dx = x1 - x0
    dy = y1 - y0
    return [(x0 + dx * x, y0 + dy * y) for (x, y) in xys]


def world_xys(hmi, xys):
    """ Convert canvas 'xys' to world coordinates """
    (x0, y0, x1, y1) = hmi.canvas.coords(SCALE)
    dx = x1 - x0
    dy = y1 - y0
    return [(int((x - x0) / dx), int((y - y0) / dy)) for (x, y) in xys]


def rescale(hmi):
    """ Rescale the 'hmi' canvas to show all lines """
    hmi.canvas.update()
    bbox = hmi.canvas.bbox(LINE)
    if len(bbox) == 4:
        (x1, y1, x2, y2) = bbox
        (xm, ym) = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        (width, height) = (hmi.canvas.winfo_width(), hmi.canvas.winfo_height())
        (wm, hm) = (width / 2.0, height / 2.0)
        hmi.canvas.move('all', wm - xm, hm - ym)
        zoom = 0.9 * min(width / float(x2 - x1), height / float(y2 - y1))
        hmi.canvas.scale('all', wm, hm, zoom, zoom)


def draw_airport(hmi):
    """ Draw the airport on the 'hmi' canvas """
    canvas = hmi.canvas
    # Runways
    for (i, runway) in enumerate(hmi.airport.runways):
        canvas.create_line(map_xys(hmi, runway.xys), tags=item_tags(RUNWAY, i))
    # Lines
    for (i, line) in enumerate(hmi.airport.lines):
        canvas.create_line(map_xys(hmi, line.xys), tags=item_tags(LINE, i))
    # Named points
    for (i, point) in enumerate(hmi.airport.points):
        xys = 2 * map_xys(hmi, (point.xy,))
        pt_tags = item_tags(POINT, i)
        color = 'darkgrey' if point.ptype == airport.STAND else 'grey'
        if point.ptype == airport.STAND:
            canvas.create_oval(xys, fill=color, outline=color, tags=pt_tags)
        else:
            canvas.create_rectangle(xys, fill=color, outline=color, 
                                    tags=pt_tags)
    # Item aspects
    canvas.itemconfigure(RUNWAY, fill='grey', activefill='yellow', width=5)
    canvas.itemconfigure(LINE, fill='grey', activefill='yellow', width=3)
    canvas.itemconfigure(POINT, activeoutline='yellow', width=7)
    rescale(hmi)


def draw_traffic(hmi):
    """ Draw the 'hmi' traffic situation """
    
    # Current time
    hmi.time_entry.delete(0, tkinter.END)
    hmi.time_entry.insert(0, traffic.to_hms(hmi.time))
    # Aircraft plots
    hmi.canvas.delete(PLOT)
    for (i, coords) in hmi.traffic.get_plots(hmi.time):
        xy = map_xys(hmi, [coords])
        fpl = hmi.traffic.flights[i]
        color = STOP_COLOR if fpl.stop(hmi.time) else DEP_COLOR if fpl.dep else ARR_COLOR
        width = 11 if fpl.cat == airport.HEAVY else 9
        tags = item_tags(PLOT, i)
        hmi.canvas.create_oval(xy * 2, 
                               width=width,
                               fill=color,
                               outline=color,
                               activeoutline='yellow',
                               tags=tags)
        txt = hmi.canvas.create_text(xy, text=fpl.callsign,
                                     anchor="sw", tags=tags)
        rct = hmi.canvas.create_rectangle(hmi.canvas.bbox(txt),
                                          outline="black", fill="white",
                                          tags=tags)
        hmi.canvas.lower(txt, PLOT)
        hmi.canvas.lower(rct, txt)


def draw_route(hmi, i):
    """ Draw the route of a flight on the 'hmi' canvas """
    fpl = hmi.traffic.flights[i]
    xys = map_xys(hmi, (xy for xy, _ in fpl.route))
    color = DEP_COLOR if fpl.dep else ARR_COLOR
    hmi.canvas.create_line(xys, fill=color, width=3, tags=item_tags(ROUTE, i))
    hmi.canvas.lower(ROUTE, PLOT)


def popup(hmi, info, xy):
    """ Popup some 'info' on the 'hmi' canvas at 'xy'"""
    if info == '':
        hmi.canvas.delete(POPUP)
    else:
        hmi.popup.configure(text=info)
        if hmi.canvas.gettags(POPUP) == ():
            hmi.canvas.create_window(xy, window=hmi.popup, tag=POPUP)
        else:
            hmi.canvas.coords(POPUP, xy)


# Events commands

def mouse_motion(hmi, event):
    """ POPUP information on the 'hmi' element pointed by mouse """
    hmi.last_xy = (event.x, event.y)
    (tag, i) = tag_i(hmi.canvas.gettags('current'))
    info = ''
    if tag != '':
        if tag == POINT:
            point = hmi.airport.points[i]
            info = point.ptype + ' ' + point.name
        elif tag == LINE: 
            line = hmi.airport.lines[i]
            ttype = "Pushback" if line.speed < 0 else "Taxi"
            info = "{} {} {}m/s".format(ttype, line.taxiway,  abs(line.speed))
        elif tag == RUNWAY: 
            info = 'Runway ' + hmi.airport.runways[i].name
        elif tag in (PLOT, ROUTE):
            fpl = hmi.traffic.flights[i]
            time = traffic.to_hms(fpl.time)
            ctot = "CTOT:" + traffic.to_hms(fpl.slot) if fpl.slot else ""
            arrdep = "DEP" if fpl.dep else "ARR"
            info = ' '.join([arrdep, fpl.callsign, fpl.cat, time, ctot])
        elif tag == CONFLICT:
            (flight1, flight2) = hmi.conflicts[i]
            info = flight1.callsign + '<->' + flight2.callsign
    popup(hmi, info, (event.x, event.y + 40))


def select(hmi, event):
    """ Select the 'hmi' current element """
    hmi.last_xy = (event.x, event.y)
    hmi.canvas.focus_set()
    (tag, i) = tag_i(hmi.canvas.gettags('current'))
    if tag == PLOT:
        route_tag = item_tags(ROUTE, i)[0]
        if hmi.canvas.gettags(route_tag) == ():
            draw_route(hmi, i)
        else: 
            hmi.canvas.delete(route_tag)
    elif tag == POINT:
        print([flight.callsign 
               for flight in hmi.traffic.flights
               if flight.stand == i])
    elif tag == '':
        hmi.canvas.delete(ROUTE)
        popup(hmi, world_xys(hmi, [hmi.last_xy]), hmi.last_xy)


def drag(hmi, event):
    """ Drag the 'hmi' map according to mouse motion """
    (x, y) = hmi.last_xy
    hmi.canvas.move(tkinter.ALL, event.x - x, event.y - y)
    hmi.last_xy = (event.x, event.y)


def scale(hmi, factor, event):
    """ Zoom the 'hmi' map by 'factor' """
    hmi.canvas.scale(tkinter.ALL, event.x, event.y, factor, factor)
    draw_traffic(hmi)


def wheelscale(hmi, event):
    factor = (-100 / event.delta) if event.delta < 0 else (event.delta / 100)
    scale(hmi, factor, event)

    
def forward(hmi, dt):
    """ Forward 'hmi' time by one step of 'dt' """
    t_min = hmi.traffic.t_min
    hmi.time = max(t_min, min(t_min + len(hmi.traffic.ids) - 1, hmi.time + dt))
    hmi.loop = False
    draw_traffic(hmi)


def animation_loop(hmi, dt):
    """ 'hmi' animation loop by time steps of 'dt' """
    if hmi.loop:
        next_t = hmi.time + dt
        if 0 <= next_t - hmi.traffic.t_min < len(hmi.traffic.ids):
            hmi.time = next_t
            draw_traffic(hmi)
            hmi.canvas.after(hmi.delay, animation_loop, hmi, dt)
        else:
            hmi.loop = False


def switch_loop(hmi, dt):
    """ Switch on/off the 'hmi' animation loop by steps of 'dt' """
    hmi.loop = not hmi.loop
    if hmi.loop:
        animation_loop(hmi, dt)


def set_time(hmi):
    """ Set 'hmi' time according to the 'hmi' time entry """
    hmi.time = traffic.to_time(hmi.time_entry.get())
    hmi.canvas.focus_set()
    forward(hmi, 0)


def key(hmi, event):
    """ Actions of the 'hmi' after a key 'event' """
    if event.keysym == 'space':
        rescale(hmi)
    elif event.keysym == 'Up':
        hmi.canvas.move(tkinter.ALL, 0, -20)
    elif event.keysym == 'Down':
        hmi.canvas.move(tkinter.ALL, 0, 20)
    elif event.keysym == 'Left':
        hmi.canvas.move(tkinter.ALL, -20, 0)
    elif event.keysym == 'Right':
        hmi.canvas.move(tkinter.ALL, 20, 0)
    elif event.keysym in ['KP_Add', 'plus', 'KP_Subtract', 'minus']:
        factor = 1.1 if event.keysym in ['KP_Add', 'plus'] else (1.0 / 1.1)
        scale(hmi, factor, event)
    elif event.keysym in ['n', 'b']:
        forward(hmi, 1 if event.keysym == 'n' else -1)
    elif event.keysym in ['N', 'B']:
        switch_loop(hmi, 1 if event.keysym == 'N' else -1)
    elif event.keysym == 'q':
        hmi.canvas.winfo_toplevel().destroy()
    else:
        print(event.keysym)
