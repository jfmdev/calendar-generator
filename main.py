import calendar

from browser import document


# ---- Utilities ---- #

DAY_NAMES = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

MONTH_SEPARATION = 10

def parse_int(value, default, minimum=None, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default

    if minimum is not None and parsed < minimum:
        parsed = minimum
    if maximum is not None and parsed > maximum:
        parsed = maximum
    return parsed

# ---- State management ---- #

# TODO: State should be stored in the local storage and loaded on page load.
state = {
    "include_day_names": True,
    "special_symbols": "none",
    "spaces_between": 5,
    "months_per_row": 3,
    "year": 2026,
}

def sync_state_from_inputs():
    state["include_day_names"] = document["includeDayNames"].checked

    special_symbols = "none"
    if document["specialSymbolsSymbols"].checked:
        special_symbols = "symbols"
    elif document["specialSymbolsEmojis"].checked:
        special_symbols = "emojis"
    state["special_symbols"] = special_symbols

    spaces_between = parse_int(document["spacesBetween"].value, 5, minimum=0)
    months_per_row = parse_int(document["monthsPerRow"].value, 3, minimum=1, maximum=12)
    year = parse_int(document["year"].value, 2026, minimum=1900, maximum=2100)

    document["spacesBetween"].value = str(spaces_between)
    document["monthsPerRow"].value = str(months_per_row)
    document["year"].value = str(year)

    state["spaces_between"] = spaces_between
    state["months_per_row"] = months_per_row
    state["year"] = year


def update_symbols_warning_visibility():
    show_warning = state["special_symbols"] != "none"
    document["symbolsWarningField"].style.display = "inline-block" if show_warning else "none"


def render_calendar():
    sync_state_from_inputs()
    update_symbols_warning_visibility()
    document["calendarOutput"].text = build_calendar_text()


# ---- Calendar generation ---- #

# TODO: Improve how symbols and emojis are used.
def month_block(year, month, include_day_names, special_symbols):
    month_width = 2 * 7 + state["spaces_between"] * 6
    use_symbols = special_symbols == "symbols"
    use_emojis = special_symbols == "emojis"

    month_name = calendar.month_name[month]
    month_name_line = month_name.center(month_width)
    if use_emojis:
        month_name_line = "⬛⬛⬛⬛   " + month_name_line + "    ⬛⬛⬛"
    elif use_symbols:
        month_name_line = "■■■   " + month_name_line + "   ■■■"
    lines = [month_name_line]

    if include_day_names:
        day_names = DAY_NAMES
        if use_emojis:
            day_names = ["📅 " + day_name for day_name in DAY_NAMES]
        elif use_symbols:
            day_names = ["◆ " + day_name for day_name in DAY_NAMES]
        lines.append((" " * state["spaces_between"]).join(day_names))

    if use_emojis:
        empty_cell = "⬜   "
    elif use_symbols:
        empty_cell = "□   "
    else:
        empty_cell = "  "

    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    for week in weeks:
        cells = []
        for day in week:
            if day == 0:
                cells.append(empty_cell)
            elif use_emojis:
                cells.append("🟦 " + f"{day:2d}")
            elif use_symbols:
                cells.append("■ " + f"{day:2d}")
            else:
                cells.append(f"{day:2d}")
        lines.append((" " * state["spaces_between"]).join(cells))

    return lines, month_width


# TODO: Improve how symbols and emojis are used.
def build_calendar_text():
    blocks = []
    widths = []

    for month in range(1, 13):
        block, width = month_block(
            state["year"],
            month,
            state["include_day_names"],
            state["special_symbols"],
        )
        blocks.append(block)
        widths.append(width)

    row_gap = " " * MONTH_SEPARATION

    year_line = str(state["year"]).center(sum(widths[: state["months_per_row"]]) + MONTH_SEPARATION * (state["months_per_row"] - 1))
    if state["special_symbols"] == "emojis":
        squares_count = 7 * state["months_per_row"]
        year_line = ("🟩 " * ((squares_count + 1) // 2)) + year_line + (" 🟩" * (squares_count // 2))
    elif state["special_symbols"] == "symbols":
        squares_count = 7 * state["months_per_row"]
        year_line = ("■ " * ((squares_count + 1) // 2)) + year_line + (" ■" * (squares_count // 2))
    output_lines = [year_line]

    for row_start in range(0, 12, state["months_per_row"]):
        row_blocks = blocks[row_start : row_start + state["months_per_row"]]
        row_widths = widths[row_start : row_start + state["months_per_row"]]
        max_height = max(len(block) for block in row_blocks)

        padded_blocks = []
        for block, width in zip(row_blocks, row_widths):
            if state["special_symbols"] == "emojis":
                padding_line = (("⬛   " + (" ") * state["spaces_between"]) * 6 + "⬛   ")
            elif state["special_symbols"] == "symbols":
                padding_line = (("■   " + (" ") * state["spaces_between"]) * 6 + "■   ")
            else:
                padding_line = " " * width
            padded = block + [padding_line] * (max_height - len(block))
            padded_blocks.append(padded)

        for line_index in range(max_height):
            output_lines.append(row_gap.join(block[line_index] for block in padded_blocks))

        if row_start + state["months_per_row"] < 12:
            output_lines.append("")

    return "\n".join(output_lines)


# ---- Event handlers ---- #

def on_option_change(_event):
    render_calendar()

# TODO: Implement "includeCommentsLine" feature.
document["includeDayNames"].bind("change", on_option_change)
document["specialSymbolsNone"].bind("change", on_option_change)
document["specialSymbolsSymbols"].bind("change", on_option_change)
document["specialSymbolsEmojis"].bind("change", on_option_change)
document["spacesBetween"].bind("input", on_option_change)
document["monthsPerRow"].bind("input", on_option_change)
document["year"].bind("input", on_option_change)


# ---- Initialization ---- #

render_calendar()
