async def gen_size_kb(*buttons, size_tag: str = "7%", btn_per_line: int = 5):
    kb = [(f"{button}%", f"set_size_{button}") for button in buttons]
    return (
        [[(f"Watermark Size - {size_tag}%", "btn_not_work")]]
        + [kb[i : i + btn_per_line] for i in range(0, len(kb), btn_per_line)]
        + [[("Back", "main.settings")]]
    )


async def gen_position_kb(position_tag: str):
    return [
        [(f"Current Position - {position_tag}", "btn_not_work")],
        [
            ("Top Left", "set_position_5:5"),
            ("Top Right", "set_position_main_w-overlay_w-5:5"),
        ],
        [
            ("Bottom Left", "set_position_5:main_h-overlay_h"),
            ("Bottom Right", "set_position_main_w-overlay_w-5:main_h-overlay_h-5"),
        ],
    ] + [[("Back", "main.settings")]]


async def build_settings_kb(position_tag, size_tag):
    return (await gen_position_kb(position_tag=position_tag)) + (
        await gen_size_kb(
            5,
            7,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            size_tag=size_tag,
            btn_per_line=4,
        )
    )
