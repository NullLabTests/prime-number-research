#!/usr/bin/env bash
set -euo pipefail

echo "=== Prime Number Research — Reproduction Script ==="

echo ""
echo "Step 1: Install dependencies"
pip install numpy matplotlib seaborn scipy sympy scikit-learn

echo ""
echo "Step 2: Run full research analysis (10 figures, ~2 min)"
python3 research_analysis.py

echo ""
echo "Step 3: Compile PDF paper"
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex

echo ""
echo "Done. Figures in figs/, paper in paper.pdf"
