import os

# /Users/tabaro/cloudquery.log
def collect_files_content(root_dir=".", output_file="/Users/tabaro/output.txt", exclude_folder=".venv"):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip the excluded folder
            if exclude_folder in dirpath.split(os.sep):
                continue

            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(f"\n--- Start of {file_path} ---\n")
                        outfile.write(infile.read())
                        outfile.write(f"\n--- End of {file_path} ---\n")
                except Exception as e:
                    # Skip files that can't be read as text
                    outfile.write(f"\n--- Could not read {file_path}: {e} ---\n")

if __name__ == "__main__":
    collect_files_content()
