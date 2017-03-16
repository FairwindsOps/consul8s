import pytest
from click.testing import CliRunner
from consul8s import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main, args=['--run-once'])
    assert result.exit_code in [-1, 0]
