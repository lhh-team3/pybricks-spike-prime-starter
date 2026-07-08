"""Starting point for a new mission.

To make a new mission:
  1. Copy this file and name it after your mission,
     like mission_03_deliver_the_cargo.py
  2. Write your robot's moves inside run() below.
  3. Add one line to the MENU_ITEMS list in menu_config.py, like:
        {"display": 3, "module": "mission_03_deliver_the_cargo", "function": "run"},
"""

from robot import Robot, inches


def run(robot):
    # TODO: Write your mission here! Some moves to try:
    #
    # Drive forward and backward (negative = backward):
    #     robot.drive_base.straight(inches(10))
    #     robot.drive_base.straight(inches(-5))
    #
    # Turn right or left (negative = left):
    #     robot.drive_base.turn(90)
    #     robot.drive_base.turn(-45)
    #
    # Move an attachment motor (speed in degrees/second, then angle):
    #     robot.attachment_1.run_angle(500, 180)
    #
    # Use a sensor (only if you set its port in robot.py):
    #     if robot.color_sensor.color() == Color.RED:
    #         robot.hub.speaker.beep()
    pass


# Lets you run JUST this mission: open this file and press F5.
if __name__ == "__main__":
    run(Robot())
