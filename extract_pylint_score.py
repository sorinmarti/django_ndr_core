"""Helper module to extract pylint score from the output file and update the README with the badge"""
import re


def extract_pylint_score(file_path):
    """Extracts the pylint score from the output file"""

    try:
        with open(file_path, 'r', encoding='utf8') as file:
            content = file.read()
            # Regex to match the pylint score pattern
            match = re.search(r'rated at ([0-9.]+)/10', content)
            if match:
                return match.group(1)  # Returns the captured score
            return "Score not found"
    except FileNotFoundError:
        return "File not found"


def update_readme_with_badge(score, readme_file_path='README.md'):
    """Updates the README with the badge"""

    badge_url = f"https://mperlet.github.io/pybadge/badges/{score}.svg"
    badge_md = f"![pylint score]({badge_url})"

    with open(readme_file_path, 'r', encoding='utf8') as file:
        readme_content = file.read()

    # Assuming you have a placeholder text in your README like: ![pylint score](old_url)
    updated_content = re.sub(r'!\[pylint score]\(.*\)', badge_md, readme_content)

    with open(readme_file_path, 'w', encoding='utf8') as file:
        file.write(updated_content)


if __name__ == "__main__":
    my_score = extract_pylint_score('output.txt')
    update_readme_with_badge(my_score)
