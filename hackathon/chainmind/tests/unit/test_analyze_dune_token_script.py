import importlib.util
from pathlib import Path


def test_analyze_dune_token_script_exposes_hermes_output_argument():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "analyze_dune_token.py"
    spec = importlib.util.spec_from_file_location("analyze_dune_token_script", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    args = module.build_parser().parse_args(
        ["0xToken", "--hermes-output", "runtime/reports/token_hermes.json"]
    )

    assert args.token_address == "0xToken"
    assert args.hermes_output == Path("runtime/reports/token_hermes.json")


def test_analyze_dune_token_script_exposes_cooldown_arguments():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "analyze_dune_token.py"
    spec = importlib.util.spec_from_file_location("analyze_dune_token_script", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    args = module.build_parser().parse_args(
        [
            "0xToken",
            "--hermes-output",
            "runtime/reports/token_hermes.json",
            "--cooldown-state",
            "runtime/alerts/cooldown.json",
            "--cooldown-write",
        ]
    )

    assert args.cooldown_state == Path("runtime/alerts/cooldown.json")
    assert args.cooldown_write is True
