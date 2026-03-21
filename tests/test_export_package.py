"""Tests for report generation and export -- file creation, HTML structure, standalone check.

Covers EXPT-03, EXPT-04, EXPT-06, EXPT-07.
"""
import pytest
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references'))
from report_generator import generate_report


# ---------------------------------------------------------------------------
# Helpers -- create minimal mock artifact files
# ---------------------------------------------------------------------------

def _create_mock_artifacts(base_dir, phase_num=1):
    """Create minimal iteration artifacts and best_result in base_dir."""
    exec_dir = Path(base_dir) / f'phase_{phase_num}_execute'
    exec_dir.mkdir(parents=True, exist_ok=True)

    # Create 2 iteration verdict files
    for i in [1, 2]:
        verdict = {
            'iteration': i,
            'params': {'fast': 10 + i, 'slow': 30 + i},
            'metrics': {
                'sharpe_ratio': 1.0 + i * 0.3,
                'max_drawdown': -0.10 - i * 0.02,
                'win_rate': 0.50 + i * 0.05,
                'profit_factor': 1.2 + i * 0.2,
                'total_trades': 30 + i * 5,
                'net_pnl': 2000.0 + i * 1000,
                'sortino_ratio': 1.5 + i * 0.3,
                'calmar_ratio': 1.0 + i * 0.2,
                'trade_count': 30 + i * 5,
                'expectancy': 50.0 + i * 10,
            },
            'hypothesis': f'Iteration {i} hypothesis',
            'verdict': 'MINT' if i == 2 else 'exploring',
        }
        with open(exec_dir / f'iter_{i:02d}_verdict.json', 'w') as f:
            json.dump(verdict, f)

        with open(exec_dir / f'iter_{i:02d}_params.json', 'w') as f:
            json.dump(verdict['params'], f)

        with open(exec_dir / f'iter_{i:02d}_metrics.json', 'w') as f:
            json.dump(verdict['metrics'], f)

    # Create best_result.json
    best = {
        'best_params': {'fast': 12, 'slow': 32},
        'is_metrics': {
            'sharpe_ratio': 1.6, 'max_drawdown': -0.14, 'win_rate': 0.60,
            'profit_factor': 1.6, 'total_trades': 40, 'net_pnl': 4000.0,
            'sortino_ratio': 2.1, 'calmar_ratio': 1.4,
            'trade_count': 40, 'expectancy': 70.0,
        },
        'oos_metrics': {'sharpe_ratio': 1.3, 'max_drawdown': -0.16},
        'stop_reason': 'MINT',
    }
    with open(Path(base_dir) / f'phase_{phase_num}_best_result.json', 'w') as f:
        json.dump(best, f)

    return phase_num


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_generate_report_creates_html_file(tmp_path):
    """generate_report should produce an HTML file at the output path."""
    phase_num = _create_mock_artifacts(tmp_path)
    output = tmp_path / 'report.html'
    template_path = Path(__file__).resolve().parent.parent / 'templates' / 'report-template.html'

    generate_report(
        phase_dir=str(tmp_path),
        strategy_name='Test Strategy',
        targets={'sharpe_ratio': 1.5},
        output_path=str(output),
        template_path=str(template_path),
        phase_num=phase_num,
    )

    assert output.exists(), "HTML report file should exist"
    content = output.read_text()
    assert '<html' in content


def test_generated_html_contains_plotly_cdn(tmp_path):
    """Generated HTML should include plotly CDN."""
    phase_num = _create_mock_artifacts(tmp_path)
    output = tmp_path / 'report.html'
    template_path = Path(__file__).resolve().parent.parent / 'templates' / 'report-template.html'

    generate_report(
        phase_dir=str(tmp_path),
        strategy_name='Test Strategy',
        targets={'sharpe_ratio': 1.5},
        output_path=str(output),
        template_path=str(template_path),
        phase_num=phase_num,
    )

    content = output.read_text()
    assert 'plotly' in content.lower()


def test_generated_html_has_all_sections(tmp_path):
    """Generated HTML should contain all main sections."""
    phase_num = _create_mock_artifacts(tmp_path)
    output = tmp_path / 'report.html'
    template_path = Path(__file__).resolve().parent.parent / 'templates' / 'report-template.html'

    generate_report(
        phase_dir=str(tmp_path),
        strategy_name='Test Strategy',
        targets={'sharpe_ratio': 1.5},
        output_path=str(output),
        template_path=str(template_path),
        phase_num=phase_num,
    )

    content = output.read_text()
    assert 'metrics-summary' in content
    assert 'equity-chart' in content or 'equity-curve' in content or 'Equity Curve' in content
    assert 'drawdown' in content.lower()
    assert 'iteration' in content.lower() or 'Optimization' in content
    assert 'trade' in content.lower() or 'Trade' in content


def test_generated_html_standalone(tmp_path):
    """Generated HTML should not have external CSS links (only inline + plotly CDN)."""
    phase_num = _create_mock_artifacts(tmp_path)
    output = tmp_path / 'report.html'
    template_path = Path(__file__).resolve().parent.parent / 'templates' / 'report-template.html'

    generate_report(
        phase_dir=str(tmp_path),
        strategy_name='Test Strategy',
        targets={'sharpe_ratio': 1.5},
        output_path=str(output),
        template_path=str(template_path),
        phase_num=phase_num,
    )

    content = output.read_text()
    # Should not have external CSS links (rel="stylesheet" pointing to .css files)
    import re
    css_links = re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*\.css', content)
    assert len(css_links) == 0, f"Found external CSS links: {css_links}"


def test_report_with_no_artifacts_raises(tmp_path):
    """generate_report with empty phase_dir should raise ValueError."""
    empty_dir = tmp_path / 'empty'
    empty_dir.mkdir()
    output = tmp_path / 'report.html'
    template_path = Path(__file__).resolve().parent.parent / 'templates' / 'report-template.html'

    with pytest.raises(ValueError, match="No iteration artifacts"):
        generate_report(
            phase_dir=str(empty_dir),
            strategy_name='Test Strategy',
            targets={'sharpe_ratio': 1.5},
            output_path=str(output),
            template_path=str(template_path),
        )
