import json
import asyncio
import aiofiles
from datetime import datetime
import os

async def process_region(region: str):
    try:
        region_file_path = os.path.join("regions", region, f'amnezia-{region}-voice-list.json')
        async with aiofiles.open(region_file_path, 'r') as f:
            return json.loads(await f.read())
    except Exception as e:
        print(f"Error processing region {region}: {e}")
        return []  # Return empty list on failure
    
async def process_base():
    try:
        region_file_path = 'amnezia-base-list.json'
        async with aiofiles.open(region_file_path, 'r') as f:
            return json.loads(await f.read())
    except Exception as e:
        print(f"Error processing base domains: {e}")
        return []  # Return empty list on failure


async def main():
    regions = os.listdir("regions")
    data = []

    # Process regions concurrently
    tasks = [process_region(region) for region in regions]
    region_data = await asyncio.gather(*tasks)
    base_data = await process_base()

    for row in region_data:
        if row:
            data.extend(row)

    # Write to text files
    ip_list = "\n".join([voice["ip"] for voice in data])
    domain_list = "\n".join([voice["hostname"] for voice in data])

    async with aiofiles.open(os.path.join("data", 'voice-ip-list.txt'), 'w') as f:
        await f.write(ip_list + "\n")

    async with aiofiles.open(os.path.join("data", 'voice-domain-list.txt'), 'w') as f:
        await f.write(domain_list + "\n")

    # Append new data to the JSON file
    os.makedirs("amnezia", exist_ok=True)
        
    async with aiofiles.open(os.path.join("amnezia", 'amnezia-voice-list.json'), 'w') as f:
        await f.write(json.dumps(data, indent=4))
    
    async with aiofiles.open(os.path.join("amnezia", 'amnezia-everything-list.json'), 'w') as f:
        await f.write(json.dumps(base_data + data, indent=4))


if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
