import inspect
import os


def create_context_key():
    stack = inspect.stack()[2:]
    frames = []
    for frame_info in stack:
        lineno = frame_info.lineno
        file_name = os.path.basename(frame_info.filename)
        frames.append(f"{file_name}:{lineno}")

    key = "|".join(frames)
    return key
