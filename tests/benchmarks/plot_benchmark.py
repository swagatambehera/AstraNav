
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Locate the AstraNav project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Input and output paths
CSV_PATH = PROJECT_ROOT / "tests" / "benchmarks" / "benchmark_comparison.csv"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "screenshots"
OUTPUT_FILE = OUTPUT_DIR / "algorithm_comparison.png"

# Read and display benchmark data
df = pd.read_csv(CSV_PATH)

print("\n=== BENCHMARK COMPARISON DATA ===")
print(df.to_string(index=False))

# Verified measurements from benchmark-final-v2
algorithms = ["Dijkstra", "Bidirectional Dijkstra"]

explored_vertices = [19.000000, 13.593651]

execution_time = [
    0.001211387294,
    0.001577019508
]

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Create two comparison charts
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Chart 1: Mean explored vertices
bars1 = axes[0].bar(algorithms, explored_vertices)

axes[0].set_title("Mean Explored Vertices")
axes[0].set_ylabel("Number of Vertices")
axes[0].tick_params(axis="x", rotation=10)
axes[0].bar_label(bars1, fmt="%.3f", padding=3)
axes[0].grid(axis="y", linestyle="--", alpha=0.4)

# Chart 2: Mean execution time
bars2 = axes[1].bar(algorithms, execution_time)

axes[1].set_title("Mean Execution Time")
axes[1].set_ylabel("Execution Time (ms)")
axes[1].tick_params(axis="x", rotation=10)
axes[1].bar_label(bars2, fmt="%.6f", padding=3)
axes[1].grid(axis="y", linestyle="--", alpha=0.4)

fig.suptitle(
    "AstraNav: Dijkstra vs Bidirectional Dijkstra",
    fontsize=14
)

plt.tight_layout()

# Save high-resolution image
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")

print(f"\nChart successfully saved at:\n{OUTPUT_FILE}")

plt.show()
