# Rocket Launch Simulator
 
A Python program that simulates a rocket flying straight up. You pick an engine and how long it burns. The rocket keeps its momentum after the engine shuts off, so it coasts upward, slows down, reaches its highest point, then falls back down. At the end you get graphs of the flight.
 
## What it simulates
 
- **Three engines:** solid rocket motor, kerosene/liquid oxygen, and hydrogen/liquid oxygen.
- **The same rocket for every engine:** 45,000 lb dry mass plus 255,000 lb of fuel (300,000 lb at liftoff), 12 ft wide.
- **Realistic air:** a three-zone atmosphere (troposphere, lower stratosphere, upper stratosphere) that gives air pressure and density at any altitude.
- **Gravity that changes with altitude:** it gets weaker the higher the rocket goes.
- **Air drag:** it slows the rocket down, and it fades as the air gets thin.
- **Engines that change with altitude:** thrust and efficiency (Isp) improve as the air thins.
- **Burning fuel:** the rocket gets lighter as fuel is used.
- **Momentum:** after the engine turns off, the rocket keeps its velocity.
## How to run it
 
1. Run the program:
```
   python rocket_simple.py
```
 
2. Choose an engine (1, 2 or 3), then type how many seconds the engine should burn.
The program prints the highest altitude, top speed, engine shutoff time and total flight time. It then shows five graphs and saves them as `rocket_flight.png`.
 
## The graphs
 
| Graph | What it shows |
|---|---|
| Altitude | How high the rocket is over time |
| Velocity | Speed up (positive) or down (negative) |
| Acceleration | Measured in g's; drops sharply when the engine shuts off |
| Thrust | The engine's push, which rises as the air thins |
| Mass | Total weight, dropping as fuel burns |
 
A red dashed line marks when the engine shut off.
 
## The engines
 
Based on real engines, scaled so each one fits the same rocket.
 
| # | Engine | Based on | Thrust (sea level / vacuum) | Isp (sea level / vacuum) |
|---|---|---|---|---|
| 1 | Solid rocket motor | Space Shuttle boosters | 420,000 / 465,000 lbf | 242 / 268 s |
| 2 | Kerosene / LOX | SpaceX Merlin 1D (2 engines) | 380,000 / 410,000 lbf | 282 / 311 s |
| 3 | Hydrogen / LOX | Space Shuttle main engine | 418,000 / 512,000 lbf | 366 / 452 s |
 
Isp (specific impulse) is how efficiently an engine uses fuel: higher means more push from the same amount of fuel.
 
## The atmosphere equations
 
Altitude `h` is in feet, temperature `T` in °F, pressure `p` in lb/ft².
 
| Zone | Altitude | Temperature | Pressure |
|---|---|---|---|
| Troposphere | 0 to 36,152 ft | `T = 59 - 0.00356h` | `p = 2116((T+459.7)/518.6)^5.256` |
| Lower stratosphere | 36,152 to 82,345 ft | `T = -70` | `p = 473.1e^(1.73 - 0.000048h)` |
| Upper stratosphere | above 82,345 ft | `T = -205.05 + 0.00164h` | `p = 51.97((T+459.7)/389.98)^-11.388` |
 
In every zone, air density is `rho = p / (1718(T + 459.7))`.
 
## How the code works
 
The program's core is the loop in `run_simulation()`. Every 0.05 seconds of flight it:
 
1. Looks up the air at the current altitude (`atmosphere()`).
2. Checks whether the engine is still on, and if so finds thrust and fuel use (`engine_output()`).
3. Works out the forces: thrust pushes up, drag pushes against the motion, gravity pulls down (`gravity()`).
4. Updates **acceleration, then velocity, then altitude**.
5. Saves the numbers in lists so they can be graphed.
Because velocity is only changed by acceleration, the rocket keeps moving after the engine stops. That is the momentum.
 
The file is organized in order: constants, engines, functions, the simulation, graphs, then the main program at the bottom.
 
## Limitations
 
- Straight-up flight only (one dimension), with no sideways motion or steering.
- The upper stratosphere equation is a curve fit that is not meant for very high altitudes. Very long burns that reach hundreds of miles up give less trustworthy results.
- There is no parachute, so the rocket hits the ground at full speed.
- The burn time is typed in before launch. The engine can't be stopped during the flight.
## Units
 
Feet, seconds, pounds, and degrees Fahrenheit throughout.
 
