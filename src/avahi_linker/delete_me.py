import pathlib
filename = "file.txt"

try:
   pathlib.Path(filename).read_text()
except OSError as e:
    print(f"could not read {filename}: {e.strerror}")    