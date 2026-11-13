"""The list of missions your hub menu shows, in the order it shows them.

Each slot is a little dictionary with these keys:

    "display"   (required) What shows on the hub screen for this slot.
                A number 0-99, a single letter like "A", or a 5-row
                pixel pattern (list of 5 strings) — same as pix_display.
    "module"    (required) The name of the .py file to run, with no ".py"
                and no dots.
    "function"  (optional) The name of the function inside that file to
                call, like "run". Leave this key OUT to run the WHOLE
                file top-to-bottom instead (this is how block programs run).
    "blocks"    (optional, default False) Set to True for a function that
                comes from a block program's "My Block".
    "enabled"   (optional, default True) Set to False to hide a slot from
                the menu without deleting it from this list.

The ORDER of the list is the order the slots appear in the menu.

Heads up: the Pybricks Git extension's menu manager rewrites this file —
comments inside the MENU_ITEMS list are not kept.
"""

# Bundle hints: these imports never run (the "if" below is always false).
# They exist so your programs get uploaded to the hub along with main.py —
# the uploader only sends files it sees in a real "import" line.
#
# Leave the "_BUNDLE_HINTS" name alone: "if False:" would be deleted by the
# compiler and your programs would stop being uploaded.
_BUNDLE_HINTS = False
if _BUNDLE_HINTS:
    import AntMission
    import Canopy
    import ExplodingSeeds

MENU_ITEMS = [
    {"display": 1, "module": "AntMission"},
    {"display": 2, "module": "Canopy"},
    {"display": 3, "module": "ExplodingSeeds"},
]
