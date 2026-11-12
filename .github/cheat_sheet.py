"""Make a printable cheat sheet of where each mission's robot starts.

Runs on a computer (or on GitHub), NOT on the hub.

    python3 .github/cheat_sheet.py

It reads menu_config.py to learn which missions are in the menu and in
what order, then looks in each mission file for its R.A.P. comment:

    R: where the Robot goes and which way it faces
    A: which Attachment is on, and how it starts
    P: the Program number (ignored — the menu is the source of truth)

Both of these styles work, with or without the colon:

    Python missions — lines in the docstring:      R: left of the first line
    Block programs  — comment blocks (# lines):    # R left of the first line

The result is cheat_sheet.html. Open it in a browser and print it.
"""

import ast
import html
import os
import re
import sys

# "R: text", "R - text" or "R text" (same for A and P), capital letters only.
_RAP_LINE = re.compile(r"^([RAP])(?:\s*[:\-]\s*|\s+|$)(.*)$")


def find_rap(lines):
    """Return {"R": ..., "A": ..., "P": ...} from the first R.A.P. comment
    in lines, or None if there isn't one.

    It only counts when an R line is followed by an A line, so an ordinary
    sentence that happens to start with "A " is not mistaken for one.
    """
    for start in range(len(lines)):
        found = {}
        letter = None
        in_comment = lines[start].strip().startswith("#")
        for line in lines[start:]:
            text = line.strip()
            # A comment block ends at the first code line; a docstring
            # ends at a blank line or its closing quotes.
            if text.startswith("#") != in_comment:
                break
            text = text.lstrip("#").strip()
            if not text or text.startswith(('"""', "'''")):
                break
            match = _RAP_LINE.match(text)
            if match and match.group(1) not in found:
                letter = match.group(1)
                found[letter] = match.group(2).strip()
            elif letter is None or letter == "P":
                break
            else:
                # A long R or A that wrapped onto the next line.
                found[letter] = (found[letter] + " " + text).strip()
            if list(found) == ["A"] or list(found) == ["P"]:
                break  # has to begin with the R line
        if "R" in found and "A" in found:
            return found
    return None


def function_lines(lines, name):
    """Return just the lines of the top-level function called name."""
    start = None
    for i, line in enumerate(lines):
        if re.match(r"(async\s+)?def\s+%s\s*\(" % re.escape(name), line):
            start = i
        elif start is not None and line[:1] not in ("", " ", "\t", "#"):
            return lines[start:i]
    return lines[start:] if start is not None else []


def menu_items(root):
    """Read MENU_ITEMS out of menu_config.py without running the file."""
    with open(os.path.join(root, "menu_config.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "MENU_ITEMS":
            return ast.literal_eval(node.value)
    raise SystemExit("menu_config.py has no MENU_ITEMS list.")


def display_html(display):
    """Show the menu's "display" the way the hub does."""
    if isinstance(display, list):
        # A 5-row pixel pattern: draw lit pixels as blocks.
        rows = ["".join("·" if c in " 0" else "█" for c in row) for row in display]
        return "<pre>%s</pre>" % html.escape("\n".join(rows))
    return html.escape(str(display))


def build_rows(root):
    """Return one (display, program name, R, A) row per enabled menu slot."""
    rows = []
    for item in menu_items(root):
        if not item.get("enabled", True):
            continue
        file_name = item["module"] + ".py"
        function = item.get("function")
        program = item["module"]
        if function and function != "run":
            program += "." + function
        try:
            with open(os.path.join(root, file_name), encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError:
            print("::warning::%s is in the menu but the file is missing." % file_name)
            rows.append((item["display"], program, None, file_name + " is missing"))
            continue
        # Block files keep their whole workspace in a huge line 1 — skip it.
        if lines and lines[0].startswith("# pybricks blocks file:"):
            lines = lines[1:]

        # Prefer a comment inside the slot's own function (so two My Blocks
        # in one file can each have their own), then anywhere in the file.
        rap = function and find_rap(function_lines(lines, function))
        rap = rap or find_rap(lines)
        if rap is None:
            print("::warning file=%s::No R.A.P. comment found." % file_name)
            rows.append((item["display"], program, None, "No R.A.P. comment in " + file_name))
            continue
        if "P" in rap and rap["P"] != str(item["display"]):
            print(
                "::warning file=%s::Its comment says P %s but the menu shows it as %s."
                % (file_name, rap["P"], item["display"])
            )
        rows.append((item["display"], program, rap["R"], rap["A"]))
    return rows


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Robot start cheat sheet</title>
<style>
  /* Every size below is in "em", so changing the body font size
     scales the whole sheet. */
  body { font: 12pt/1.3 sans-serif; margin: 1em; color: #000; background: #fff; }
  h1 { font-size: 1.3em; margin: 0 0 0.4em; }
  table { width: 100%%; border-collapse: collapse; table-layout: fixed; }
  th, td { border: 1px solid #000; padding: 0.25em 0.4em; text-align: left;
           vertical-align: top; overflow-wrap: anywhere; }
  th { background: #ddd; }
  tr { break-inside: avoid; }
  .num { width: 3.2em; text-align: center; font-weight: bold; font-size: 1.4em; }
  .program { width: 22%%; }
  .attachment { width: 22%%; }
  .missing { font-style: italic; }
  pre { font-size: 0.45em; line-height: 1; margin: 0; }
  footer { font-size: 0.7em; margin-top: 0.5em; }
  .controls { margin-bottom: 1em; padding: 0.5em; background: #eee; font-size: 12pt; }
  @page { margin: 1cm; }
  @media print { .controls { display: none; } body { margin: 0; } }
</style>
</head>
<body>
<div class="controls">
  <label>Text size
    <input type="range" min="6" max="24" value="12"
      oninput="document.body.style.fontSize = this.value + 'pt'">
  </label>
  <button onclick="window.print()">Print</button>
  — slide until it all fits on one page (check the print preview).
</div>
<h1>Robot start cheat sheet</h1>
<table>
<tr><th class="num">#</th><th class="program">Program</th>
<th>R — Robot position</th><th class="attachment">A — Attachment</th></tr>
%s
</table>
<footer>%s</footer>
</body>
</html>
"""


def build_page(rows):
    table_rows = []
    for display, program, robot, attachment in rows:
        if robot is None:
            # Nothing to show — "attachment" holds the reason why.
            cells = '<td class="missing" colspan="2">%s</td>' % html.escape(attachment)
        else:
            cells = "<td>%s</td><td>%s</td>" % (html.escape(robot), html.escape(attachment))
        table_rows.append(
            '<tr><td class="num">%s</td><td>%s</td>%s</tr>'
            % (display_html(display), html.escape(program), cells)
        )
    # On GitHub, note which repo and commit this sheet was made from.
    made_from = "%s %s" % (
        os.environ.get("GITHUB_REPOSITORY", ""),
        os.environ.get("GITHUB_SHA", "")[:7],
    )
    return PAGE % ("\n".join(table_rows), html.escape(made_from.strip()))


def self_check():
    """python3 .github/cheat_sheet.py --test"""
    python_style = ['"""Mission 1:', "R: by the", "wall", "A: Forks", "P: 1", '"""']
    assert find_rap(python_style) == {"R": "by the wall", "A": "Forks", "P": "1"}
    block_style = ["x = 1", "    # R South wall", "    # A None", "    go()"]
    assert find_rap(block_style) == {"R": "South wall", "A": "None"}
    assert find_rap(['"""A number 0-99.', "P is for program", '"""']) is None
    two = ["def a():", "    # R one", "    # A x", "def b():", "    # R two", "    # A y"]
    assert find_rap(function_lines(two, "b"))["R"] == "two"
    assert display_html(["1   1"] * 5).count("█") == 10
    print("cheat_sheet.py self-check passed.")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        self_check()
        sys.exit()
    # Optional arguments: the repo folder to read, then the file to write.
    here = os.path.dirname(os.path.abspath(__file__))
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(here)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "cheat_sheet.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_page(build_rows(root)))
    print("Wrote", out)
