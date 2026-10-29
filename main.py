import sys

REASONS = {
    101: "Switching Protocols", 200: "OK", 201: "Created", 204: "No Content",
    206: "Partial Content", 301: "Moved Permanently", 302: "Found", 304: "Not Modified",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
    405: "Method Not Allowed", 408: "Request Timeout", 411: "Length Required",
    412: "Precondition Failed", 413: "Content Too Large", 414: "URI Too Long",
    415: "Unsupported Media Type", 416: "Range Not Satisfiable", 426: "Upgrade Required",
    431: "Request Header Fields Too Large", 500: "Internal Server Error",
    501: "Not Implemented", 503: "Service Unavailable", 505: "HTTP Version Not Supported",
}


def parse_spec(data):
    """data is the input as a str, one char per byte.
    Returns (method, status, header_lines, body)."""
    nl = data.find("\n")
    first = data if nl < 0 else data[:nl]
    rest = "" if nl < 0 else data[nl + 1:]
    method, status = first.split(" ")
    headers = []
    while True:
        nl = rest.find("\n")
        if nl < 0:
            line, rest = rest, ""
        else:
            line, rest = rest[:nl], rest[nl + 1:]
        if line == "":
            break
        headers.append(line)
    return method, int(status), headers, rest


def render(method, status, headers, body):
    """Return the exact wire bytes, as a str with one char per byte."""

    # 1. Remove existing Content-Length headers (case-insensitive)
    filtered_headers = []

    for header in headers:
        name = header.split(":", 1)[0].strip()

        if name.lower() != "content-length":
            filtered_headers.append(header)

    # 2. Determine whether this status code forbids a response body
    no_body_status = (
        100 <= status < 200
        or status == 204
        or status == 304
    )

    if no_body_status:
        body = ""

    # 3. Add the correct Content-Length when permitted
    if not no_body_status:
        filtered_headers.append(f"Content-Length: {len(body)}")

    # 4. Build the status line and headers using CRLF
    reason = REASONS.get(status, "Unknown")
    status_line = f"HTTP/1.1 {status} {reason}"

    response = "\r\n".join([status_line] + filtered_headers)
    response += "\r\n\r\n"

    # 5. HEAD responses include headers but omit the body
    if method != "HEAD":
        response += body

    return response


def main():
    # Read bytes, not text. latin-1 maps one byte to one char, so len() counts bytes.
    data = sys.stdin.buffer.read().decode("latin-1")
    method, status, headers, body = parse_spec(data)
    sys.stdout.buffer.write(render(method, status, headers, body).encode("latin-1"))


main()
