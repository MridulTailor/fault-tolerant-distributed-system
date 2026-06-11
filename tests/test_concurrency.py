import urllib.request
import urllib.error
import json
import concurrent.futures

SCHEDULER_1_URL = "http://localhost:8001/sessions"
SCHEDULER_2_URL = "http://localhost:8003/sessions"

def make_request(url):
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return 500, None

def test_split_brain():
    print("--- Testing Split-Brain Concurrency ---")
    print("Sending 40 concurrent requests simultaneously to both schedulers.")
    
    # I send 20 to scheduler-1 and 20 to scheduler-2 at the same time
    urls = [SCHEDULER_1_URL] * 20 + [SCHEDULER_2_URL] * 20
    
    success_count = 0
    rejected_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(make_request, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            status, data = future.result()
            if status == 200:
                success_count += 1
            elif status == 503:
                rejected_count += 1
                
    print(f"Total successful allocations: {success_count} (Expected <= 30)")
    print(f"Total rejected allocations (503): {rejected_count}")
    
    if success_count <= 30 and (success_count + rejected_count == 40):
        print("✅ Split-brain concurrency test passed! No over-allocation occurred.")
    else:
        print("❌ Split-brain concurrency test failed!")

if __name__ == "__main__":
    test_split_brain()
