# Pybricks SPIKE Prime Starter

A starter project for FIRST LEGO League teams programming a LEGO SPIKE
Prime robot with [Pybricks](https://pybricks.com/) (Python). Fork this
repository, tell it about your robot, and start writing missions!

What you get:

- **`robot.py`** — one file that describes your robot (ports, wheel size,
  attachments, sensors). Edit it once; every mission uses it.
- **A mission menu** (`main.py`) — pick and run missions right on the hub
  with the hub's buttons. No computer needed during a match.
- **Two sample missions** and a template for writing your own.

## One-time setup

### 1. Put Pybricks firmware on your hub

Follow the instructions at
[code.pybricks.com](https://code.pybricks.com/) to install the Pybricks
firmware on your SPIKE Prime hub. While installing, give your hub a
name (like `TeamBot`) — you'll use it below.

> You can always go back to the official LEGO firmware later using the
> LEGO SPIKE app.

### 2. Set up your computer

You need [Python 3.10+](https://www.python.org/downloads/) and
[VS Code](https://code.visualstudio.com/).

Open this folder in VS Code (it will suggest some extensions — install
them), then in a terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Tell VS Code your hub's name

Open `.vscode/settings.json` and change `"pybricks.robotName"` from
`"MyRobot"` to whatever you named your hub.

### 4. Tell the code about YOUR robot

Open `robot.py` and edit the section at the top:

- Which ports your **wheel motors** are plugged into.
- Your **wheel diameter** (printed on the tire: small SPIKE wheel = 56,
  big wheel = 88).
- Your **axle track** — the distance in millimeters between the centers
  of your two wheels. Measure it with a ruler.
- Your **attachment motor** port(s). If you only use one attachment
  motor, leave `ATTACHMENT_2_PORT = None`.
- Any **sensors** you have (color, distance, force). Leave them `None`
  if you don't have them.

## Running programs

Turn the hub on, then in VS Code open the file you want to run and
press **F5** (the "Pybricks: Run on Robot" configuration). The program
is sent to the hub over Bluetooth and runs there.

From the command line instead:

```bash
pybricksdev run --name YourHubName ble main.py
```

## The mission menu (`main.py`)

Run `main.py` on the hub and a number appears on the hub's screen:

| Button          | What it does                        |
| --------------- | ----------------------------------- |
| LEFT / RIGHT    | Pick a mission                      |
| CENTER          | Run the selected mission            |
| CENTER (again)  | Stop the mission while it's running |
| BLUETOOTH       | Exit the menu                       |

After a mission finishes, the menu automatically moves to the next
number — so in a match you can run your missions in order by just
pressing CENTER each time.

The sample missions:

1. **Go Out and Turn** — drives forward 10 inches, turns 180° using the
   gyro, and stops.
2. **Come Back Home** — drives forward 10 inches (which brings the
   robot home, since Mission 1 turned it around).

You can also run any single mission by opening its file and pressing
F5 — handy while you're testing.

## Writing a new mission

1. Copy `mission_template.py` and name it after your mission, like
   `mission_03_deliver_the_cargo.py`.
2. Write your moves inside the `run(robot)` function.
3. Add it to the menu in `main.py` — one import and one `add_item` line.

Common moves cheat-sheet:

```python
robot.drive_base.straight(inches(10))   # forward 10 inches
robot.drive_base.straight(inches(-5))   # backward 5 inches
robot.drive_base.turn(90)               # turn right 90 degrees
robot.drive_base.turn(-45)              # turn left 45 degrees
robot.attachment_1.run_angle(500, 180)  # spin attachment: speed, degrees
robot.hub.speaker.beep()                # beep!
```

See the [Pybricks documentation](https://docs.pybricks.com/) for
everything else your robot can do.

## Troubleshooting

- **Hub not found / connection times out** — Is the hub turned on and
  nearby? Does the name in `.vscode/settings.json` exactly match your
  hub's name? Is the hub already connected to something else (like the
  Pybricks web IDE)?
- **Robot drives backward** — Swap `CLOCKWISE` and `COUNTERCLOCKWISE`
  for the wheels in `robot.py`.
- **Robot curves when driving straight** — Double-check the wheel
  directions and `AXLE_TRACK_MM` in `robot.py`, and make sure both
  tires are the same size and clean.
- **Turns are off by a few degrees** — Keep the robot perfectly still
  for a second after the program starts so the gyro can settle.
- **`ImportError: no module named 'typing'`** — Your code runs on the
  hub, which doesn't have Python's full standard library. Only import
  from `pybricks.*` (see `menu.py` for the safe way to use typing).

## License

MIT — see [LICENSE](LICENSE).
