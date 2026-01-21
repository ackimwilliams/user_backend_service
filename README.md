# User Service Implementation

---

This is a high-availability backend service built with modern concurrency, and testing practices:
- Thread-safe in-memory CRUD service
- Dependency-injected datastore abstraction
- HTTP API via FastAPI
- Structured JSON logging
- Unit tests
- Docker containerization


## Setup and run instructions

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export APP_ENV=dev
export LOG_LEVEL=INFO
export LOG_JSON=true
export PORT=8000

python -m app.main

# or containerized

docker run --rm -p 8000:8000 \
  -e APP_ENV=dev \
  -e PORT=8000 \
  -e LOG_JSON=true \
  -e LOG_LEVEL=INFO \
  user-service:latest
```

## Testing

```bash
python -m unittest -v
```

<img width="618" height="116" alt="image" src="https://github.com/user-attachments/assets/e4e5b217-8c73-48dd-95c1-6f6e05c89f5b" />

## Example usage

```bash

# create
curl -s -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Joe","email":"joe@example.com"}'

# get
curl -s http://localhost:8000/users/1

# update email
curl -s -X PUT http://localhost:8000/users/1/email \
  -H "Content-Type: application/json" \
  -d '{"email":"joe_new_email@example.com"}'

# delete
curl -i -X DELETE http://localhost:8000/users/1

# not found
curl -i http://localhost:8000/users/-1

# bad request
curl -i -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"","email":"bad_email_address"}'

```

## Sample commands 
<img width="616" height="371" alt="image" src="https://github.com/user-attachments/assets/fe91c89e-5455-4672-95cf-1b0925eec8dc" />


## Sample logs
<img width="677" height="289" alt="image" src="https://github.com/user-attachments/assets/1364f936-9e7b-4329-9210-c75aeb02fda2" />

