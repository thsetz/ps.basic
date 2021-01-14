def get_html_string(var_p: dict):
    """Return html table structure for a data structure."""
    html_string = "<table>"
    for name, value in var_p.items():
        if type(value) is dict:
            html_string += "<tr><td>%s</td><td>%s</td></tr>" % (
                str(name),
                get_html_string(value),
            )
        else:
            html_string += "<tr><td>%s</td><td>%s</td></tr>" % (
                str(name),
                str(value),
            )

    html_string += "</table>"
    return html_string


def hms_string(sec_elapsed: int):
    """Return the hour:minute:seconds for a period in seconds."""
    h = int(sec_elapsed / (60 * 60))
    m = int(sec_elapsed % (60 * 60) / 60)
    s = sec_elapsed % 60
    return "%02d:%02d:%02d" % (h, m, s)
