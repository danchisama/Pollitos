#!/bin/bash
# Script para iniciar el receptor UDP en segundo plano

LOG_DIR="./logs"
if [ ! -d "$LOG_DIR" ]; then
  mkdir -p "$LOG_DIR"
  fi

  echo "Iniciando receptor de Pollitos..."
  nohup python app/receiver.py > "$LOG_DIR/receiver_nohup.out" 2>&1 &
  echo "Receptor iniciado con PID $!"
  
