import pytest
from pytest import approx

from beautiplot._config import _Config


@pytest.fixture
def config() -> _Config:
    from beautiplot import config

    return config


def test_default_settings(config: _Config) -> None:
    assert config.fontsize == 11
    assert config.fontfamily == 'serif'
    assert config.dpi == 300
    assert config.cmap.name == 'inferno'
    assert config.colorbar_width == approx(10 * config.bp)
    assert config.width == approx(5.90551)
    assert config.legend_setup == {
        'columnspacing': 1.5,
        'handlelength': 1.5,
        'handletextpad': 0.5,
        'borderaxespad': 0.2,
    }
    assert r'\usepackage{amsmath}' in config.tex_preamble


def test_update_settings(config: _Config) -> None:
    config.fontsize = 14
    assert config.fontsize == 14
    config.fontfamily = 'sans-serif'
    assert config.fontfamily == 'sans-serif'
    config.dpi = 150
    assert config.dpi == 150
    config.set_cmap('viridis')
    assert config.cmap.name == 'viridis'
    config.default()


def test_colorbar_width(config: _Config) -> None:
    config.colorbar_width = 20
    assert config.colorbar_width == approx(20 * config.bp)
    config.default()


def test_width(config: _Config) -> None:
    config.width = 500
    assert config.width == approx(500 * config.pt)
    config.default()


def test_add_usepackage(config: _Config) -> None:
    config.add_usepackage('geometry')
    assert '\\usepackage{geometry}' in config.tex_preamble
    config.default()


def test_remove_usepackage(config: _Config) -> None:
    config.add_usepackage('geometry')
    config.remove_usepackage('geometry')
    assert '\\usepackage{geometry}' not in config.tex_preamble
    config.default()


def test_add_preamble(config: _Config) -> None:
    config.add_preamble(r'\newcommand{\RR}[2]{\mathbb{R}^{#1 \times #2}}')
    assert r'\newcommand{\RR}[2]{\mathbb{R}^{#1 \times #2}}' in config.tex_preamble
    config.default()


def test_remove_preamble(config: _Config) -> None:
    config.add_preamble(r'\newcommand{\RR}[2]{\mathbb{R}^{#1 \times #2}}')
    config.remove_preamble(r'\newcommand{\RR}[2]{\mathbb{R}^{#1 \times #2}}')
    assert r'\newcommand{\RR}[2]{\mathbb{R}^{#1 \times #2}}' not in config.tex_preamble
    config.default()


def test_add_legend_setup(config: _Config) -> None:
    config.add_legend_setup('fontsize', 10)
    assert config.legend_setup['fontsize'] == 10
    config.default()


def test_remove_legend_setup(config: _Config) -> None:
    config.add_legend_setup('fontsize', 10)
    config.remove_legend_setup('fontsize')
    assert 'fontsize' not in config.legend_setup
    config.default()


def test_empty_legend_setup(config: _Config) -> None:
    config.empty_legend_setup()
    assert config.legend_setup == {}
    config.default()
