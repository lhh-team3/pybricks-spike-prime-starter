try:
    from typing import Union
except ImportError:
    pass

from pybricks.hubs import PrimeHub
from pybricks.parameters import Button, Icon
from pybricks.tools import Matrix, wait


class Patterns:
    numbers = [
        [" ### ", " # # ", " # # ", " # # ", " ### "],
        ["  #  ", " ##  ", "  #  ", "  #  ", " ### "],
        [" ### ", "   # ", " ### ", " #   ", " ### "],
        [" ### ", "   # ", " ### ", "   # ", " ### "],
        [" # # ", " # # ", " ### ", "   # ", "   # "],
        [" ### ", " #   ", " ### ", "   # ", " ### "],
        [" ### ", " #   ", " ### ", " # # ", " ### "],
        [" ### ", "   # ", "   # ", "   # ", "   # "],
        [" ### ", " # # ", " ### ", " # # ", " ### "],
        [" ### ", " # # ", " ### ", "   # ", " ### "],
        ["# ###", "# # #", "# # #", "# # #", "# ###"],
        [" #  #", "## ##", " #  #", " #  #", " #  #"],
        ["# ###", "#   #", "# ###", "# #  ", "# ###"],
        ["# ###", "#   #", "# ###", "#   #", "# ###"],
        ["# # #", "# # #", "# ###", "#   #", "#   #"],
        ["# ###", "# #  ", "# ###", "#   #", "# ###"],
        ["# ###", "# #  ", "# ###", "# # #", "# ###"],
        ["# ###", "#   #", "#   #", "#   #", "#   #"],
        ["# ###", "# # #", "# ###", "# # #", "# ###"],
        ["# ###", "# # #", "# ###", "#   #", "# ###"],
    ]

    @staticmethod
    def is_valid_pattern(pattern: list[str]):
        if len(pattern) != 5:
            return False
        for line in pattern:
            if len(line) != 5:
                return False
        return True


def display_pattern(hub: PrimeHub, pattern: list[str]):
    """
    Display a pattern on the hub using a visual representation.

    Args:
        hub: PrimeHub instance to display on.
        pattern: List of strings where each string represents a row.
                 Use '#' or anything other than space or zero to turn pixel on,
                 Use space or 0 to turn pixel off,
                 Use a number 1-9 to change the brightness.

    Example:
        display_pattern(hub, [
            "     ",
            " # # ",
            "     ",
            "#   #",
            " ### "
        ])
    """
    rows = []
    for row in pattern:
        pixels = []
        for char in row:
            if char == " ":
                pixels.append(0)
            else:
                try:
                    pixels.append(int(char) * 10)
                except ValueError:
                    pixels.append(100)
        rows.append(pixels)
    hub.display.icon(Matrix(rows))


def display_number(hub: PrimeHub, number: int):
    """
    Display a number (0-99) on the hub using a 5x5 pixel pattern.

    Args:
        hub: PrimeHub instance to display on.
        number: An integer from 0 to 99.
    """
    if number < 0 or number > 99:
        raise ValueError("Number must be between 0 and 99")

    if number < 10:
        hub.display.char(str(number))
    elif number < 20:
        display_pattern(hub, Patterns.numbers[number])
    else:
        hub.display.number(number)


def display_content(hub: PrimeHub, content: Union[str, int, list[str]]):
    if isinstance(content, int):
        if content > -100 and content < 100:
            if content < 0:
                hub.display.number(content)
            else:
                display_number(hub, content)
        else:
            raise ValueError("Number must be between -99 and 99")
    elif isinstance(content, str):
        hub.display.char(content[0])
    else:
        display_pattern(hub, content)


def run_number_selector():
    """
    Run an interactive number selector on the hub.
    Use LEFT/RIGHT buttons to cycle through numbers 0-25.
    Press CENTER button to exit.
    """
    hub = PrimeHub()
    selector = 0
    hub.display.char("?")
    hub.display.icon(
        Matrix(
            [
                [0, 20, 40, 20, 0],
                [20, 40, 60, 40, 20],
                [40, 60, 80, 60, 40],
                [20, 40, 60, 40, 20],
                [0, 20, 40, 20, 0],
            ]
        )
    )
    print(Icon.ARROW_DOWN)
    selector_increment = 0

    while True:
        if hub.buttons.pressed() & {Button.RIGHT, Button.LEFT}:
            if Button.RIGHT in hub.buttons.pressed():
                selector_increment = 1
            elif Button.LEFT in hub.buttons.pressed():
                selector_increment = -1
            while any(hub.buttons.pressed()):
                wait(10)
            selector = (selector + selector_increment) % 26
            display_number(hub, selector)
        wait(10)


if __name__ == "__main__":
    # Run the interactive number selector when this file is executed directly
    run_number_selector()
