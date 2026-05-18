import calendar

from browser import document


# ---- Utilities ---- #

DAY_NAMES = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

DECORATORS = {
    "basic": ("*", "|", "#", " ", " "),
    "geometric": ("□", "■", "●", " ", " "),
    "emojis": ("⬛", "📅", "🟦", "⬛", "⬜"),
}

COMMENT_CELL_DECORATOR = 0
DAY_CELL_DECORATOR = 1
DAY_NAME_DECORATOR = 2
EMPTY_CELL_DECORATOR = 3
PADDING_CELL_DECORATOR = 4

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
    "include_comments_line": False,
    "include_separation_line": False,
    "decorators": "none",
    "spaces_between": 5,
    "months_per_row": 3,
    "year": 2026,
}

def sync_state_from_inputs():
    state["include_day_names"] = document["includeDayNames"].checked
    state["include_comments_line"] = document["includeCommentsLine"].checked
    state["include_separation_line"] = document["includeSeparationLine"].checked

    decorators = "none"
    if document["decoratorsBasic"].checked:
        decorators = "basic"
    elif document["decoratorsGeometric"].checked:
        decorators = "geometric"
    elif document["decoratorsEmojis"].checked:
        decorators = "emojis"
    state["decorators"] = decorators

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
    show_warning = state["decorators"] == "geometric" or state["decorators"] == "emojis"
    document["decoratorsWarningField"].style.display = "inline-block" if show_warning else "none"


def render_calendar():
    sync_state_from_inputs()
    update_symbols_warning_visibility()
    document["calendarOutput"].text = build_calendar_text()


# ---- Calendar generation ---- #

def month_block(year, month, include_day_names, include_comments_line, include_separation_line, decorators):
    use_decorators = decorators != "none"

    month_width = 2 * 7 + state["spaces_between"] * 6
    if use_decorators:
        month_width = month_width + 7 * 2
    
    month_name = calendar.month_name[month]
    month_name_line = month_name.center(month_width)
    lines = [month_name_line]

    if include_day_names:
        day_names = DAY_NAMES
        if use_decorators:
            day_names = [DECORATORS[decorators][DAY_NAME_DECORATOR] + " " + day_name for day_name in DAY_NAMES]
        lines.append((" " * state["spaces_between"]).join(day_names))

    empty_cell = "  " if not use_decorators else DECORATORS[decorators][EMPTY_CELL_DECORATOR] + "   "

    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    for week in weeks:
        cells = []
        for day in week:
            if day == 0:
                cells.append(empty_cell)
            elif use_decorators:
                cells.append(DECORATORS[decorators][DAY_CELL_DECORATOR] + " " + f"{day:2d}")
            else:
                cells.append(f"{day:2d}")
        lines.append((" " * state["spaces_between"]).join(cells))

        if include_comments_line:
            if use_decorators:
                comment_cells = []
                for day in week:
                    decorator_index = COMMENT_CELL_DECORATOR if day != 0 else EMPTY_CELL_DECORATOR
                    comment_cells.append(DECORATORS[decorators][decorator_index] + "   ")
                lines.append((" " * state["spaces_between"]).join(comment_cells))
            else:
                lines.append(" " * month_width)

        if include_separation_line:
            lines.append(" " * month_width)

    return lines, month_width


def build_calendar_text():
    use_decorators = state["decorators"] != "none"

    blocks = []
    widths = []

    for month in range(1, 13):
        block, width = month_block(
            state["year"],
            month,
            state["include_day_names"],
            state["include_comments_line"],
            state["include_separation_line"],
            state["decorators"],
        )
        blocks.append(block)
        widths.append(width)

    row_gap = " " * MONTH_SEPARATION

    calendar_width = sum(widths[: state["months_per_row"]]) + MONTH_SEPARATION * (state["months_per_row"] - 1)
    year_line = str(state["year"]).center(calendar_width)
    output_lines = [year_line]

    for row_start in range(0, 12, state["months_per_row"]):
        row_blocks = blocks[row_start : row_start + state["months_per_row"]]
        row_widths = widths[row_start : row_start + state["months_per_row"]]
        max_height = max(len(block) for block in row_blocks)

        padded_blocks = []
        for block, width in zip(row_blocks, row_widths):
            if use_decorators:
                padding_line = (DECORATORS[state["decorators"]][PADDING_CELL_DECORATOR] + "   " + (" ") * state["spaces_between"]) * 6 + DECORATORS[state["decorators"]][PADDING_CELL_DECORATOR] + "   "
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

document["includeDayNames"].bind("change", on_option_change)
document["includeCommentsLine"].bind("change", on_option_change)
document["includeSeparationLine"].bind("change", on_option_change)
document["decoratorsNone"].bind("change", on_option_change)
document["decoratorsBasic"].bind("change", on_option_change)
document["decoratorsGeometric"].bind("change", on_option_change)
document["decoratorsEmojis"].bind("change", on_option_change)
document["spacesBetween"].bind("input", on_option_change)
document["monthsPerRow"].bind("input", on_option_change)
document["year"].bind("input", on_option_change)


# ---- Initialization ---- #

render_calendar()
