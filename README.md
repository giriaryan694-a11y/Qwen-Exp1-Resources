# Qwen Exp1 Resources

Resources and scripts used during **Qwen Experiment 1**.

> [!WARNING]
>
> ## ⚠️ Security Warning
>
> These scripts are **experimental remote-access utilities** and are **not production-ready**.
>
> `webshell.py` provides an HTTP interface capable of executing system commands, while `file_receiver.py` accepts file uploads. Exposing either service to an untrusted network can allow unauthorized access, command execution, or arbitrary file upload if the configuration is compromised.
>
> **Use only on machines you own or have explicit authorization to test. Keep the services bound to localhost or an isolated test environment whenever possible, use a strong unique password, and do not expose them directly to the public internet without appropriate access controls.**
>
> The examples in this repository are intended for the Qwen experiment only.

The full experiment write-up and analysis will be published separately on **AryterLog**:

**Write-up:** https://giriaryan694-a11y.github.io/AryterLog/posts/qwen-ui-limitations-vs-model-capabilities/

---

## `webshell.py`

`webshell.py` is a lightweight authenticated web shell used during the experiment to allow Qwen to interact with the experiment machine and execute commands.

### Configuration

**Password**

At line 5:

```python
AUTH_HASH = hashlib.sha256("qwen_session123".encode()).hexdigest()
```

Replace `qwen_session123` with your own password.

**Port**

At the end of the file, change:

```python
port=5000
```

to the port you want to use.

### Testing

Start the server and test it with:

```bash
curl -X POST -d "auth=qwen_session123&cmd=id" http://localhost:5000/shell
```

Replace the password and port when you change the configuration.

---

## `file_receiver.py`

`file_receiver.py` is used during the experiment to allow Qwen to upload files, archives, or fixed codebases to the experiment machine.

### Configuration

**Port**

At line 12:

```python
PORT = int(os.getenv("PORT", "8000"))
```

Change `8000` to the port you want to use.

**Maximum upload size**

At line 13:

```python
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "2048"))
```

The value is specified in **MB**.

The default value is:

```text
2048 MB ≈ 2 GB
```

For example, to allow 500 MB:

```python
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "500"))
```

**Password**

At line 10:

```python
PASSWORD = "qwen_session123"
```

Replace `qwen_session123` with your own password.

### Uploading a file

A file can be uploaded using:

```bash
curl -T /path/to/file.zip \
  -H 'X-Password: qwen_session123' \
  http://127.0.0.1:8000/upload/file.zip
```

Qwen can perform the equivalent operation when provided with an appropriate code-interpreter/tool environment.

---

## Sharing Files With Qwen

For experiments where Qwen needs to retrieve a file from the experiment machine, Python's built-in HTTP server can be used:

```bash
python -m http.server 8000
```

This exposes the current directory over HTTP.

To make the HTTP server reachable from outside the machine, a port-forwarding/tunneling solution such as **Cloudflare Tunnel (`cloudflared`)** can be used.

> **Important:** A tunnel can make a locally running service reachable from the internet. Only expose services that are intentionally configured for external access, and shut down the tunnel/server when the experiment is finished.

---

## Experiment Scope

These scripts are **experiment resources**, not the experiment's main write-up.

The detailed methodology, observations, results, and analysis will be documented separately on AryterLog.

**AryterLog write-up:** https://giriaryan694-a11y.github.io/AryterLog/posts/qwen-ui-limitations-vs-model-capabilities/
