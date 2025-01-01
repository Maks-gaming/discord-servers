import datetime
import sys
import asyncio
import aiofiles
import dns.asyncresolver

if len(sys.argv) <= 1:
    print("Please provide a region as an argument.")
    sys.exit(1)

region = sys.argv[1]
print(f"Generating IP list for {region}...")

resolver = dns.asyncresolver.Resolver()
resolver.nameservers = ['8.8.8.8', '8.8.4.4']

async def get_a_records(domain):
    try:
        answer = await resolver.resolve(domain, 'A')
        return domain, " ".join([rdata.to_text() for rdata in answer])
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        return domain, f"Error: {str(e)}"
    except Exception as e:
        return domain, f"Error: {str(e)}"

async def process_domain(region, id, results):
    domain = f"{region}{id}.discord.gg"
    domain, a_records = await get_a_records(domain)
    if a_records and "Error" not in a_records:
        results.append(a_records)
        print(f"\r{domain} -> {a_records}", end="")

async def main():
    tasks = []
    results = []
    max_concurrent_tasks = 1000 # Depends on your system
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def limited_task(region, id):
        async with semaphore:
            await process_domain(region, id, results)

    for id in range(15001):  # Up to 15000 inclusive
        tasks.append(limited_task(region, id))

    await asyncio.gather(*tasks)

    # Write all results to the file at once
    async with aiofiles.open('ip_list_new.txt', 'a') as f:
        await f.write("\n".join(results) + "\n")

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    asyncio.run(main())
    end_time = datetime.datetime.now()
    print(f"\nFinished! Time taken: {end_time - start_time}")
