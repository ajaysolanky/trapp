import hashlib


def hash_file_from_fp(file_path):
    """Generate SHA-256 hash for a file."""
    with open(file_path, "rb") as f:
        return hash_file_from_file_obj(f)


def hash_file_from_file_obj(file_obj):
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file_obj.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
