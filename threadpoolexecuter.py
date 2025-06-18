import requests
import concurrent.futures
import time

API_URL = "http://localhost:8000"
RESOURCE_TYPE = "GPU"
REQUESTER_ID = "team42"
NUM_THREADS = 10

def request_resource(thread_id):
    try:
        response = requests.post(
            f"{API_URL}/request",
            params={"resource_type": RESOURCE_TYPE, "requester_id": f"{REQUESTER_ID}-{thread_id}"}
        )
        result = response.json()
        return (thread_id, response.status_code, result)
    except Exception as e:
        return (thread_id, "ERROR", str(e))

def main():
    # Step 1: Add a single resource
    print("Adding one resource...")
    add_response = requests.post(f"{API_URL}/resources", params={"resource_type": RESOURCE_TYPE})
    print(f"Resource created: {add_response.json()}")

    # Step 2: Start concurrent requests
    print(f"\nRunning {NUM_THREADS} concurrent requests...\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(request_resource, i) for i in range(NUM_THREADS)]

        success = 0
        failure = 0

        for future in concurrent.futures.as_completed(futures):
            thread_id, status, result = future.result()
            print(f"[Thread-{thread_id}] {status}: {result}")
            if status == 200:
                success += 1
            else:
                failure += 1

    print(f"\n✅ Done. Success: {success}, Failures: {failure}")

if __name__ == "__main__":
    main()
