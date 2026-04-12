from typing import Iterable

from gradio.themes import Soft
from gradio.themes.utils import colors, fonts, sizes

# Anthropic-inspired neutral palette
sand = colors.Color(
    name="sand",
    c50="#FAF8F5",
    c100="#F0EBE3",
    c200="#E8DED1",
    c300="#D4C5B0",
    c400="#C0AD93",
    c500="#A89279",
    c600="#3D3429",
    c700="#2C251D",
    c800="#1E1A14",
    c900="#13110D",
    c950="#0A0907",
)

# Warm accent color (Anthropic coral/terracotta)
accent = colors.Color(
    name="accent",
    c50="#FEF5EE",
    c100="#FCE7D4",
    c200="#F8CCA8",
    c300="#F3A971",
    c400="#EC8139",
    c500="#D4A574",
    c600="#C4854A",
    c700="#A66A3A",
    c800="#875536",
    c900="#6E462F",
    c950="#3B2117",
)

err_txt = "#E87561"
gradient = "linear-gradient(135deg, *primary_400 0%, *primary_500 100%)"
gradient_muted = "linear-gradient(135deg, *primary_500 0%, *primary_600 100%)"

err_dark = "rgba(232, 117, 97, 1)"
err_dark_muted = "rgba(232, 117, 97, 0.75)"

err = "rgba(232, 117, 97, 1)"
err_muted = "rgba(210, 100, 80, 1)"


common = dict(
    # element colours
    color_accent="*primary_400",
    # shadows
    shadow_drop="0 1px 3px 0 rgb(0 0 0 / 0.04)",
    shadow_drop_lg="0 2px 8px 0 rgba(0 0 0 / 0.06)",
    # layout atoms
    block_label_margin="*spacing_xl",
    block_label_padding="*spacing_xl",
    block_label_shadow="none",
    layout_gap="*spacing_xxl",
    section_header_text_size="*text_lg",
    # buttons
    button_shadow="none",
    button_shadow_active="*shadow_drop",
    button_shadow_hover="none",
)
dark_mode = dict(
    # body attributes
    body_text_color_subdued_dark="*neutral_300",
    # element colours
    background_fill_secondary_dark="*neutral_950",
    border_color_accent_dark="rgba(255,255,255,0)",
    border_color_primary_dark="*neutral_700",
    color_accent_soft_dark="*primary_400",
    # text
    link_text_color_dark="*primary_300",
    link_text_color_active_dark="*primary_200",
    link_text_color_visited_dark="*primary_400",
    # layout atoms
    block_label_background_fill_dark="*neutral_800",
    block_label_border_width_dark="0px",
    block_label_text_color_dark="*primary_300",
    block_shadow_dark="none",
    block_title_text_color_dark="*primary_300",
    panel_border_width_dark="0px",
    # component atoms
    checkbox_background_color_selected_dark="*primary_400",
    checkbox_border_color_focus_dark="*primary_400",
    checkbox_border_color_selected_dark="*primary_500",
    checkbox_label_background_fill_selected_dark="*primary_200",
    checkbox_label_text_color_selected_dark="*neutral_700",
    error_border_color_dark=err_dark,
    error_text_color_dark="*neutral_100",
    error_icon_color_dark=err_dark,
    input_background_fill_dark="*neutral_700",
    input_border_color_dark="*input_background_fill",
    input_border_color_focus_dark="*input_background_fill",
    input_placeholder_color_dark="*neutral_500",
    loader_color_dark="*primary_300",
    slider_color_dark="*primary_300",
    stat_background_fill_dark="*primary_100",
    table_border_color_dark="*neutral_800",
    table_even_background_fill_dark="*neutral_900",
    table_odd_background_fill_dark="*neutral_800",
    table_row_focus_dark="*neutral_600",
    # buttons
    button_primary_background_fill_dark=gradient,
    button_primary_background_fill_hover_dark=gradient_muted,
    button_secondary_background_fill_hover_dark="*neutral_700",
    button_cancel_background_fill_dark=err_dark,
    button_cancel_background_fill_hover_dark=err_dark_muted,
)
light_mode = dict(
    background_fill_primary="#FAF8F5",
    background_fill_secondary="#FAF8F5",
    # body attributes
    body_background_fill="*background_fill_primary",
    body_text_color="*neutral_800",
    body_text_color_subdued="*neutral_500",
    border_color_accent="rgba(255,255,255,0)",
    border_color_primary="*neutral_200",
    color_accent_soft="*primary_100",
    # text
    link_text_color="*primary_500",
    link_text_color_visited="*primary_700",
    # layout atoms
    block_label_border_width="0px",
    block_label_background_fill="white",
    block_label_text_color="*neutral_700",
    block_shadow="none",
    block_title_text_color="*neutral_700",
    panel_border_width="0px",
    # component atoms
    checkbox_background_color_selected="*primary_400",
    checkbox_border_color_focus="*primary_400",
    checkbox_border_color_selected="*primary_400",
    checkbox_label_border_color="*primary_200",
    error_background_fill="*background_fill_primary",
    error_border_color=err_muted,
    error_text_color="*neutral_800",
    input_background_fill="*neutral_100",
    input_border_color="*neutral_200",
    input_border_color_focus="*primary_300",
    input_placeholder_color="*neutral_400",
    loader_color="*primary_400",
    slider_color="*primary_400",
    stat_background_fill="*primary_100",
    table_even_background_fill="*neutral_50",
    table_odd_background_fill="*neutral_100",
    table_row_focus="*primary_100",
    # buttons
    button_primary_background_fill="*neutral_800",
    button_primary_background_fill_hover="*neutral_700",
    button_primary_text_color="white",
    button_secondary_background_fill="*neutral_200",
    button_secondary_background_fill_hover="*neutral_300",
    button_cancel_background_fill=err_muted,
    button_cancel_background_fill_hover=err,
    button_cancel_text_color="*neutral_50",
)


class Kotaemon(Soft):
    """ChatCLT theme — Anthropic-inspired warm minimal aesthetic."""

    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = accent,
        secondary_hue: colors.Color | str = accent,
        neutral_hue: colors.Color | str = sand,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_md,
        text_size: sizes.Size | str = sizes.text_md,
        font: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Inter"),
            "system-ui",
            "-apple-system",
            "sans-serif",
        ),
        font_mono: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("JetBrains Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )
        self.name = "chatclt"
        super().set(
            **common,
            **dark_mode,
            **light_mode,
        )
