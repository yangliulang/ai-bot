import bcrypt

_BCRYPT_ROUNDS = 12


def hash_password(plain: str) -> str:
    """生成 bcrypt 哈希（字符串存储）。"""
    data = plain.encode("utf-8")
    if len(data) > 72:
        raise ValueError("password exceeds bcrypt 72-byte limit")
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(data, salt).decode("ascii")


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False
