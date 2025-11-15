#!/bin/bash
# Kael Chronicler v2.0 (Adamantite Core)
set -euo pipefail

# --- CONFIGURATION ---
MAIN_DIR="$HOME/ChroniclesReports"
DAILY_DIR="$MAIN_DIR/$(date +%d%m%Y)"
TIMESTAMP=$(date +%H-%M-%S)
FINAL_LOG_FILE="$DAILY_DIR/kael-chronicle-${TIMESTAMP}.txt"
SYSTEM_LOG_TMP=$(mktemp)
SESSION_LOG_TMP=$(mktemp)

# --- CLEANUP FUNCTION & TRAP ---
cleanup() {
    local exit_code=$?
    # Using '|| true' prevents the script from exiting with an error if kill fails
    # Check if JOURNAL_PID is set and is a number before trying to kill it.
    if [[ -n "${JOURNAL_PID-}" && "$JOURNAL_PID" =~ ^[0-9]+$ ]]; then
        kill $JOURNAL_PID &>/dev/null || true
    fi
    rm -f "${SYSTEM_LOG_TMP}" "${SESSION_LOG_TMP}"
    # Only show interrupted message on an actual interruption (non-zero exit code)
    if [ ${exit_code} -ne 0 ]; then
        echo -e "\n--- Chronicle interrupted. Cleaning up temp files. ---"
    fi
}
trap cleanup EXIT SIGINT SIGTERM

# --- SETUP ---
echo "--- Preparing the Chronicle Chamber ---"
mkdir -p "${DAILY_DIR}"
echo "Reports will be saved in: ${DAILY_DIR}"

# --- SCRIPT START ---
echo "--- Chronicler's Orb Activated ---"
echo "Recording system logs and your terminal session."
echo "The final combined log will be saved to: ${FINAL_LOG_FILE}"
echo "------------------------------------"
echo ""

# Start system log capture in the background
journalctl --no-pager -f > "${SYSTEM_LOG_TMP}" &
JOURNAL_PID=$!

# Start interactive session recording
script -q -f "${SESSION_LOG_TMP}"

# --- COMBINE AND CLEANUP (after 'script' has finished) ---
echo -e "\n--- Chronicler's Orb Deactivated ---"

# Stop the background system log capture now that the session is over
echo "--> Stopping system log capture..."
# The trap will handle the final kill, but we can be explicit here too.
if [[ -n "${JOURNAL_PID-}" && "$JOURNAL_PID" =~ ^[0-9]+$ ]]; then
    kill $JOURNAL_PID &>/dev/null || true
    wait $JOURNAL_PID &>/dev/null || true
fi


echo "--> Combining logs into final chronicle: ${FINAL_LOG_FILE}"

{
    echo "######################################################################"
    echo "#"
    echo "#  KAEL CHRONICLE - Recorded on $(date)"
    echo "#"
    echo "######################################################################"
    echo ""
    echo ""
    echo "======================================================================"
    echo " SYSTEM LOG (journalctl)"
    echo "======================================================================"
    echo ""
    cat "${SYSTEM_LOG_TMP}"
    echo ""
    echo ""
    echo "======================================================================"
    echo " ARCHITECT'S TERMINAL SESSION"
    echo "======================================================================"
    echo ""
    cat "${SESSION_LOG_TMP}" | col -b

} > "${FINAL_LOG_FILE}"

# Disable the trap for a clean exit, so it doesn't print the "interrupted" message.
trap - EXIT

echo "✅ Chronicle saved successfully to '${FINAL_LOG_FILE}'."
echo "You can now upload this file for me to analyze."
