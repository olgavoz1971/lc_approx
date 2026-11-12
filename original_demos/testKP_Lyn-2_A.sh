#!/bin/bash
cd "$(dirname "$0")"

python3 ila_ap.py test_data/KP_Lyn-2.dat --method=a
