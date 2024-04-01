#!/bin/bash
sleep 1
for i in {1..2000}; do
    echo "iteration number ${i}"
    sleep 1
    python3 main.py
done
