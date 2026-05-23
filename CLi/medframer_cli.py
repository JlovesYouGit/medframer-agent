#!/usr/bin/env python3
"""
MedFramer autonomous CLI for Ollama model operations and biological discovery.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
ASI_CORE_PARENT = REPO_ROOT / "asi core"
if str(ASI_CORE_PARENT) not in sys.path:
    sys.path.insert(0, str(ASI_CORE_PARENT))

from light_asi_core.config import RuntimeConfig
from light_asi_core.continuous_data_flow import ContinuousDataFlow
from light_asi_core.discovery_agent import DiscoveryAgent
from light_asi_core.model_tuner import ModelTuner
from light_asi_core.ollama_client import OllamaClient, OllamaConnectionError
from light_asi_core.persistent_memory import PersistentMemory
from light_asi_core.weight_adjuster import WeightAdjuster


def _resolve_path(path_value: Optional[str], fallback: Path) -> Path:
    if not path_value:
        return fallback.resolve()
    return Path(path_value).expanduser().resolve()


def _runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    config = RuntimeConfig()
    config.model_store_path = _resolve_path(
        getattr(args, "model_store", None), config.model_store_path
    )
    config.ollama_base_url = getattr(args, "ollama_url", config.ollama_base_url)

    medframework_root = getattr(args, "medframework_root", None)
    if medframework_root:
        config.medframework_root = _resolve_path(medframework_root, config.medframework_root)
    config.ensure_runtime_dirs()
    return config


def _run_ollama_cli(command: list[str], model_store: Path, host: Optional[str] = None) -> int:
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(model_store)
    if host:
        env["OLLAMA_HOST"] = host
    try:
        completed = subprocess.run(["ollama", *command], env=env, check=False)
    except FileNotFoundError:
        print("Error: `ollama` executable was not found in PATH.", file=sys.stderr)
        return 127
    return int(completed.returncode)


def _cmd_init_store(args: argparse.Namespace, config: RuntimeConfig) -> int:
    config.model_store_path.mkdir(parents=True, exist_ok=True)
    powershell_script = REPO_ROOT / "CLi" / "set_ollama_env.ps1"
    powershell_script.write_text(
        "\n".join(
            [
                f"$env:OLLAMA_MODELS = \"{config.model_store_path}\"",
                f"$env:OLLAMA_HOST = \"{args.host}:{args.port}\"",
                "Write-Host \"OLLAMA_MODELS and OLLAMA_HOST configured for this terminal session.\"",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Local model store ready: {config.model_store_path}")
    print(f"PowerShell helper written: {powershell_script}")
    return 0


def _cmd_serve(args: argparse.Namespace, config: RuntimeConfig) -> int:
    host = f"{args.host}:{args.port}"
    return _run_ollama_cli(["serve"], model_store=config.model_store_path, host=host)


def _cmd_models(args: argparse.Namespace, config: RuntimeConfig) -> int:
    command = args.models_command
    if command == "list":
        return _run_ollama_cli(["list"], model_store=config.model_store_path)
    if command == "pull":
        return _run_ollama_cli(["pull", args.model], model_store=config.model_store_path)
    if command == "show":
        return _run_ollama_cli(["show", args.model], model_store=config.model_store_path)
    if command == "rm":
        return _run_ollama_cli(["rm", args.model], model_store=config.model_store_path)
    if command == "ps":
        return _run_ollama_cli(["ps"], model_store=config.model_store_path)
    if command == "stop":
        return _run_ollama_cli(["stop", args.model], model_store=config.model_store_path)
    print(f"Unsupported models command: {command}", file=sys.stderr)
    return 2


def _cmd_chat(args: argparse.Namespace, config: RuntimeConfig) -> int:
    client = OllamaClient(base_url=config.ollama_base_url)
    try:
        client.list_models()
    except OllamaConnectionError as exc:
        print(f"Ollama connection error: {exc}", file=sys.stderr)
        return 1

    messages: list[Dict[str, str]] = []
    if args.system_prompt:
        messages.append({"role": "system", "content": args.system_prompt})

    print("MedFramer chat active. Type /bye to exit.")
    while True:
        try:
            user_input = input("lab> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"/bye", "/exit", "exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})
        response = client.chat(
            model=args.model,
            messages=messages,
            options={"temperature": float(args.temperature)},
        )
        assistant_text = response.get("message", {}).get("content", "").strip()
        print(f"\nagent> {assistant_text}\n")
        messages.append({"role": "assistant", "content": assistant_text})
    return 0


def _render_markdown_result(payload: Dict[str, Any]) -> str:
    wr = payload.get("working_result", {})
    explanation = payload.get("explanation_module", {})
    steps = payload.get("optimal_discovery_process", [])
    refs = payload.get("evidence_endpoints", [])

    lines = [
        f"# Discovery Result: {payload.get('query', '')}",
        f"Model: `{payload.get('model', '')}`",
        "",
        "## Working Biological Result",
        f"- Type: {wr.get('result_type', 'analysis')}",
        f"- Title: {wr.get('title', 'Untitled')}",
        "",
        wr.get("content", "").strip(),
        "",
        "## Optimal Discovery Process",
    ]
    for item in steps:
        step = item.get("step", "?")
        action = item.get("action", "")
        why = item.get("why", "")
        lines.append(f"{step}. {action} — {why}")

    lines.extend(
        [
            "",
            "## Explanation Module",
            explanation.get("summary", ""),
            "",
            "## Evidence Endpoints",
        ]
    )
    for ref in refs:
        lines.append(f"- `{ref}`")
    return "\n".join(lines).strip() + "\n"


def _cmd_discover(args: argparse.Namespace, config: RuntimeConfig) -> int:
    agent = DiscoveryAgent(config=config)
    result = agent.run_discovery(
        query=args.query,
        model=args.model,
        max_files=args.max_files,
        medframework_root=_resolve_path(args.medframework_root, config.medframework_root)
        if args.medframework_root
        else None,
    )
    payload = result.to_dict()

    if args.format == "json":
        output_text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        output_text = _render_markdown_result(payload)

    print(output_text)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.write_text(output_text, encoding="utf-8")
    return 0


def _cmd_index(args: argparse.Namespace, config: RuntimeConfig) -> int:
    agent = DiscoveryAgent(config=config)
    snapshot = agent.index_medframework(
        max_files=args.max_files,
        medframework_root=_resolve_path(args.medframework_root, config.medframework_root)
        if args.medframework_root
        else None,
    )
    output = {
        "indexed_documents": len(snapshot["documents"]),
        "top_terms": snapshot["patterns"].top_terms[:10],
        "mesh_path": str(config.mesh_store_path),
    }
    print(json.dumps(output, indent=2))
    return 0


def _cmd_tune_model(args: argparse.Namespace, config: RuntimeConfig) -> int:
    tuner = ModelTuner(config)
    result = tuner.create_custom_model(
        base_model=args.base_model,
        custom_name=args.custom_name,
        medframework_root=_resolve_path(args.medframework_root, config.medframework_root)
        if args.medframework_root
        else None,
        max_files=args.max_files,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 1


def _cmd_memory(args: argparse.Namespace, config: RuntimeConfig) -> int:
    memory = PersistentMemory(config)
    
    if args.memory_action == "stats":
        stats = memory.get_statistics()
        print(json.dumps(stats, indent=2))
    elif args.memory_action == "export":
        export_path = memory.export_memory()
        print(f"Memory exported to: {export_path}")
    elif args.memory_action == "import":
        result = memory.import_memory(Path(args.import_path))
        print(json.dumps(result, indent=2))
    elif args.memory_action == "context":
        context = memory.get_relevant_context(args.query, max_results=args.max_results)
        print(json.dumps(context, indent=2))
    
    return 0


def _cmd_weights(args: argparse.Namespace, config: RuntimeConfig) -> int:
    weight_adjuster = WeightAdjuster(config)
    
    if args.weights_action == "summary":
        summary = weight_adjuster.get_weight_adjustment_summary()
        print(json.dumps(summary, indent=2))
    elif args.weights_action == "get":
        weights = weight_adjuster.get_model_weights(args.model)
        print(json.dumps(weights, indent=2))
    elif args.weights_action == "reset":
        result = weight_adjuster.reset_model_weights(args.model)
        print(json.dumps(result, indent=2))
    elif args.weights_action == "export":
        export_path = weight_adjuster.export_weight_adjustments()
        print(f"Weights exported to: {export_path}")
    
    return 0


def _cmd_flow(args: argparse.Namespace, config: RuntimeConfig) -> int:
    flow = ContinuousDataFlow(config)
    
    if args.flow_action == "start":
        flow.start_flow()
        print("Continuous data flow started. Press Ctrl+C to stop.")
        try:
            while True:
                stats = flow.get_flow_statistics()
                print(f"\rFlow stats - Input: {stats['input_queue_size']} | Processing: {stats['processing_queue_size']} | Output: {stats['output_queue_size']} | Match Rate: {stats['average_match_rates']}", end="")
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            flow.stop_flow()
            print("\nFlow stopped.")
    elif args.flow_action == "stats":
        stats = flow.get_flow_statistics()
        print(json.dumps(stats, indent=2))
    elif args.flow_action == "input":
        data = {"text": args.text, "source": args.source}
        if args.qr_code:
            data["qr_code"] = args.qr_code
        success = flow.input_data(data)
        print(f"Data input: {'success' if success else 'failed'}")
    elif args.flow_action == "output":
        output = flow.get_output()
        if output:
            print(json.dumps(output, indent=2))
        else:
            print("No output available")
    elif args.flow_action == "reset":
        flow.reset_flow()
        print("Flow reset")
    
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="medframer",
        description="Autonomous MedFramer CLI for local Ollama model operations and discovery.",
    )
    parser.add_argument(
        "--model-store",
        default=str(REPO_ROOT / "models_store"),
        help="Local path where Ollama model files are stored.",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        help="Base URL for Ollama HTTP API.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_store = subparsers.add_parser(
        "init-local-store", help="Create local model-store and a PowerShell env helper script."
    )
    init_store.add_argument("--host", default="127.0.0.1")
    init_store.add_argument("--port", type=int, default=11434)

    serve = subparsers.add_parser("serve", help="Run `ollama serve` with project-local model path.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=11434)

    models = subparsers.add_parser("models", help="Model lifecycle operations.")
    model_sub = models.add_subparsers(dest="models_command", required=True)
    model_sub.add_parser("list", help="List downloaded models.")
    pull = model_sub.add_parser("pull", help="Download a model.")
    pull.add_argument("model")
    show = model_sub.add_parser("show", help="Show model metadata.")
    show.add_argument("model")
    rm = model_sub.add_parser("rm", help="Remove a downloaded model.")
    rm.add_argument("model")
    model_sub.add_parser("ps", help="Show running models.")
    stop = model_sub.add_parser("stop", help="Stop a running model.")
    stop.add_argument("model")

    chat = subparsers.add_parser("chat", help="Interactive chat session for lab users.")
    chat.add_argument("--model", required=True, help="Model name (example: llama3.2).")
    chat.add_argument("--temperature", type=float, default=0.2)
    chat.add_argument(
        "--system-prompt",
        default="You are a professional biomedical assistant. Return precise and testable outputs.",
    )

    discover = subparsers.add_parser(
        "discover",
        help="Run autonomous discovery pipeline with medframework ingestion and explanation output.",
    )
    discover.add_argument("--model", required=True)
    discover.add_argument("--query", required=True)
    discover.add_argument("--medframework-root", default=None)
    discover.add_argument("--max-files", type=int, default=300)
    discover.add_argument("--format", choices=["json", "markdown"], default="markdown")
    discover.add_argument("--output", default=None)

    index = subparsers.add_parser(
        "index", help="Ingest medframework data and refresh node-mesh without calling the model."
    )
    index.add_argument("--medframework-root", default=None)
    index.add_argument("--max-files", type=int, default=300)

    # Model tuning commands
    tune = subparsers.add_parser("tune", help="Fine-tune Ollama models using medframework data.")
    tune.add_argument("--base-model", required=True, help="Base model to fine-tune (e.g., llama3.2)")
    tune.add_argument("--custom-name", required=True, help="Name for the custom model")
    tune.add_argument("--medframework-root", default=None)
    tune.add_argument("--max-files", type=int, default=100)

    # Memory commands
    memory = subparsers.add_parser("memory", help="Persistent memory management.")
    memory_sub = memory.add_subparsers(dest="memory_action", required=True)
    memory_sub.add_parser("stats", help="Show memory statistics")
    memory_sub.add_parser("export", help="Export memory to file")
    memory_import = memory_sub.add_parser("import", help="Import memory from file")
    memory_import.add_argument("--import-path", required=True, help="Path to memory file")
    memory_context = memory_sub.add_parser("context", help="Get relevant context for a query")
    memory_context.add_argument("--query", required=True, help="Query to search for")
    memory_context.add_argument("--max-results", type=int, default=5)

    # Weight commands
    weights = subparsers.add_parser("weights", help="Model weight adjustment management.")
    weights_sub = weights.add_subparsers(dest="weights_action", required=True)
    weights_sub.add_parser("summary", help="Show weight adjustment summary")
    weights_get = weights_sub.add_parser("get", help="Get weights for a specific model")
    weights_get.add_argument("--model", required=True, help="Model name")
    weights_reset = weights_sub.add_parser("reset", help="Reset weights for a model")
    weights_reset.add_argument("--model", required=True, help="Model name")
    weights_sub.add_parser("export", help="Export weight adjustments")

    # Continuous flow commands
    flow = subparsers.add_parser("flow", help="Continuous data flow with QR pattern extraction.")
    flow_sub = flow.add_subparsers(dest="flow_action", required=True)
    flow_sub.add_parser("start", help="Start continuous data flow")
    flow_sub.add_parser("stats", help="Show flow statistics")
    flow_sub.add_parser("reset", help="Reset flow state")
    flow_input = flow_sub.add_parser("input", help="Input data into the flow")
    flow_input.add_argument("--text", required=True, help="Text data to process")
    flow_input.add_argument("--source", default="manual", help="Data source identifier")
    flow_input.add_argument("--qr-code", default=None, help="QR code data if present")
    flow_sub.add_parser("output", help="Get processed output from flow")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = _runtime_config(args)

    if args.command == "init-local-store":
        return _cmd_init_store(args, config)
    if args.command == "serve":
        return _cmd_serve(args, config)
    if args.command == "models":
        return _cmd_models(args, config)
    if args.command == "chat":
        return _cmd_chat(args, config)
    if args.command == "discover":
        return _cmd_discover(args, config)
    if args.command == "index":
        return _cmd_index(args, config)
    if args.command == "tune":
        return _cmd_tune_model(args, config)
    if args.command == "memory":
        return _cmd_memory(args, config)
    if args.command == "weights":
        return _cmd_weights(args, config)
    if args.command == "flow":
        return _cmd_flow(args, config)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
