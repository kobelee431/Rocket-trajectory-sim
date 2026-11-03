"""
Simple Rocket Launch Simulator (straight up)
============================================

How it works (the big idea):
    Every tiny time step (0.05 seconds) we
      1. look up the air at the rocket's altitude   (your atmosphere equations)
      2. find the forces: thrust (up), drag (against motion), gravity (down)
      3. use the forces to update acceleration -> velocity -> altitude
      4. save the numbers so we can graph them at the end

    After the engine shuts off the rocket KEEPS ITS VELOCITY (momentum), so it
    coasts upward, slows down, stops at its highest point, then falls back down.

Units: feet, seconds, pounds, degrees Fahrenheit.
Needs: matplotlib   (install with:  pip install matplotlib)
"""

import math
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 1. Numbers that never change
# ----------------------------------------------------------------------
G0 = 32.174              # gravity at the ground (ft/s^2)
EARTH_RADIUS = 20902231  # radius of the Earth (ft)

# The SAME rocket is used for every engine
DRY_MASS = 45000         # rocket with no fuel (lb)
FUEL_MASS = 255000       # fuel we start with (lb)
AREA = 113               # front area of a 12 ft wide rocket (ft^2)
DRAG_COEFF = 0.3         # how "slippery" the rocket is (smaller = less drag)

TIME_STEP = 0.05         # seconds per step of the simulation

# ----------------------------------------------------------------------
# 2. The three engines
#    thrust is in pounds of force, isp (efficiency) is in seconds.
#    Each has a value at sea level and a value in a vacuum.
# ----------------------------------------------------------------------
ENGINES = {
    "1": {"name": "Solid rocket motor (like the Space Shuttle boosters)",
          "thrust_sea": 420000, "thrust_vac": 465000,
          "isp_sea": 242, "isp_vac": 268},
    "2": {"name": "Kerosene / liquid oxygen (like SpaceX Merlin)",
          "thrust_sea": 380000, "thrust_vac": 410000,
          "isp_sea": 282, "isp_vac": 311},
    "3": {"name": "Hydrogen / liquid oxygen (like the Space Shuttle main engine)",
          "thrust_sea": 418000, "thrust_vac": 512000,
          "isp_sea": 366, "isp_vac": 452},
}


# ----------------------------------------------------------------------
# 3. Functions
# ----------------------------------------------------------------------
def atmosphere(h):
    """Give back the air pressure and air density at altitude h (feet).
    The air has three zones, each with its own equations."""
    if h < 36152:                       # troposphere
        temp = 59 - 0.00356 * h
        pressure = 2116 * ((temp + 459.7) / 518.6) ** 5.256
    elif h < 82345:                     # lower stratosphere
        temp = -70
        pressure = 473.1 * math.exp(1.73 - 0.000048 * h)
    else:                               # upper stratosphere
        temp = -205.05 + 0.00164 * h
        pressure = 51.97 * ((temp + 459.7) / 389.98) ** -11.388

    density = pressure / (1718 * (temp + 459.7))
    return pressure, density


def gravity(h):
    """Gravity gets weaker the higher you go."""
    return G0 * (EARTH_RADIUS / (EARTH_RADIUS + h)) ** 2


def engine_output(engine, pressure):
    """Thrust and isp change with air pressure: the thinner the air,
    the closer the engine gets to its 'vacuum' numbers."""
    ratio = pressure / 2116                    # 1 at sea level, 0 in space
    if ratio > 1:
        ratio = 1
    thrust = engine["thrust_vac"] - (engine["thrust_vac"] - engine["thrust_sea"]) * ratio
    isp = engine["isp_vac"] - (engine["isp_vac"] - engine["isp_sea"]) * ratio
    return thrust, isp


def choose_engine():
    """Ask the user which engine they want."""
    print("Choose an engine:")
    for number in ENGINES:
        print(" ", number, "-", ENGINES[number]["name"])
    choice = input("Enter 1, 2 or 3: ")
    while choice not in ENGINES:
        choice = input("Please enter 1, 2 or 3: ")
    return ENGINES[choice]


def choose_burn_time():
    """Ask how many seconds the engine should stay on."""
    while True:
        try:
            seconds = float(input("How many seconds should the engine burn? "))
            if seconds >= 0:
                return seconds
            print("Time can't be negative.")
        except ValueError:
            print("Please type a number.")


# ----------------------------------------------------------------------
# 4. The simulation
# ----------------------------------------------------------------------
def run_simulation(engine, burn_time):
    time = 0.0
    altitude = 0.0
    velocity = 0.0
    mass = DRY_MASS + FUEL_MASS          # total weight of the rocket (lb)

    # Lists to remember everything for the graphs
    times = []
    altitudes = []
    velocities = []
    accelerations = []
    thrusts = []
    masses = []

    while time < 20000:
        pressure, density = atmosphere(altitude)

        # Is the engine on? It turns off when time is up OR the fuel runs out.
        if time < burn_time and mass > DRY_MASS:
            thrust, isp = engine_output(engine, pressure)
            fuel_burned = thrust / isp * TIME_STEP      # pounds of fuel this step
        else:
            thrust = 0
            fuel_burned = 0

        # Forces
        drag = 0.5 * density * velocity * abs(velocity) * DRAG_COEFF * AREA
        mass_in_slugs = mass / G0                       # physics needs slugs, not pounds
        acceleration = (thrust - drag) / mass_in_slugs - gravity(altitude)

        # If the rocket is sitting on the ground and can't lift off, it stays put
        if altitude == 0 and acceleration < 0:
            acceleration = 0

        # Save this moment
        times.append(time)
        altitudes.append(altitude)
        velocities.append(velocity)
        accelerations.append(acceleration / G0)         # shown in "g's"
        thrusts.append(thrust)
        masses.append(mass)

        # Move forward one step in time
        velocity = velocity + acceleration * TIME_STEP  # momentum is kept here!
        altitude = altitude + velocity * TIME_STEP
        mass = max(mass - fuel_burned, DRY_MASS)
        time = time + TIME_STEP

        # Stop when the rocket is back on the ground (or never left it)
        if altitude <= 0 and velocity <= 0:
            break

    return times, altitudes, velocities, accelerations, thrusts, masses


# ----------------------------------------------------------------------
# 5. Graphs
# ----------------------------------------------------------------------
def make_graphs(engine, burn_time, data):
    times, altitudes, velocities, accelerations, thrusts, masses = data

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle(engine["name"] + "  -  engine burn time: " + str(burn_time) + " s")

    # Each graph: (position, list of values, title, y-axis label)
    graphs = [
        (axes[0][0], altitudes, "Altitude", "feet"),
        (axes[0][1], velocities, "Velocity (up is positive)", "feet per second"),
        (axes[0][2], accelerations, "Acceleration", "g's"),
        (axes[1][0], thrusts, "Thrust", "pounds of force"),
        (axes[1][1], masses, "Mass (fuel burning off)", "pounds"),
    ]
    for ax, values, title, label in graphs:
        ax.plot(times, values)
        ax.set_title(title)
        ax.set_xlabel("time (seconds)")
        ax.set_ylabel(label)
        ax.grid(True)
        # dashed line where the engine turned off
        ax.axvline(burn_time_actual(thrusts, times), color="red", linestyle="--")

    fig.delaxes(axes[1][2])      # we only have 5 graphs, so remove the empty 6th box
    plt.tight_layout()
    plt.savefig("rocket_flight.png")
    plt.show()


def burn_time_actual(thrusts, times):
    """Find the moment the engine actually shut off."""
    last_on = 0
    for i in range(len(thrusts)):
        if thrusts[i] > 0:
            last_on = times[i]
    return last_on


# ----------------------------------------------------------------------
# 6. Main program
# ----------------------------------------------------------------------
print("=== Rocket Launch Simulator ===")
engine = choose_engine()
burn_time = choose_burn_time()

data = run_simulation(engine, burn_time)
times, altitudes, velocities, accelerations, thrusts, masses = data

print()
if max(altitudes) < 1:
    print("The rocket never left the ground.")
else:
    print("Highest altitude:", round(max(altitudes)), "feet")
    print("Fastest speed:   ", round(max(velocities)), "feet per second")
    print("Engine shut off at", round(burn_time_actual(thrusts, times), 1), "seconds")
    print("Total flight time:", round(times[-1]), "seconds")

make_graphs(engine, burn_time, data)