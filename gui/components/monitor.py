"""
System monitoring bar.
"""

import PySimpleGUI as sg

FONT_FAMILY = "Helvetica"
FONT_SIZE_BIG = 20
FONT_SIZE_SMALL = 12
FONT_STYLE = "bold"


class MonitorBar(sg.Column):
    """System bar for parameter monitoring."""

    # Value displays
    ipap: sg.Text
    epap: sg.Text
    freq: sg.Text
    vc_in: sg.Text
    vc_out: sg.Text
    oxygen: sg.Text

    # Buttons
    lock_btn: sg.RealtimeButton

    # Misc
    expander: sg.Text

    def __init__(self):
        self.ipap = sg.Text(
            "-",
            font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE),
            size=(4, 1),
            justification="right",
        )
        self.epap = sg.Text(
            "-",
            font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE),
            size=(4, 1),
            justification="right",
        )
        self.freq = sg.Text(
            "-",
            font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE),
            size=(4, 1),
            justification="right",
        )
        self.vc_in = sg.Text(
            "-",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE),
            size=(3, 1),
            justification="right",
        )
        self.vc_out = sg.Text(
            "-",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE),
            size=(3, 1),
            justification="right",
        )
        self.oxygen = sg.Text(
            "-",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE),
            size=(4, 1),
            justification="right",
        )

        self.lock_btn = sg.RealtimeButton("Bloquear", size=(9, 2))

        self.expander = sg.Text()

        super().__init__(
            [
                [
                    sg.Text(
                        "IPAP:", font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE)
                    ),
                    self.ipap,
                    sg.Text(
                        "cmH\N{SUBSCRIPT TWO}O",
                        font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE),
                    ),
                ]
                + [
                    sg.Text(
                        "EPAP:", font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE)
                    ),
                    self.epap,
                    sg.Text(
                        "cmH\N{SUBSCRIPT TWO}O",
                        font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE),
                    ),
                ]
                + [
                    sg.Text(
                        "Frecuencia:",
                        font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE),
                    ),
                    self.freq,
                    sg.Text(
                        "rpm", font=(FONT_FAMILY, FONT_SIZE_BIG, FONT_STYLE)
                    ),
                ]
                + [
                    sg.Text(
                        "V (in):",
                        font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE),
                    ),
                    self.vc_in,
                    sg.Text(
                        "ml", font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE)
                    ),
                ]
                + [
                    sg.Text(
                        "V (out):",
                        font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE),
                    ),
                    self.vc_out,
                    sg.Text(
                        "ml", font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE)
                    ),
                ]
                + [
                    sg.Text(
                        "O\N{SUBSCRIPT TWO}:",
                        font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE),
                    ),
                    self.oxygen,
                    sg.Text(
                        "%", font=(FONT_FAMILY, FONT_SIZE_SMALL, FONT_STYLE)
                    ),
                ]
                + [self.expander]
                + [self.lock_btn]
            ]
        )

    def expand(self):
        super().expand(expand_x=True)
        self.expander.expand(expand_x=True)

    def update_values(
        self,
        ipap: float,
        epap: float,
        freq: float,
        vc_in: float,
        vc_out: float,
        oxygen: float,
    ):
        """Change the values shown in the bar.

        Args:
            ipap (float): Value for IPAP.
            epap (float): Value for EPAP.
            freq (float): Value for respiratory frequency.
            vc_in (float): Value for inhaled volume.
            vc_out (float): Value for exhaled volume.
            oxygen (float): Value for oxygen percentage.
        """

        self.ipap.update("%.1f" % round(ipap, 1))
        self.epap.update("%.1f" % round(epap, 1))
        self.freq.update("%.1f" % round(freq, 1))
        self.vc_in.update(vc_in)
        self.vc_out.update(vc_out)
        self.oxygen.update("%.1f" % round(oxygen, 1))

    def set_alarm(self, type: str, criticality: str):
        """Change the colours of the labels to reflect an alarm.

        Args:
            type (str): Alarm type.
            criticality (str): Level of criticality.
        """

        if type == "pressure_min":
            self.epap.update(
                text_color="orange" if criticality == "medium" else "red"
            )
        elif type == "pressure_max":
            self.ipap.update(
                text_color="orange" if criticality == "medium" else "red"
            )
