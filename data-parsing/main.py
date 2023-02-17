from typing import Dict, List, Tuple
import re
import sys
import os

REQUIRED_ARG_LENGTH = 3

HEADER_PATTERN = r"[{\s]'\w+/(\w+)':.+?[,}]"
JSON_PATTERN = r"[{\s]'\w+/(\w+)':\s['\"](.+?)['\"][,}]"

REVIEW_START_INDEX = 5
PROFILE_NAME_INDEX = 11
REGEX_VALUE_INDEX = 1

def main(data_path: str, output_directory: str) -> None:
    if not os.path.isfile(data_path):
        print(f"{output_directory} is not a valid file.")
        return

    if not os.path.isdir(output_directory):
        print(f"{output_directory} is not a valid directory.")
        return

    print(f"Opening data file: {data_path}")
    with open(data_path, "r") as file:
        print("Reading file... ", end="")
        lines = file.readlines()
    print("done")

    print("Creating data collection entities")
    headers: List[str] = re.findall(HEADER_PATTERN, lines[0])
    headers = [f"{item[0].upper()}{item[1:]}" for item in headers]

    beers: Dict[str, object] = {}
    beers["header"] = ",".join(headers[:REVIEW_START_INDEX])

    reviews: List[str] = []
    reviews.append(",".join(["BeerName"] + headers[REVIEW_START_INDEX:]))

    users = set()

    def format_entry(items: List[str]) -> str:
        return ",".join(f'"{item[REGEX_VALUE_INDEX]}"' for item in items)

    pattern = re.compile(JSON_PATTERN)
    print("Starting parsing")
    for i, line in enumerate(lines):
        if i % 100000 == 0 and i != 0:
            print(f"Parsed {i} lines")
        try:
            regex_result: List[Tuple[str, str]] = pattern.findall(line)

            beer_attributes = regex_result[:REVIEW_START_INDEX]
            entry = format_entry(beer_attributes)

            BEER_NAME_INDEX = 0
            beer_name = beer_attributes[BEER_NAME_INDEX][REGEX_VALUE_INDEX]
            if not beer_name in beers:
                beers[beer_name] = entry

            review_attributes = [beer_attributes[BEER_NAME_INDEX]] + regex_result[REVIEW_START_INDEX:]
            entry = format_entry(review_attributes)
            reviews.append(entry)

            users.add(regex_result[PROFILE_NAME_INDEX][1])
        except IndexError as e:
            break
        except Exception as e:
            print(e)
            print(f"Error while parsing line: {i}\nExiting program")
            return
    print("Done parsing")

    print("Writing beers.csv... ", end="")
    with open("beers.csv", "w") as file:
        file.write("\n".join(beers.values()))
    print("done")

    print("Writing reviews.csv... ", end="")
    with open("reviews.csv", "w") as file:
        file.write("\n".join(reviews))
    print("done")

    print("Writing users.csv... ", end="")
    with open("users.csv", "w") as file:
        file.write("Username\n")
        file.write("\n".join(list(users)))
    print("done")

if len(sys.argv) != REQUIRED_ARG_LENGTH:
    print("Invalid call. Please provide the source json file and output directory as arguments.")
    exit()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
