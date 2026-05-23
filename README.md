# MedFramer Agent

An autonomous AI agent with a professional chat interface for biological and medical discovery. MedFramer combines local Ollama models with structured biological data ingestion to generate lab-grade results with comprehensive explanations.

## Overview

MedFramer is designed for lab-grade professionals who need to:
- Input biological/medical queries through a professional CLI interface
- Receive working biological results (analysis, protocols, code)
- Understand the optimal discovery process with detailed explanations
- Leverage recursive pattern extraction from biological data structures

## Architecture

```
┌─────────────────────┐
│ Lab Professional    │
│ Input              │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ CLI Interface       │
│ (medframer_cli.py) │
└──────────┬──────────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
┌─────────────────┐  ┌─────────────────────┐
│ Ollama Model    │  │ Discovery Pipeline │
│ Operations      │  │                     │
└─────────────────┘  └──────────┬──────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Medframework Ingestion  │
                    │ (data structure feeds)  │
                    └──────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ Recursive Pattern       │
                    │ Engine (ASI Core)       │
                    └──────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ Node Mesh Store         │
                    │ (document/term links)   │
                    └──────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ Structured Biological  │
                    │ Result + Explanation    │
                    └─────────────────────────┘
```

## Project Structure

```
BIO/
├── CLi/                          # User entrypoints and command workflows
│   ├── __init__.py
│   └── medframer_cli.py          # Main CLI interface
├── asi core/                     # Autonomous processing logic
│   └── light_asi_core/
│       ├── __init__.py
│       ├── config.py             # Runtime configuration
│       ├── types.py              # Data structures
│       ├── utils.py              # Utility functions
│       ├── ollama_client.py      # Ollama API client
│       ├── medframework_ingest.py # Data ingestion from medframeworks
│       ├── pattern_engine.py     # Recursive pattern extraction
│       ├── node_mesh.py          # Node mesh storage
│       ├── explanation_engine.py # Explanation generation
│       └── discovery_agent.py    # Main discovery orchestration
├── medframeworks/               # Biological data/process source tree
│   ├── fix vocab/
│   └── safe - depression med - tech/
├── MEDFRAMER_AGENT_SPEC.md       # Detailed specification
├── README.md                     # This file
└── .gitignore                    # Repository hygiene rules
```

## Features

### CLI Commands

- **init-local-store**: Create local model store and environment helper script
- **serve**: Run Ollama server with project-local model path
- **models**: Model lifecycle operations (list, pull, show, rm, ps, stop)
- **chat**: Interactive chat session for lab professionals
- **discover**: Run autonomous discovery pipeline with explanation output
- **index**: Ingest medframework data and refresh node-mesh

### Core Capabilities

1. **Local Model Management**: Download, list, and manage Ollama models in project-local store
2. **Interactive Chat**: Professional chat interface with customizable system prompts
3. **Autonomous Discovery**: End-to-end pipeline from query to structured biological results
4. **Pattern Extraction**: Recursive signal detection across biological documents
5. **Node Mesh Storage**: Persistent graph of document/term/co-occurrence relationships
6. **Explanation Engine**: Comprehensive process transparency with evidence mapping

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running ([https://ollama.com](https://ollama.com))
- Git (for cloning the repository)

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/JlovesYouGit/medframer-agent.git
cd medframer-agent
```

2. **Install Ollama** (if not already installed):
```bash
# On Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# On Windows
# Download from https://ollama.com/download
```

3. **Initialize local model store**:
```bash
python -m CLi.medframer_cli init-local-store
```

This creates:
- `models_store/` directory for local model files
- `CLi/set_ollama_env.ps1` PowerShell helper script

4. **Start Ollama server**:
```bash
python -m CLi.medframer_cli serve
```

Or run directly with Ollama:
```bash
ollama serve
```

5. **Download a model**:
```bash
python -m CLi.medframer_cli models pull llama3.2
```

## Usage

### Interactive Chat

Start a chat session with a downloaded model:

```bash
python -m CLi.medframer_cli chat --model llama3.2
```

Customize the chat experience:
```bash
python -m CLi.medframer_cli chat \
  --model llama3.2 \
  --temperature 0.2 \
  --system-prompt "You are a specialized biomedical research assistant."
```

### Autonomous Discovery

Run the discovery pipeline with biological context:

```bash
python -m CLi.medframer_cli discover \
  --model llama3.2 \
  --query "Analyze potential drug interactions for SSRI medications" \
  --format markdown \
  --output discovery_result.md
```

Options:
- `--model`: Required. Ollama model name
- `--query`: Required. Biological/medical query
- `--medframework-root`: Optional. Path to medframeworks directory
- `--max-files`: Maximum files to ingest (default: 300)
- `--format`: Output format (json/markdown, default: markdown)
- `--output`: Optional. File path to save results

### Index Medframework Data

Refresh the node-mesh without calling the model:

```bash
python -m CLi.medframer_cli index \
  --medframework-root medframeworks \
  --max-files 300
```

### Model Management

List available models:
```bash
python -m CLi.medframer_cli models list
```

Show model metadata:
```bash
python -m CLi.medframer_cli models show llama3.2
```

Remove a model:
```bash
python -m CLi.medframer_cli models rm llama3.2
```

## Output Format

### Markdown Output

The discovery command generates structured markdown with:

```markdown
# Discovery Result: [query]

Model: `llama3.2`

## Working Biological Result
- Type: analysis/protocol/code
- Title: [result title]
[content]

## Optimal Discovery Process
1. [action] — [rationale]
2. [action] — [rationale]
...

## Explanation Module
[summary and rationale]

## Evidence Endpoints
- `file://[path]`
- `file://[path]`
```

### JSON Output

Structured JSON with complete metadata:

```json
{
  "query": "...",
  "model": "llama3.2",
  "working_result": {
    "result_type": "analysis",
    "title": "...",
    "content": "...",
    "assumptions": [...],
    "validation_steps": [...],
    "limitations": [...]
  },
  "optimal_discovery_process": [...],
  "explanation_module": {...},
  "pattern_snapshot": {...},
  "evidence_endpoints": [...],
  "knowledge_stats": {...}
}
```

## How It Works

### 1. Data Ingestion

The system ingests files from the `medframeworks/` directory:
- Supports: `.py`, `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.csv`, `.toml`
- Skips: `venv`, `.venv`, `__pycache__`, `.git`, `node_modules`
- Generates file:// endpoint URLs for traceability

### 2. Pattern Extraction

The Recursive Pattern Engine analyzes ingested documents:
- Extracts top terms by frequency
- Identifies co-occurring term pairs
- Detects recursive signals across documents
- Ranks patterns by document presence and frequency

### 3. Node Mesh Construction

Builds a persistent graph structure:
- **Document nodes**: File metadata and checksums
- **Term nodes**: Extracted vocabulary terms
- **Contains edges**: Document-term relationships
- **Co-occurrence edges**: Term-term relationships with weights

### 4. Discovery Pipeline

When processing a query:
1. Ingests and indexes medframework data
2. Builds pattern report from documents
3. Constructs context-aware prompt for Ollama
4. Requests structured JSON output from model
5. Normalizes and validates response
6. Generates comprehensive explanation
7. Maps evidence to source endpoints

### 5. Explanation Generation

The Explanation Engine provides:
- High-level summary of discovery process
- Query focus and rationale
- Supporting evidence endpoints
- Model output metadata
- Safety and validation recommendations

## Configuration

### Environment Variables

- `OLLAMA_BASE_URL`: Ollama API endpoint (default: `http://127.0.0.1:11434`)
- `OLLAMA_MODELS`: Local model store path (default: `models_store/`)
- `MEDFRAMEWORK_ROOT`: Path to medframeworks directory
- `MEDFRAMEWORK_MAX_FILES`: Maximum files to ingest (default: 300)
- `MEDFRAMEWORK_MAX_FILE_BYTES`: Maximum file size in bytes (default: 1048576)
- `NODE_MESH_PATH`: Path to node mesh storage (default: `node_mesh/mesh_store.json`)

### Runtime Configuration

The system can be configured via CLI arguments or environment variables. See `--help` for each command:

```bash
python -m CLi.medframer_cli --help
python -m CLi.medframer_cli discover --help
```

## Development

### Project Structure Contract

- `CLi/` owns user entrypoints and command workflows
- `asi core/` owns autonomous processing logic (Light ASI Core modules)
- `medframeworks/` remains the biological data/process source tree

### Adding New Commands

Edit `CLi/medframer_cli.py`:
1. Add command function following `_cmd_*` pattern
2. Register subparser in `_build_parser()`
3. Add routing logic in `main()`

### Extending Pattern Engine

Modify `asi core/light_asi_core/pattern_engine.py`:
- Adjust stopword lists
- Modify token extraction logic
- Add new pattern detection algorithms

### Custom Data Sources

Extend `asi core/light_asi_core/medframework_ingest.py`:
- Add new file suffixes to `DEFAULT_SUFFIXES`
- Implement custom validation logic
- Add specialized parsers for specific formats

## Troubleshooting

### Ollama Connection Error

**Problem**: `Ollama connection error: Could not reach Ollama at http://127.0.0.1:11434`

**Solution**: Start Ollama server:
```bash
ollama serve
```

Or use the CLI:
```bash
python -m CLi.medframer_cli serve
```

### Model Not Found

**Problem**: Model not available after download

**Solution**: Check model list:
```bash
python -m CLi.medframer_cli models list
```

Re-download if needed:
```bash
python -m CLi.medframer_cli models pull llama3.2
```

### No Documents Indexed

**Problem**: Discovery returns no context

**Solution**: 
- Verify medframeworks directory exists and contains files
- Check file suffixes are supported
- Increase `--max-files` limit
- Check file size limits

### JSON Parse Errors

**Problem**: Model returns non-JSON response

**Solution**: 
- System includes fallback handling
- Try lower temperature: `--temperature 0.1`
- Use simpler model or different prompt
- Check model supports structured output

## Performance Considerations

- **File Ingestion**: Limited by `max_files` and `max_file_bytes` configuration
- **Pattern Extraction**: O(n²) for co-occurrence detection on top terms
- **Model Calls**: Single request per discovery (no streaming)
- **Node Mesh**: JSON storage, suitable for <10,000 documents
- **Memory**: Pattern extraction holds all documents in memory

## Security and Safety

- **No External APIs**: Uses only local Ollama models
- **File Isolation**: Medframework data ingested from local filesystem
- **No Model Weights in Git**: .gitignore excludes all model artifacts
- **Validation Required**: All outputs include validation steps and limitations
- **Traceability**: All results include source file endpoints

## License

This project is provided as-is for biological and medical research purposes.

## Contributing

Contributions should follow the project structure contract:
- Preserve directory ownership (CLi/, asi core/, medframeworks/)
- Maintain type hints and docstrings
- Add tests for new functionality
- Update documentation for interface changes

## Acknowledgments

- Built with [Ollama](https://ollama.com) for local model inference
- Inspired by agent-97 AGI framework structure
- Designed for lab-grade biological and medical discovery

## Contact

For issues, questions, or contributions, visit the repository:
https://github.com/JlovesYouGit/medframer-agent
