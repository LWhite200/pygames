import os

def read_grid_file(file_path):
    """Reads a grid file and extracts the grid data and Areas.append line."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
        grid = []
        areas_append_line = None
        for line in lines:
            if line.strip() and not line.strip().startswith("Areas.append"):
                # Parse grid row
                row = [int(num) for num in line.strip().split()]
                grid.append(row)
            elif line.strip().startswith("Areas.append"):
                # Capture the Areas.append line
                areas_append_line = line.strip()
        return grid, areas_append_line

def generate_master_grids(output_file, grids_folder):
    """Generates the masterGrids.py file with all grids and Areas.append logic."""
    grids = {}
    areas_appends = []

    # Read all .txt files in the grids folder
    for filename in os.listdir(grids_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(grids_folder, filename)
            grid_name = filename[:-4]  # Remove '.txt' from the filename
            grid, areas_append_line = read_grid_file(file_path)
            grids[grid_name] = grid
            if areas_append_line:
                areas_appends.append(areas_append_line)

    # Write the masterGrids.py file
    with open(output_file, 'w') as f:
        # Write all grids
        for grid_name, grid in grids.items():
            f.write(f"{grid_name} = [\n")
            for row in grid:
                f.write(f"    {row},\n")
            f.write("]\n\n")
        
        # Write the main function
        f.write("def main():\n")
        f.write("    Areas = []\n\n")
        
        # Write all Areas.append statements
        for areas_append in areas_appends:
            f.write(f"    {areas_append}\n")
        
        f.write("\n    return Areas\n\n")
        
        f.write("if __name__ == \"__main__\":\n")
        f.write("    main()\n")

if __name__ == "__main__":
    # Folder containing grid files
    grids_folder = "grids.txt"  # Ensure this folder exists and contains .txt files
    # Output file
    output_file = "masterGrids.py"
    
    # Generate the masterGrids.py file
    generate_master_grids(output_file, grids_folder)
    print(f"Generated {output_file} with all grids and Areas.append statements.")