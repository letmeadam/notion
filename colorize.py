from typing import Union

from colorist import BgColor, BgColorRGB, Color, ColorRGB, Effect


def colorize_string(input_str: str, *color_args: str) -> str:
    modification_string = ""

    for color_arg in color_args:
        modification_string += str(_get_modifier(color_arg))

    if modification_string:
        return modification_string + input_str + Color.OFF

    return input_str


def _get_modifier(color_arg: str) -> Union[str, BgColor, BgColorRGB, Color, ColorRGB, Effect]:
    if color_arg == "italic":
        return Effect.DIM

    if color_arg == "underline":
        return Effect.UNDERLINE

    if color_arg == "bold":
        return Effect.BOLD

    elif color_arg.startswith("grey") or color_arg.startswith("gray"):
        color = (128, 128, 128)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Brown
    elif color_arg.startswith("brown"):
        color = (255, int(255 * 0.75), 0)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Orange
    elif color_arg.startswith("orange"):
        color = (255, int(255 * 0.5), 0)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Yellow
    elif color_arg.startswith("yellow"):
        color = (255, 255, 0)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Green
    elif color_arg.startswith("green"):
        color = (0, 255, 0)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Blue
    elif color_arg.startswith("blue"):
        color = (0, 0, 255)
        if color_arg.endswith("background"):
            return BgColorRGB(*color)
        else:
            return ColorRGB(*color)

    # Purple
    elif color_arg.startswith("purple"):
        color = (int(255 * 0.5), 0, 255)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Pink
    elif color_arg.startswith("pink"):
        color = (255, 0, 255)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    # Red
    elif color_arg.startswith("red"):
        color = (255, 0, 0)
        if color_arg.endswith("background"):
            return str(Color.BLACK) + str(BgColorRGB(*color))
        else:
            return ColorRGB(*color)

    return ""
