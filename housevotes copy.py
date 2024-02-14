import os
import requests
import json
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

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if JSON file already exists for this roll call vote and timestamp
        json_file = f"vote_data_{current_roll}_{timestamp}.json"
        existing_files = [f for f in os.listdir() if f.startswith(f"vote_data_{current_roll}_")]
        if existing_files:
            print(f"JSON file for roll call vote {current_roll} already exists. Skipping...")
            current_roll += 1
            continue

        # Parse the XML content
        root = ET.fromstring(response.content)

        # Initialize a dictionary to hold the data
        vote_data = {}

        # Extract metadata
        metadata_dict = {}
        vote_metadata = root.find(".//vote-metadata")
        for child in vote_metadata:
            if child.tag == "chamber":
                # Replace "House of Representatives" with "house"
                metadata_dict[child.tag] = "house"
            else:
                metadata_dict[child.tag] = child.text
        # Manipulate the metadata elements
        for key, value in metadata_dict.items():
            if key == "session":
                metadata_dict[key] = "2"
            if key == "chamber":
                metadata_dict[key] = "house"
            elif key == "vote-date":
                metadata_dict[key] = datetime.strptime(value, "%Y-%m-%d").strftime("%B %d, %Y")
            elif key == "vote-question":
                metadata_dict[key] = value.upper()


        vote_data["metadata"] = metadata_dict

        # Extract recorded votes
        recorded_votes_list = []
        recorded_votes = root.findall(".//recorded-vote")
        for recorded_vote in recorded_votes:
            legislator_info = recorded_vote.find("legislator")
            recorded_vote_dict = {
                "name_id": legislator_info.get("name-id"),
                "vote": recorded_vote.find("vote").text,
                "sort_field": legislator_info.get("sort-field"),
                "party": legislator_info.get("party"),
                "state": legislator_info.get("state")
            }
            recorded_votes_list.append(recorded_vote_dict)

        vote_data["recorded_votes"] = recorded_votes_list

        # Write data to JSON file
        with open(json_file, "w") as jsonfile:
            json.dump(vote_data, jsonfile, indent=4)

        print(f"Processed {url} successfully. JSON file '{json_file}' created.")
        current_roll += 1

    else:
        print("No more results found.")
        break
