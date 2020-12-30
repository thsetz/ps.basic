import pytest
from ps.basic.utils import get_html_string, hms_string


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"A": "B"}, "<table><tr><td>A</td><td>B</td></tr></table>"),  # dictionary
        (
            {"A": {"B1": "B2"}},
            "<table><tr><td>A</td><td><table><tr><td>B1</td><td>B2</td></tr></table></td></tr></table>",
        ),
    ],
)
def test_hml_string(test_input, expected):
    assert get_html_string(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (1, "00:00:01"),
        (61, "00:01:01"),
        (3661, "01:01:01"),
    ],
)
def test_hml_string(test_input, expected):
    assert hms_string(test_input) == expected
