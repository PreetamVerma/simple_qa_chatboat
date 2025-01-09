import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict
import jwt
import time
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Secret and Expiry
SECRET_KEY = "your_secret_key"  # Replace with a secure key in production
TOKEN_EXPIRY = 3600  # 1 hour



# Mock database
user_db: Dict[str, Dict] = {
    "alice@email.com": {"name": "Alice", "access": ["Company_A"]},
    "bob@email.com": {"name": "Bob", "access": ["Company_B", "Company_C"]},
    "charlie@email.com": {"name": "Charlie", "access": ["Company_D", "Company_E"]}
}



# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr


class AuthenticatedUser(BaseModel):
    email: EmailStr
    name: str
    access: list


class QueryRequest(BaseModel):
    question: str



# Generate JWT token
def create_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": time.time() + TOKEN_EXPIRY
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token




def verify_token(authorization: str = Header(...)) -> AuthenticatedUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = authorization.split("Bearer ")[1]
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded_token.get("email")
        if email not in user_db:
            raise HTTPException(status_code=401, detail="Invalid user")
        user = user_db[email]
        return AuthenticatedUser(email=email, name=user["name"], access=user["access"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    
# Function to load past queries from the file
def load_past_queries(email: str) -> str:
    file_path = f"queries_{email}.txt"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return ""



# Function to save the new query to the file
def save_query(email: str, query: str) -> None:
    file_path = f"queries_{email}.txt"
    with open(file_path, "a") as file:
        file.write(query + "\n")



# Login endpoint
@app.post("/login")
def login(request: LoginRequest):
    email = request.email
    if email not in user_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    token = create_token(email)
    return {"access_token": token, "token_type": "Bearer", "expiry":"3600"}



# Protected route
@app.get("/protected")
def protected_route(user: AuthenticatedUser = Depends(verify_token)):
    return {"message": f"Hello, {user.name}!", "access": user.access}



# Query endpoint (saving and returning past interactions)
@app.post("/query")
def handle_query(request: QueryRequest, user: AuthenticatedUser = Depends(verify_token)):
    # Load past queries from the file
    past_queries = load_past_queries(user.email)
    
    # Mock search based on access rights
    documents = {
        "Company_A": "Company A revenue in Q4 was $1.5 billion.",
        "Company_B": "Company B revenue in Q4 was $2.0 billion.",
        "Company_C": "Company C revenue in Q4 was $1.8 billion.",
        "Company_D": "Company D revenue in Q4 was $2.2 billion.",
        "Company_E": "Company E revenue in Q4 was $2.5 billion."
    }

    # Search only in user's accessible documents
    results = [text for company, text in documents.items() if company in user.access]

    if not results:
        raise HTTPException(status_code=403, detail="No access to relevant documents.")
    
    # For simplicity, concatenate all results (in real-world, you'd use an LLM or search engine)
    combined_results = " ".join(results)
    
    # Save new query to the file
    save_query(user.email, request.question)
    
    # Return past queries along with the new result
    return {"past_queries": past_queries, "new_query": request.question, "response": combined_results}


# Get user profile
@app.get("/users/me")
def get_user_profile(user: AuthenticatedUser = Depends(verify_token)):
    return {"email": user.email, "name": user.name, "access": user.access}



# Logout endpoint (optional)
@app.post("/logout")
def logout():
    return {"message": "User logged out successfully. Clear token on client side."}


if __name__ == '__main__':
    app.sta(host='0.0.0.0', port=8080, debug=True, reload=True)
