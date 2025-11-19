#!/bin/bash
# Chronicler v4.3 - The Guardian (Command Wrapper Edition)
set -euo pipefail

# --- CONFIGURATION ---
MAX_BACKUPS=10
BACKUP_DIR="$HOME/.local/share/chronicler"
SESSION_DIR="$BACKUP_DIR/sessions"
LOG_FILE="$BACKUP_DIR/chronicler.log"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# --- FUNCTIONS ---
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOG_FILE"
}

print_help() {
    echo "Chronicler v4.3: The Guardian Flight Recorder"
    echo ""
    echo "Usage: chronicler [command] [options]"
    echo ""
    echo "Modes:"
    echo "  (default)           Start a full terminal recording session (The Overseer)."
    echo "  exec <cmd> [args]   Run a specific command wrapped in a recording session."
    echo "  <file_path>         Snapshot a specific file."
    echo ""
    echo "Options:"
    echo "  --list <file>       List backups for a file."
    echo "  --restore <file>    Restore a file."
    echo "  --help              Show this help."
}

dump_file_content() {
    local fpath="$1"
    echo ""
    echo "================================================================"
    echo ">>> CHRONICLER CONTENT DUMP START: $fpath"
    echo "================================================================"
    if [ -f "$fpath" ]; then
        cat "$fpath"
    else
        echo "[File does not exist]"
    fi
    echo ""
    echo "================================================================"
    echo ">>> CHRONICLER CONTENT DUMP END"
    echo "================================================================"
}

# --- TEMPORAL SCRYING (Dynamic Change Detection) ---
scan_for_changes() {
    local session_log="$1"
    local start_time="$2"

    echo "" >> "$session_log"
    echo "######################################################################" >> "$session_log"
    echo "# CHRONICLER OVERSEER REPORT (Modified Artifacts)" >> "$session_log"
    echo "######################################################################" >> "$session_log"
    
    # Use find to locate files modified after the start timestamp.
    # We exclude common noise directories to keep the report clean.
    CHANGES_FOUND=$(find /etc /usr/local/bin "$HOME/.config" "$HOME"         -mount         (             -path "*/.git" -o             -path "*/.cache" -o             -path "*/.local/share" -o             -path "*/node_modules" -o             -path "*/build" -o             -path "*/artifacts" -o             -path "*/.mozilla" -o             -path "*/.vscode" -o             -path "$BACKUP_DIR"         ) -prune         -o -type f -newermt "@$start_time"         ! -name "mtab"         ! -name "adjtime"         ! -name "ld.so.cache"         ! -name "*.log"         ! -name ".zsh_history"         ! -name ".bash_history"         ! -name ".lesshst"         ! -name ".viminfo"         ! -name "*.swp"         ! -name ".Xauthority"         -print 2>/dev/null || true)

    if [ -z "$CHANGES_FOUND" ]; then
        echo ">>> No significant configuration changes detected." >> "$session_log"
        return
    fi

    IFS=$'
'
    for f in $CHANGES_FOUND; do
        # Don't log the session file itself
        if [[ "$f" == "$session_log" ]]; then continue; fi
        
        # Check file size (skip if > 100KB)
        fsize=$(stat -c%s "$f" 2>/dev/null || echo 0)
        if [ "$fsize" -gt 102400 ]; then
            echo ">>> DETECTED MODIFICATION: $f (Skipped - Too Large: ${fsize} bytes)" >> "$session_log"
            continue
        fi

        # Check if binary
        if grep -qI . "$f" 2>/dev/null; then
             echo "" >> "$session_log"
             echo ">>> DETECTED MODIFICATION: $f" >> "$session_log"
             echo "----------------------------------------------------------------------" >> "$session_log"
             cat "$f" >> "$session_log" 2>/dev/null || echo "[Permission Denied - Content Protected]" >> "$session_log"
             echo "" >> "$session_log"
             echo "----------------------------------------------------------------------" >> "$session_log"
        else
             echo ">>> DETECTED MODIFICATION: $f (Skipped - Binary File)" >> "$session_log"
        fi
    done
    unset IFS
}

start_recording() {
    mkdir -p "$SESSION_DIR"
    SESSION_FILE="$SESSION_DIR/session_${TIMESTAMP}.txt"
    START_EPOCH=$(date +%s)
    
    # Tabula Rasa: Full Terminal Reset
    # We use tput reset if available to clear scrollback and state, ensuring a truly clean slate.
    if command -v tput &>/dev/null; then
        tput reset
    else
        clear
    fi
    
    echo "================================================================"
    echo "   KAEL CHRONICLER v4.3 (THE GUARDIAN)   "
    echo "================================================================"
    echo ">>> Flight Recorder Engaged."
    echo ">>> Log File: $SESSION_FILE"
    echo ">>> Temporal Scrying Active: I will watch for ANY file changes."
    echo ">>> Type 'exit' or press Ctrl+D to end session."
    echo "================================================================"
    
    # Start script. When user exits shell, script ends.
    script -f -q "$SESSION_FILE"
    
    echo ">>> The Overseer is scanning for artifacts modified during this session..."
    scan_for_changes "$SESSION_FILE" "$START_EPOCH"
    echo "================================================================"
    echo ">>> CHRONICLER FLIGHT RECORDER STOPPED"
    echo "================================================================"
}

# --- SCRIPT MAIN ---

mkdir -p "$BACKUP_DIR"
mkdir -p "$SESSION_DIR"

if [ $# -eq 0 ]; then
    start_recording
    exit 0
fi

case "$1" in
    --help|-h)
        print_help
        exit 0
        ;;

    exec)
        # Guardian Protocol: Run a single command wrapped in script
        shift
        if [ "$1" == "--" ]; then shift; fi
        if [ $# -eq 0 ]; then echo "Error: No command provided."; exit 1; fi
        
        CMD_NAME=$(basename "$1")
        CMD_ARGS="$*"
        # Use a separate naming convention for command logs
        SESSION_FILE="$SESSION_DIR/cmd_${TIMESTAMP}_${CMD_NAME}.log"
        
        # We do NOT clear the screen for exec mode as it wraps inline commands
        # -q: Quiet start message
        # -e: Return exit code of child process
        # -c: Command to run
        # We allow stdin passthrough for interactive commands like pacman
        
        script -q -e -c "$CMD_ARGS" "$SESSION_FILE"
        exit_code=$?
        
        log "EXEC: '$CMD_ARGS' -> $SESSION_FILE (Exit: $exit_code)"
        exit $exit_code
        ;;

    --record|-r)
        start_recording
        ;;

    --list)
        shift
        FILE_PATH=$1
        if [ ! -f "$FILE_PATH" ]; then echo "Error: File '$FILE_PATH' not found."; exit 1; fi
        FILE_BACKUP_DIR="$BACKUP_DIR/$(realpath -- "$FILE_PATH" | sed 's/\//_/g')"
        
        echo "Available backups for: $FILE_PATH"
        if [ -d "$FILE_BACKUP_DIR" ] && [ "$(ls -A "$FILE_BACKUP_DIR")" ]; then
            ls -1 --color=auto "$FILE_BACKUP_DIR"
        else
            echo "No backups found."
        fi
        ;;

    --cat)
        shift
        FILE_PATH=$1
        dump_file_content "$FILE_PATH"
        ;;

    --restore)
        shift
        FILE_PATH=$1
        if [ ! -f "$FILE_PATH" ]; then echo "Error: File '$FILE_PATH' not found."; exit 1; fi
        FILE_BACKUP_DIR="$BACKUP_DIR/$(realpath -- "$FILE_PATH" | sed 's/\//_/g')"

        if [ ! -d "$FILE_BACKUP_DIR" ] || [ -z "$(ls -A "$FILE_BACKUP_DIR")" ]; then
            echo "Error: No backups found for $FILE_PATH" >&2
            exit 1
        fi
        
        echo "Select a backup to restore for $FILE_PATH:"
        TMP_FILE=$(mktemp)
        trap 'rm -f -- "$TMP_FILE"' EXIT
        find "$FILE_BACKUP_DIR" -mindepth 1 -maxdepth 1 -printf "%f\n" | sort -r > "$TMP_FILE"

        select backup_file in $(cat "$TMP_FILE"); do
            if [ -n "$backup_file" ]; then
                read -p "Restore '$backup_file'? (y/N) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    cp "$FILE_BACKUP_DIR/$backup_file" "$FILE_PATH"
                    echo "Restored."
                    log "RESTORED: '$FILE_PATH' from '$backup_file'"
                    dump_file_content "$FILE_PATH"
                else
                    echo "Restore aborted."
                fi
                break
            else
                echo "Invalid selection."
            fi
        done
        ;;

    --purge)
        shift
        FILE_PATH=$1
        if [ ! -f "$FILE_PATH" ]; then echo "Error: File '$FILE_PATH' not found."; exit 1; fi
        FILE_BACKUP_DIR="$BACKUP_DIR/$(realpath -- "$FILE_PATH" | sed 's/\//_/g')"
        
        if [ -d "$FILE_BACKUP_DIR" ]; then
            ls -t "$FILE_BACKUP_DIR" | tail -n +$(($MAX_BACKUPS + 1)) | xargs -I {} rm -- "$FILE_BACKUP_DIR/{}"
            echo "Purge complete. Kept the latest $MAX_BACKUPS backups for $FILE_PATH."
            log "PURGED: Backups for '$FILE_PATH'"
        else
            echo "No backups found to purge for $FILE_PATH."
        fi
        ;;

    --force)
        shift
        FILE_PATH=$1
        FORCE=true
        # Fall through to default case logic below
        ;;
    
    *)
        # Logic for creating a backup (The default for "chronicler filename")
        if [ "$1" == "--force" ]; then shift; FORCE=true; else FILE_PATH=$1; FORCE=false; fi
        
        if [ ! -f "$FILE_PATH" ]; then
            echo "Error: File not found at '$FILE_PATH'" >&2
            exit 1
        fi

        BASENAME=$(basename -- "$FILE_PATH")
        FILE_BACKUP_DIR="$BACKUP_DIR/$(realpath -- "$FILE_PATH" | sed 's/\//_/g')"
        mkdir -p "$FILE_BACKUP_DIR"
        
        LATEST_BACKUP=$(ls -t "$FILE_BACKUP_DIR" | head -n 1)
        
        if [ "$FORCE" = false ] && [ -n "$LATEST_BACKUP" ]; then
            if cmp -s "$FILE_PATH" "$FILE_BACKUP_DIR/$LATEST_BACKUP"; then
                echo "Info: No changes detected since last backup ('$LATEST_BACKUP')."
                dump_file_content "$FILE_PATH"
                exit 0
            fi
        fi

        BACKUP_FILE="$FILE_BACKUP_DIR/${BASENAME}_${TIMESTAMP}"
        cp "$FILE_PATH" "$BACKUP_FILE"
        
        echo "Chronicler has archived '$FILE_PATH' to:"
        echo "$BACKUP_FILE"
        log "BACKED UP: '$FILE_PATH' to '$BACKUP_FILE'"
        
        dump_file_content "$FILE_PATH"
        ;;
esac
