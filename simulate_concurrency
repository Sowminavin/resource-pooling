import requests
import threading

API_URL = "http://localhost:8000"
RESOURCE_TYPE = "GPU"
REQUESTER_ID = "team42"
NUM_THREADS = 10

def request_resource(thread_id):
    response = requests.post(
        f"{API_URL}/request",
        params={"resource_type": RESOURCE_TYPE, "requester_id": f"{REQUESTER_ID}-{thread_id}"}
    )
    print(f"[Thread-{thread_id}] {response.status_code}: {response.json()}")

def main():
    print("Adding a GPU resource...")
    requests.post(f"{API_URL}/resources", params={"resource_type": RESOURCE_TYPE})

    print("Running threads...")
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=request_resource, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
