# hello-world
Baby Steps

## Install Claude Code in your terminal

Claude Code is Anthropic's official CLI for Claude. Pick the install method that matches your environment.

### Prerequisites
- macOS, Linux, or Windows (via WSL)
- Node.js 18 or newer (only required for the npm install method)
- An Anthropic account

### Install with the native installer (recommended)

macOS / Linux / WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

### Install with npm

```bash
npm install -g @anthropic-ai/claude-code
```

### First run

Start Claude Code from any project directory:

```bash
claude
```

On first launch you'll be prompted to sign in with your Anthropic account. After that, type your request at the prompt and Claude will read files, run commands, and edit code in the current directory.

### Useful commands
- `claude` — start an interactive session in the current directory
- `claude --help` — list all flags and subcommands
- `/help` — in-session help
- `/config` — change model, theme, and other settings

### Docs
Full documentation: https://docs.claude.com/en/docs/claude-code
