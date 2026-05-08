from pathlib import Path


ROOTS = [Path("app"), Path("tests")]
EXTENSIONS = {".py", ".css", ".js", ".html"}

MOJIBAKE_MARKERS = [
    "\ufffd",
    "\u929d",
    "\u875f",
    "\u9788",
    "\u569a",
    "\u64a3",
    "\u61ad",
    "\u875e",
    "\u6470",
    "\u7603",
    "\u922d",
    "\u95b0",
    "\u7508",
    "\uee38",
]


def iter_files():
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                yield path


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def count_markers(text):
    return sum(text.count(marker) for marker in MOJIBAKE_MARKERS)


def suspicious_lines(text):
    high = []
    review = []
    for number, line in enumerate(text.splitlines(), start=1):
        high_score = count_markers(line)
        non_ascii = sum(1 for char in line if ord(char) > 127)
        question_marks = line.count("?")
        private_use = sum(1 for char in line if 0xE000 <= ord(char) <= 0xF8FF)
        if private_use:
            high_score += private_use * 3
        if high_score:
            high.append((number, high_score, line.strip()[:160]))
            continue
        if non_ascii and question_marks >= 2 and "??" not in line:
            review.append((number, question_marks, line.strip()[:160]))
    return high, review


def main():
    results = []
    for path in iter_files():
        text = read_text(path)
        marker_count = count_markers(text)
        replacement_count = text.count("\ufffd")
        high_lines, review_lines = suspicious_lines(text)
        line_score = sum(item[1] for item in high_lines)
        review_score = sum(item[1] for item in review_lines)
        if marker_count or replacement_count or line_score or review_score:
            results.append((line_score, review_score, replacement_count, path, high_lines[:8], review_lines[:8]))

    results.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)

    print("text issue scan")
    print("files_with_issues", len(results))
    print()

    for high_score, review_score, replacement_count, path, high_lines, review_lines in results[:40]:
        print(f"{path} high={high_score} review={review_score} replacement={replacement_count}")
        for number, score, preview in high_lines:
            safe_preview = preview.encode("unicode_escape").decode("ascii")
            print(f"  high line {number} score={score} {safe_preview}")
        for number, score, preview in review_lines:
            safe_preview = preview.encode("unicode_escape").decode("ascii")
            print(f"  review line {number} score={score} {safe_preview}")
        print()


if __name__ == "__main__":
    main()
