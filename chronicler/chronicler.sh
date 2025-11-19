#!/bin/bash
# Chronicler v3.1 - The Black Box Flight Recorder
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
    echo "Chronicler: The diligent scribe and flight recorder."
    echo ""
    echo "Usage: chronicler [command] [options]"
    echo ""
    echo "Default (No Args): Starts a Flight Recorder session (captures all terminal output)."
    echo ""
    echo "Commands:"
    echo "  <file_path>         Smart backup: Backs up file AND DUMPS CONTENT to terminal."
    echo "                      (This allows the Flight Recorder to capture the config state)."
    echo "  --force <file>      Force a backup even if no changes are detected."
    echo "  --cat <file>        Just output the file content (for logging purposes)."
    echo "  --purge <file>      Purge old backups for a file."
    echo "  --list <file>       List available backups."
    echo "  --restore <file>    Interactively restore a file."
    echo "  --help              Show this help message."
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

start_recording() {
    mkdir -p "$SESSION_DIR"
    SESSION_FILE="$SESSION_DIR/session_${TIMESTAMP}.txt"
    
    echo "================================================================"
    echo ">>> CHRONICLER FLIGHT RECORDER ENGAGED"
    echo ">>> Recording entire terminal session to:"
    echo ">>> $SESSION_FILE"
    echo ">>>"
    echo ">>> Type 'exit' or press Ctrl+D to stop recording."
    echo "================================================================"
    
    # Use 'script' to record everything to the file.
    # -f flushes output after each write
    # -q be quiet about start/stop messages
    # 'script' will spawn a new shell. When that shell exits, recording stops.
    script -f -q "$SESSION_FILE"
    
    echo "================================================================"
    echo ">>> CHRONICLER FLIGHT RECORDER STOPPED"
    echo ">>> Log saved to: $SESSION_FILE"
    echo "================================================================"
    echo ">>> You can now upload this txt file to Kael for analysis."
}

# --- SCRIPT MAIN ---

mkdir -p "$BACKUP_DIR"

# DEFAULT BEHAVIOR: If no arguments, start the Flight Recorder.
if [ $# -eq 0 ]; then
    start_recording
    exit 0
fi

# --- COMMAND HANDLING ---
case "$1" in
    --help|-h)
        print_help
        exit 0
        ;;

    --record|-r)
        # Explicit record flag (alias for default)
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
        # Utility to just dump a file to the log without backing up
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
                    # Dump the restored content so the log knows what's current
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
        
        # Smart Check: Compare with latest backup
        LATEST_BACKUP=$(ls -t "$FILE_BACKUP_DIR" | head -n 1)
        
        if [ "$FORCE" = false ] && [ -n "$LATEST_BACKUP" ]; then
            if cmp -s "$FILE_PATH" "$FILE_BACKUP_DIR/$LATEST_BACKUP"; then
                echo "Info: No changes detected since last backup ('$LATEST_BACKUP')."
                # CRITICAL: Even if we skip backup, DUMP CONTENT so it appears in the Flight Recorder log.
                dump_file_content "$FILE_PATH"
                exit 0
            fi
        fi

        BACKUP_FILE="$FILE_BACKUP_DIR/${BASENAME}_${TIMESTAMP}"
        cp "$FILE_PATH" "$BACKUP_FILE"
        
        echo "Chronicler has archived '$FILE_PATH' to:"
        echo "$BACKUP_FILE"
        log "BACKED UP: '$FILE_PATH' to '$BACKUP_FILE'"
        
        # CRITICAL: Dump content so it appears in the Flight Recorder log.
        dump_file_content "$FILE_PATH"
        ;;
esac
