import math
import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Determine the absolute path to the directory containing the running application.

    Why this is critical for both Python scripts and compiled .exe binaries:
    1. PyInstaller unpacks bundled files to a temporary folder referenced by sys._MEIPASS
       when built in '--onefile' mode, OR runs from the executable's directory.
    2. When executed as a regular .py script, '__file__' contains the script's path.
    Using Path(sys.executable).parent guarantees that input/output files are read from
    and written to the actual folder where the user placed the .exe file.
    """
    if getattr(sys, "frozen", False):
        # The application is running as a compiled standalone executable
        # 'sys.executable' points directly to the .exe file
        return Path(sys.executable).resolve().parent
    else:
        # The application is running as a standard Python script (.py)
        # '__file__' contains the full path to this source code file
        return Path(__file__).resolve().parent


def read_file(file_path: Path) -> list[list[float]]:
    """Read coordinate pairs from a plain text file.

    Features and syntax used:
    - Pathlib object 'file_path': Modern, cross-platform path handling.
    - Type hinting ('list[list[float]]'): Introduced in Python 3.9+ for clear API contracts.
    - 'with open(...)': Context manager ensuring file descriptors close properly even on exceptions.
    - str.split() without parameters: Automatically splits by ANY whitespace (spaces, tabs, newlines)
      and discards duplicate adjacent spaces, preventing ValueError crashes.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required coordinate file at: {file_path}")

    coordinates = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            cleaned_line = raw_line.strip()

            # Skip empty lines or trailing empty lines
            if not cleaned_line:
                continue

            parts = cleaned_line.split()
            if len(parts) != 2:
                # Provide descriptive debugging context if a line is malformed
                raise ValueError(
                    f"Line {line_number} in '{file_path.name}' is invalid: expected 2 values, got {len(parts)}."
                )

            # Unpack and cast string values into standard 64-bit IEEE 754 floats
            x, y = float(parts[0]), float(parts[1])
            coordinates.append([x, y])

    return coordinates


def calculate_distance(point1: list[float], point2: list[float]) -> float:
    #Calculate Euclidean distance between two 2D points using math.hypot.
    
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])


def sort_by_proximity(coords_list: list[list[float]]) -> list[list[float]]:
    """Sort coordinates using the Nearest Neighbor heuristic (Greedy TSP approximation).

    Optimization:
    - Instead of repeatedly evaluating 'while False in visited:' (which incurs O(N) cost per step),
      we track remaining points in a set of integer indices: 'unvisited_indices'.
    - Checking set emptiness via 'while unvisited_indices:' runs in O(1) time.
    """
    if not coords_list:
        return []

    # Start with the first point in the list
    sorted_coords = [coords_list[0]]

    # A set of indices [1, 2, ..., n-1] waiting to be visited
    unvisited_indices = set(range(1, len(coords_list)))
    current_point = coords_list[0]

    while unvisited_indices:
        closest_distance = float("inf")
        closest_idx = -1

        # Iterate only through the remaining unvisited indices
        for idx in unvisited_indices:
            dist = calculate_distance(current_point, coords_list[idx])
            if dist < closest_distance:
                closest_distance = dist
                closest_idx = idx

        # Transition state: remove visited point from candidate set and append to result
        unvisited_indices.remove(closest_idx)
        current_point = coords_list[closest_idx]
        sorted_coords.append(current_point)

    return sorted_coords


def main():
    # 1. Resolve working directory dynamically relative to binary/script location
    base_dir = get_base_dir()
    input_file = base_dir / "coords.txt"
    output_file = base_dir / "sortedCoords.txt"

    print(f"Working Directory: {base_dir}")
    print(f"Loading points from: {input_file.name}...")

    # 2. Ingestion and validation
    try:
        raw_coords = read_file(input_file)
    except FileNotFoundError as err:
        print(f"\n[ERROR] {err}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as err:
        print(f"\n[ERROR] Failed reading input file: {err}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    if not raw_coords:
        print("[WARNING] The file is empty. Nothing to process.")
        input("\nPress Enter to exit...")
        return

    # 3. Execution of proximity sorting
    print(f"Processing {len(raw_coords)} points...")
    sorted_coords = sort_by_proximity(raw_coords)

    # 4. Output serialisation
    with open(output_file, mode="w", encoding="utf-8") as file:
        for point in sorted_coords:
            file.write(f"{point[0]} {point[1]}\n")

    print(f"Successfully wrote output to: {output_file.name}")
    print("\nSorted Points Preview (first 5 or all):")
    for pt in sorted_coords[:5]:
        print(f"  {pt}")
    if len(sorted_coords) > 5:
        print(f"  ... and {len(sorted_coords) - 5} more points.")

    # Prevent command-line window from abruptly closing when run directly via double-click on Windows
    input("\nExecution completed. Press Enter to exit...")


# Python's canonical entry point guard: ensures execution only occurs when run directly,
# not when imported as an external module into another script.
if __name__ == "__main__":
    main()