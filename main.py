import sys

supported_methods = {
    "GET", "HEAD", "POST", "PUT",
    "DELETE", "OPTIONS", "PATCH"
}


def judge(line):
    if "\r" in line or "\n" in line:
        return "400"

    parts = line.split(" ")

    if len(parts) != 3 or any(part == "" for part in parts):
        return "400"

    method, target, version = parts

    if any(c < "A" or c > "Z" for c in method):
        return "400"

    if target != "*" and not target.startswith("/"):
        return "400"

    if target == "*" and method != "OPTIONS":
        return "400"

    if any(ord(c) < 0x21 or ord(c) > 0x7e for c in target):
        return "400"

    if (
        len(version) != 8
        or not version.startswith("HTTP/")
        or not ("0" <= version[5] <= "9")
        or version[6] != "."
        or not ("0" <= version[7] <= "9")
    ):
        return "400"

    supported_methods = {
        "GET", "HEAD", "POST", "PUT",
        "DELETE", "OPTIONS", "PATCH"
    }

    if method not in supported_methods:
        return "501"

    if version not in ("HTTP/1.0", "HTTP/1.1"):
        return "505"

    return "OK " + line

def main():
    # Read bytes, not text: text mode would rewrite \r\n as \n before you ever see it.
    data = sys.stdin.buffer.read().decode("latin-1")
    pieces = data.split("\r\n")
    tail = pieces.pop()  # whatever follows the last CRLF
    out = [judge(p) for p in pieces]
    if tail != "":
        out.append("400")  # an unterminated fragment is a 400
    for o in out:
        sys.stdout.write(o + "\n")


main()
