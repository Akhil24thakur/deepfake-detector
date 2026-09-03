from PIL import Image
import io

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_DIMENSION = 2048


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_and_load(file_bytes: bytes, filename: str):
    if len(file_bytes) > MAX_SIZE_BYTES:
        return None, "File too large. Max 10MB allowed."

    if not allowed_file(filename):
        return None, "Invalid file type. Use JPG, PNG, WEBP or GIF."

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        image = Image.open(io.BytesIO(file_bytes))
        return image, None
    except Exception:
        return None, "Could not read image. File may be corrupted."


def get_image_info(file_bytes: bytes, filename: str) -> dict:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        width, height = image.size
        size_kb = round(len(file_bytes) / 1024, 1)
        size_str = (
            f"{size_kb} KB"
            if size_kb < 1024
            else f"{round(size_kb / 1024, 1)} MB"
        )

        return {
            "filename": filename,
            "dimensions": f"{width} x {height}",
            "size": size_str,
            "format": image.format or filename.rsplit(".", 1)[-1].upper(),
        }
    except Exception:
        return {
            "filename": filename,
            "dimensions": "Unknown",
            "size": "Unknown",
            "format": "Unknown",
        }
