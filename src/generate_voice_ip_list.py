import sys
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
import threading


if not len(sys.argv) > 1:
    print("Please provide a region as an argument.")
    sys.exit(1)
    
region = sys.argv[1]

print(f"Generating ip list for {region}...")

def get_a_records(domain):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        answer = resolver.resolve(domain, 'A')
        return domain, " ".join([rdata.to_text() for rdata in answer])
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        return domain, f"Error: {str(e)}"
    except Exception as e:
        return domain, f"Error: {str(e)}"

output_lock = threading.Lock()  # For synchronizing output

def process_domain(region, id):
    domain = f"{region}{id}.discord.gg"
    domain, a_records = get_a_records(domain)
    
    with output_lock:  # Locking output for each thread
        if a_records and "Error" not in a_records:
            print(f"\r{domain} -> {a_records}")
            
            # Write the result immediately to the file
            with open('ip_list_new.txt', 'a') as f:
                f.write(f"{a_records}\n")

with ThreadPoolExecutor(max_workers=100) as executor:
    for id in range(15001):  # Up to 15000 inclusive
        executor.submit(process_domain, region, id)
