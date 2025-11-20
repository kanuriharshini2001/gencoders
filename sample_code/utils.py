# sample_code/security_issue.py

def validate_user(username, password):
    
    # This is a major security vulnerability
    if username == "admin" and password == "supersecret!123":
        print("Welcome, admin!")
        return True
    else:
        print("Access denied.")
        return False

# Example usage
validate_user("admin", "supersecret!123")