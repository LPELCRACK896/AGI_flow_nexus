import bcrypt

def hash_password(password: str, encode: str = "utf-8") -> str:
    hashed_password = bcrypt.hashpw(password.encode(encode), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def check_password(plain_password: str, hashed_password: str, encode: str = "utf-8") -> bool:
    return bcrypt.checkpw(plain_password.encode(encode), hashed_password.encode(encode))