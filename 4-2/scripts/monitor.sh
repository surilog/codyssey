#!/bin/bash

PID=$(pgrep -n -f agent-leak-app)
LOG_FILE="/var/log/agent-app/agent_app.log"
MONITOR_LOG="/var/log/agent-app/monitor.log"

if [ -z "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] PROCESS:down" >> "$MONITOR_LOG"
    exit 1
fi

MEM_MB=$(ps -o rss= -p $PID | awk '{print int($1/1024)}')
MEM_PCT=$(ps -o pmem= -p $PID)
CPU_PCT=$(ps -o pcpu= -p $PID)
LOG_IDLE=0

if [ -f "$LOG_FILE" ]; then
    LOG_IDLE=$(( $(date +%s) - $(stat -c %Y "$LOG_FILE") ))
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] PID:$PID STAT:S CPU:${CPU_PCT}% RSS:${MEM_MB}MB MEM:${MEM_PCT}% LOG_IDLE:${LOG_IDLE}s" >> "$MONITOR_LOG"