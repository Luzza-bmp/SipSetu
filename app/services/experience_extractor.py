import re
from datetime import datetime


def extract_experience_years(text):
    # 1. Capture months (words/numbers) and 4-digit years (19xx or 20xx)
    # Handles: "Jan 2020 - Present", "03/2015 to 08/2019", "2010 - 2015"
    months_regex = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})?"
    separator_regex = r"\s*(?:[-–]|to)\s*"
    year_regex = r"((?:19|20)\d{2})"

    # Full pattern to catch: [Month] [Start Year] to [Month] [End Year / Present]
    pattern = rf"\b{months_regex}\s*{year_regex}{separator_regex}(?:{months_regex}\s*{year_regex}|(Present|Current|Now))\b"

    matches = re.findall(pattern, text, re.IGNORECASE)

    if not matches:
        return 0.0

    current_year = datetime.now().year
    intervals = []

    for start_yr, end_yr, present in matches:
        start_year = int(start_yr)

        if present:
            end_year = current_year
        else:
            end_year = int(end_yr)

        # Safeguard against typos in resumes (e.g., 2018 - 2015)
        if start_year <= end_year:
            intervals.append([start_year, end_year])

    if not intervals:
        return 0.0

    # 2. Merge overlapping intervals to prevent double-counting
    # (e.g., Job A: 2018-2022 and Job B: 2020-2023 becomes one span: 2018-2023)
    intervals.sort(key=lambda x: x[0])
    merged_intervals = [intervals[0]]

    for current in intervals[1:]:
        prev_start, prev_end = merged_intervals[-1]
        curr_start, curr_end = current

        if curr_start <= prev_end:  # Overlap found
            merged_intervals[-1][1] = max(prev_end, curr_end)
        else:
            merged_intervals.append(current)

    # 3. Calculate total distinct years
    total_years = sum(end - start for start, end in merged_intervals)

    return float(total_years)
