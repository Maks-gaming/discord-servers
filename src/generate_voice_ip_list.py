import json
import sys
import asyncio
import aiofiles
import dns.asyncresolver
from datetime import datetime
import os
import shutil


if len(sys.argv) <= 1:
    print("Please provide a region as an argument.")
    sys.exit(1)

region = sys.argv[1]
print(f"Generating IP list for {region}...")

resolver = dns.asyncresolver.Resolver()
resolver.nameservers = ['8.8.8.8', '8.8.4.4']

async def get_a_records(domain, retries=3, delay=1):
    for attempt in range(retries):
        try:
            answer = await resolver.resolve(domain, 'A')
            return domain, " ".join([rdata.to_text() for rdata in answer])
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
            return domain, f"Error: {str(e)}"
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                return domain, f"Error: {str(e)}"


async def process_domain(region, id, results):
    domain = f"{region}{id}.discord.gg"
    domain, a_records = await get_a_records(domain)
    if a_records and "Error" not in a_records:
        results.append({"hostname": domain, "ip": a_records})
        print(f"\r{domain} -> {a_records}", end="")
        

async def append_to_json(file_path, new_data):
    # Check if file exists
    if not os.path.exists(file_path):
        # If file doesn't exist, create it and initialize with an empty list (or other default structure)
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps([], indent=4))

    # Read existing data
    async with aiofiles.open(file_path, 'r') as f:
        try:
            existing_data = json.loads(await f.read())
        except json.JSONDecodeError:
            existing_data = []  # In case the file is empty or doesn't contain valid JSON

    # Append new data
    for row in new_data:
        existing_data.append(row)

    # Write updated data back to the file
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(existing_data, indent=4))

async def main():
    tasks = []
    results = []
    max_concurrent_tasks = 500
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def limited_task(region, id):
        async with semaphore:
            await process_domain(region, id, results)

    for id in range(15001):  # Up to 15000 inclusive
        tasks.append(limited_task(region, id))

    await asyncio.gather(*tasks)

    region_dir = os.path.join("regions", region)

    if len(results) == 0:
        print("\nNo results found.")
        if os.path.exists(region_dir):
            shutil.rmtree(region_dir)
        return

    # Create directory structure
    os.makedirs(region_dir, exist_ok=True)

    # Write all results to files
    async with aiofiles.open(os.path.join(region_dir, f'{region}-voice-ip-list.txt'), 'w') as f:
        await f.write("\n".join(map(lambda a: a["ip"], results)) + "\n")

    async with aiofiles.open(os.path.join(region_dir, f'{region}-voice-domain-list.txt'), 'w') as f:
        await f.write("\n".join(map(lambda a: a["hostname"], results)) + "\n")
        
    async with aiofiles.open(os.path.join(region_dir, f'amnezia-{region}-voice-list.json'), 'w') as f:
        await f.write(json.dumps(results, indent=4))
        
    async with aiofiles.open('voice-ip-list.new.txt', 'a') as f:
        await f.write("\n".join(map(lambda a: a["ip"], results)) + "\n")
        
    async with aiofiles.open('voice-domain-list.new.txt', 'a') as f:
        await f.write("\n".join(map(lambda a: a["hostname"], results)) + "\n")
        
    await append_to_json('amnezia-voice-list.json', results)


if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
