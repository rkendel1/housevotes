import requests
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# Starting URL
base_url = "https://clerk.house.gov/evs/2024/roll"
current_roll = 35  # Starting roll number

while True:
    url = f"{base_url}{current_roll:03d}.xml"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Processing {url}...")

        # Parse the XML content
        root = ET.fromstring(response.content)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define CSV file name with timestamp
        csv_file = f"vote_data_{current_roll}_{timestamp}.csv"

        # Open the CSV file in write mode
        with open(csv_file, "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write metadata to CSV file
            vote_metadata = root.find(".//vote-metadata")
            for child in vote_metadata:
                csvwriter.writerow([child.tag, child.text])

            # Write header row for recorded votes
            csvwriter.writerow(["Name ID", "Vote", "Sort Field", "Party", "State"])

            # Find and print the recorded vote and legislator information
            recorded_votes = root.findall(".//recorded-vote")
            for recorded_vote in recorded_votes:
                legislator_info = recorded_vote.find("legislator")
                name_id = legislator_info.get("name-id")
                vote = recorded_vote.find("vote").text
                sort_field = legislator_info.get("sort-field")
                party = legislator_info.get("party")
                state = legislator_info.get("state")
                # Write data to CSV file
                csvwriter.writerow([name_id, vote, sort_field, party, state])

        print(f"Processed {url} successfully. CSV file '{csv_file}' created.")
        current_roll += 1
    else:
        print("No more results found.")
        break
