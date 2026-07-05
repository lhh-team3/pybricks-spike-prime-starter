"""Mission 1: Go Out and Turn.

Drive forward 10 inches, turn all the way around (180 degrees) using
the gyro, and stop. After this mission the robot is facing back the
way it came — ready for Mission 2: Come Back Home.
"""

from robot import Robot, inches


def run(robot):
    robot.drive_base.straight(inches(10))  # drive forward 10 inches
    robot.drive_base.turn(180)  # turn around (gyro keeps it accurate)
    robot.drive_base.stop()


# Lets you run JUST this mission: open this file and press F5.
if __name__ == "__main__":
    run(Robot())
