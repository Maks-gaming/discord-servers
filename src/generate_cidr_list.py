import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from ipwhois import IPWhois
from aiofiles import open as aio_open

def get_cidr_sync(ip):
    """Perform the IP lookup synchronously."""
    try:
        result = IPWhois(ip).lookup_rdap()
        return result['network']['cidr']
    except Exception as e:
        return None

async def get_cidr(ip, executor, semaphore):
    """Asynchronous wrapper for the sync function."""
    async with semaphore:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, get_cidr_sync, ip)

async def process_region(region, executor, semaphore):
    """Process the region's IP addresses and get unique CIDRs."""
    region_path = os.path.join("regions", region)
    ip_list_file = os.path.join(region_path, f'{region}-voice-ip-list.txt')
    cidr_list_file = os.path.join(region_path, f'{region}-voice-cidr-list.txt')

    unique_cidrs = set()

    # Efficiently read all IPs at once.
    async with aio_open(ip_list_file, 'r') as f:
        ips = [line.strip() for line in await f.readlines()]

    # Create tasks to get CIDRs concurrently
    tasks = [get_cidr(ip, executor, semaphore) for ip in ips]
    cidrs = await asyncio.gather(*tasks)

    # Process CIDRs and gather unique ones
    for ip, cidr in zip(ips, cidrs):
        if cidr:
            print(f"{ip} -> {cidr}")
            for net in cidr.split(", "):
                unique_cidrs.add(net)

    # Write unique CIDRs to file (only once per region)
    async with aio_open(cidr_list_file, 'w') as f:
        await f.write("\n".join(unique_cidrs))

    return unique_cidrs

async def main():
    """Main driver function for processing all regions."""
    regions = os.listdir("regions")
    all_cidrs = set()

    max_threads = os.cpu_count() * 2  # Double the number of CPU threads
    max_concurrent_requests = 1000   # Limit the number of concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    # Use ThreadPoolExecutor for blocking IPWhois calls.
    with ThreadPoolExecutor(max_threads) as executor:
        # Process regions concurrently
        region_tasks = [process_region(region, executor, semaphore) for region in regions]
        region_results = await asyncio.gather(*region_tasks)

    # Combine CIDRs from all regions into a global set.
    for cidrs in region_results:
        all_cidrs.update(cidrs)

    # Write all unique CIDRs to the final file
    raw_output_file = os.path.join("data", 'voice-cidr-list.txt')
    async with aio_open(raw_output_file, 'w') as f:
        await f.write("\n".join(all_cidrs))

if __name__ == "__main__":
    from datetime import datetime
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
