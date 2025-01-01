import json
import asyncio
import aiofiles
from datetime import datetime
import os

async def append_to_json(file_path, new_data):
    # Check if the file exists and create if not
    if not os.path.exists(file_path):
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps([], indent=4))

    # Read and update the existing data
    async with aiofiles.open(file_path, 'r') as f:
        try:
            existing_data = json.loads(await f.read())
        except json.JSONDecodeError:
            existing_data = []  # In case of empty or invalid JSON

    existing_data.extend(new_data)  # Efficiently append new data

    # Write the updated data back to the file
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(existing_data, indent=4))


async def process_region(region: str):
    try:
        region_file_path = os.path.join("regions", region, f'amnezia-{region}-voice-list.json')
        async with aiofiles.open(region_file_path, 'r') as f:
            return json.loads(await f.read())
    except Exception as e:
        print(f"Error processing region {region}: {e}")
        return []  # Return empty list on failure


async def main():
    regions = os.listdir("regions")
    data = []

    # Process regions concurrently
    tasks = [process_region(region) for region in regions]
    region_data = await asyncio.gather(*tasks)

    for row in region_data:
        if row:
            data.extend(row)

    # Write to text files
    ip_list = "\n".join([voice["ip"] for voice in data])
    domain_list = "\n".join([voice["hostname"] for voice in data])

    async with aiofiles.open('voice-ip-list.txt', 'w') as f:
        await f.write(ip_list + "\n")

    async with aiofiles.open('voice-domain-list.txt', 'w') as f:
        await f.write(domain_list + "\n")

    # Append new data to the JSON file
    await append_to_json('amnezia-voice-list.json', data)


if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
