#!/usr/bin/env python3
import hmac
import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

PASSWORD = "qwen_session123"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "2048"))

UPLOAD_DIR = Path(__file__).resolve().parent / "received_files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def authorized():
    pw = request.headers.get("X-Password") or request.args.get("password")

    if not pw and request.mimetype == "multipart/form-data":
        pw = request.form.get("password")

    if not pw:
        return False

    return hmac.compare_digest(pw.encode("utf-8"), PASSWORD.encode("utf-8"))


def make_dest(filename):
    safe = secure_filename(filename) or "upload.bin"

    while True:
        file_id = secrets.token_hex(8)
        dest = UPLOAD_DIR / f"{file_id}_{safe}"
        if not dest.exists():
            return dest, safe


def save_stream(dest):
    limit = app.config["MAX_CONTENT_LENGTH"]
    written = 0

    try:
        with dest.open("wb") as out:
            while True:
                chunk = request.stream.read(1024 * 1024)
                if not chunk:
                    break

                written += len(chunk)
                if written > limit:
                    raise ValueError("too_large")

                out.write(chunk)
    except Exception:
        dest.unlink(missing_ok=True)
        raise


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": f"payload too large; max {MAX_UPLOAD_MB} MB"}), 413


@app.get("/health")
def health():
    return jsonify({"status": "receiver"})


@app.post("/upload")
def upload_multipart():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "missing file field"}), 400

    f = request.files["file"]

    if not f.filename:
        return jsonify({"error": "empty filename"}), 400

    dest, safe = make_dest(f.filename)
    f.save(dest)

    return jsonify({
        "received": safe,
        "stored_as": dest.name,
        "size": dest.stat().st_size
    }), 201


@app.put("/upload")
@app.put("/upload/<path:filename>")
@app.post("/upload/<path:filename>")
def upload_raw(filename=None):
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    if filename is None:
        filename = (
            request.headers.get("X-Filename")
            or request.args.get("filename")
            or "upload.bin"
        )

    if (
        request.content_length is not None
        and request.content_length > app.config["MAX_CONTENT_LENGTH"]
    ):
        return jsonify({"error": f"payload too large; max {MAX_UPLOAD_MB} MB"}), 413

    if (
        request.content_length is None
        and request.headers.get("Transfer-Encoding", "").lower() != "chunked"
    ):
        return jsonify({"error": "Content-Length or chunked Transfer-Encoding required"}), 411

    dest, safe = make_dest(filename)

    try:
        save_stream(dest)
    except ValueError as e:
        if str(e) == "too_large":
            return jsonify({"error": f"payload too large; max {MAX_UPLOAD_MB} MB"}), 413
        return jsonify({"error": "upload failed"}), 500
    except Exception:
        return jsonify({"error": "upload failed"}), 500

    return jsonify({
        "received": safe,
        "stored_as": dest.name,
        "size": dest.stat().st_size
    }), 201


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
