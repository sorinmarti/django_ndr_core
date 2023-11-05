import os
from collections import defaultdict


# Function to count lines, words, and characters in a file
def count_file(filename):
    lines = words = chars = 0
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            lines += 1
            words += len(line.split())
            chars += len(line)
    return lines, words, chars


# Walk through the directory and process each file
def process_directory(directory):
    stats = defaultdict(lambda: {'files': [], 'total_lines': 0, 'total_words': 0, 'total_chars': 0})
    for root, dirs, files in os.walk(directory):
        # Skip directories named "static"
        dirs[:] = [d for d in dirs if d != 'static']
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1]
            try:
                line_count, word_count, char_count = count_file(file_path)
                stats[file_extension]['files'].append((file, line_count, word_count, char_count))
                stats[file_extension]['total_lines'] += line_count
                stats[file_extension]['total_words'] += word_count
                stats[file_extension]['total_chars'] += char_count
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    return stats


# Print the results
def print_stats(stats):
    grand_total_lines = grand_total_words = grand_total_chars = 0
    for extension, data in stats.items():
        """print(f"\nFiles with extension '{extension}':")
        for file, lines, words, chars in data['files']:
            print(f"{file}: Lines = {lines}, Words = {words}, Characters = {chars}")"""
        print(
            f"Total for '{extension}': Lines = {data['total_lines']}, Words = {data['total_words']}, Characters = {data['total_chars']}\n")
        grand_total_lines += data['total_lines']
        grand_total_words += data['total_words']
        grand_total_chars += data['total_chars']

    print(f"Grand Total: Lines = {grand_total_lines}, Words = {grand_total_words}, Characters = {grand_total_chars}")


# Replace 'your_directory_path' with the path to the directory you want to process
directory_to_process = '.'
stats = process_directory(directory_to_process)
print_stats(stats)
