"""Competition program: shows a menu of all your missions on the hub.

Buttons:
    LEFT / RIGHT  — pick a mission (the number shows on the hub's screen)
    CENTER        — run the selected mission
    CENTER again  — stop a mission while it is running
    BLUETOOTH     — exit the menu

After a mission finishes, the menu automatically moves to the next one,
so during a match you can just keep pressing CENTER.
"""

from menu import Menu
from robot import Robot

import mission_01_go_out_and_turn
import mission_02_come_back_home

robot = Robot()
menu = Menu(robot.hub, context=robot)

# To add a mission: import its file above, then add one line here.
# The number is what shows on the hub's screen (0-99).
menu.add_item(1, mission_01_go_out_and_turn.run)
menu.add_item(2, mission_02_come_back_home.run)

menu.run(auto_increment=True)
