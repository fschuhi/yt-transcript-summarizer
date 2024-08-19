import os
import sys


def print_file_content(filename):
    print(f"{'=' * 20} {filename} {'=' * 20}")
    with open(filename, 'r') as file:
        print(file.read().rstrip())

def main():
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print("Usage: python script.py <filename>")
        print("The file should contain a list of filenames to process.")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Current directory path: {os.getcwd()}")
    print()

    try:
        with open(input_file, 'r') as file:
            filelist = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    for i, filename in enumerate(filelist):
        if filename.startswith('./'):
            filename = filename[2:]
        
        try:
            print_file_content(filename)
            if i < len(filelist) - 1:
                print()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            sys.exit(1)

if __name__ == "__main__":
    main()