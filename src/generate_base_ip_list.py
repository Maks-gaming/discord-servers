import json
import os
import sys
import asyncio
import aiofiles
import dns.asyncresolver
from datetime import datetime

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

async def process_domain(domain, results):
    domain, a_records = await get_a_records(domain)
    if a_records and "Error" not in a_records:
        results.append({"hostname": domain, "ip": a_records.split()[0]})
        print(f"\r{domain} -> {a_records}", end="")

async def main():
    tasks = []
    results = []
    max_concurrent_tasks = 1000
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def limited_task(domain):
        async with semaphore:
            await process_domain(domain, results)

    # Read the list of domains from the file
    try:
        async with aiofiles.open(os.path.join("data", 'base-domain-list.txt'), 'r') as f:
            domains = await f.readlines()
    except FileNotFoundError:
        print("Domain list file not found.")
        sys.exit(1)

    domains = [domain.strip() for domain in domains]  # Clean up line breaks

    for domain in domains:
        tasks.append(limited_task(domain))

    await asyncio.gather(*tasks)

    if len(results) == 0:
        print("\nNo results found.")
        return

    # Display results instead of saving them
    async with aiofiles.open(os.path.join("data", 'base-ip-list.txt'), 'w') as f:
        await f.write("\n".join(map(lambda a: a["ip"], results)) + "\n")
    
    os.makedirs("amnezia", exist_ok=True)
    async with aiofiles.open(os.path.join("amnezia", 'amnezia-base-list.json'), 'w') as f:
        await f.write(json.dumps(results, indent=4))

if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
