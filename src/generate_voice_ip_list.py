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

# Increase concurrency limit and handle DNS query timeouts
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

# Async function to handle domain processing with semaphore for concurrency control
async def process_domain(region, id, results, semaphore):
    domain = f"{region}{id}.discord.gg"
    async with semaphore:
        domain, a_records = await get_a_records(domain)
        if a_records and "Error" not in a_records:
            results.append({"hostname": domain, "ip": a_records})
            print(f"\r{domain} -> {a_records}", end="")

# Main function to launch all tasks concurrently
async def main():
    tasks = []
    results = []
    max_concurrent_tasks = 1000  # Experiment with this value for optimal performance
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    for id in range(15001):  # Up to 15000 inclusive
        tasks.append(process_domain(region, id, results, semaphore))

    await asyncio.gather(*tasks)

    region_dir = os.path.join("regions", region)

    if len(results) == 0:
        print("\nNo results found.")
        if os.path.exists(region_dir):
            shutil.rmtree(region_dir)
        return

    # Create directory structure
    os.makedirs(region_dir, exist_ok=True)

    # Writing all results to files at once to minimize I/O operations
    ip_list = "\n".join(map(lambda a: a["ip"], results)) + "\n"
    domain_list = "\n".join(map(lambda a: a["hostname"], results)) + "\n"
    json_list = json.dumps(results, indent=4)

    # Perform async writes in batch
    async with aiofiles.open(os.path.join(region_dir, f'{region}-voice-ip-list.txt'), 'w') as f:
        await f.write(ip_list)

    async with aiofiles.open(os.path.join(region_dir, f'{region}-voice-domain-list.txt'), 'w') as f:
        await f.write(domain_list)

    async with aiofiles.open(os.path.join(region_dir, f'amnezia-{region}-voice-list.json'), 'w') as f:
        await f.write(json_list)

if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
