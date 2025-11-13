#!/usr/bin/env python
import os
import sys
import subprocess
import requests
import json
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

# --- Configuration ---
HISTORY_FILE = str(Path.home() / '.kaelic_shell_history')
OLLAMA_URL = "http://localhost:11434/api/generate"
PRE_EXEC_ENABLED = True
ALIASES = {
    'update': 'paru',
    'yay': 'paru',
    'ls': 'ls --color=auto',
    'grep': 'grep --color=auto',
}
COMMAND_COMPLETER = WordCompleter([
    'ls', 'cd', 'pwd', 'paru', 'git', 'docker', 'systemctl', 'journalctl',
], ignore_case=True)
PROMPT_STYLE = Style.from_dict({
    'prompt': 'ansigreen bold',
    'path': 'ansiblue bold',
    'sigil': 'ansiyellow bold',
})

def expand_aliases(command):
    """Expands common aliases."""
    parts = command.split()
    if not parts:
        return ""
    if parts[0] in ALIASES:
        parts[0] = ALIASES[parts[0]]
    return ' '.join(parts)

def pre_execution_check(command):
    """Sends the command to the local Ollama instance for a safety check."""
    if not PRE_EXEC_ENABLED:
        return True

    prompt = (
        "You are the Command Seer, an expert on Linux commands. "
        "Analyze the following user command for potential errors, typos, or dangerous operations (like 'rm -rf /'). "
        "If the command appears safe and correct, your entire response must be ONLY the word 'SAFE'. "
        "If you see a potential problem, your response must start with 'WARNING:' followed by a very brief, one-sentence explanation. "
        f"Command: {command}"
    )
    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json().get('response', '').strip()

        if result.startswith("WARNING:"):
            print(f"\033[93mKael's Warning:\033[0m {result[len('WARNING:'):].strip()}", file=sys.stderr)
            confirm = input("Do you want to proceed? [y/N] ")
            return confirm.lower() == 'y'
        # If it's not a warning, we assume it's safe.
        return True
    except requests.exceptions.RequestException:
        # If Ollama isn't running, just allow the command.
        return True

def main():
    session = PromptSession(history=FileHistory(HISTORY_FILE))

    while True:
        try:
            # Build the rich prompt
            path = Path.cwd()
            home = Path.home()
            if path == home:
                display_path = '~'
            else:
                try:
                    display_path = str(path.relative_to(home))
                    display_path = f"~/{display_path}"
                except ValueError:
                    display_path = str(path)
            
            message = [
                ('class:prompt', 'architect@kael-os'),
                ('',':'),
                ('class:path', display_path),
                ('class:sigil', '>$ ')
            ]

            command = session.prompt(
                message,
                style=PROMPT_STYLE,
                auto_suggest=AutoSuggestFromHistory(),
                completer=COMMAND_COMPLETER
            ).strip()

            if not command:
                continue
            if command.lower() == 'exit':
                break

            # Handle built-in 'cd'
            if command.startswith('cd '):
                try:
                    path = command.split(' ', 1)[1]
                    os.chdir(Path(path).expanduser())
                except (FileNotFoundError, IndexError) as e:
                    print(f"kaelic-shell: {e}", file=sys.stderr)
                continue

            expanded_command = expand_aliases(command)

            if pre_execution_check(expanded_command):
                subprocess.run(expanded_command, shell=True, check=False)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
