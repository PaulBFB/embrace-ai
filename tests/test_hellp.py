import pytest
from src.hello import main


def test_main():

    result = main()

    assert result is None

