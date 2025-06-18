This is an internal API for resource pooling. It supports:
- Adding resources
- Allocating resources (thread-safe)
- Releasing resources
- Listing available and all resources

## 🚀 Features
- Built with FastAPI
- Thread-safe resource allocation using `threading.Lock`
- Simulates concurrent access with Python threads

## 📦 Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- Requests (for test script)

## 🛠 Install & Run

```bash
git clone https://github.com/your-username/resource-pool-api.git
cd resource-pool-api
pip install -r requirements.txt
uvicorn app.main:app --reload
