"""Mission 2: Come Back Home.

Drive forward 10 inches. Run this after Mission 1 (Go Out and Turn):
since the robot already turned around, driving forward brings it back
to where it started.
"""

from robot import Robot, inches


def run(robot):
    robot.drive_base.straight(inches(10))  # drive forward 10 inches
    robot.drive_base.stop()


# Lets you run JUST this mission: open this file and press F5.
if __name__ == "__main__":
    run(Robot())
