import sys


def judge(line):
    """Decide what to print for ONE line (already cut at CRLF, CRLF removed).
    Return "OK <method> <target> <version>", "400", "501" or "505"."""
    # TODO 1: a CR or LF left inside the line means it was not terminated by CRLF -> "400".
    # TODO 2: exactly three non-empty fields separated by single spaces -> else "400".
    # TODO 3: method only A-Z; target starts with "/" (or is "*" for OPTIONS) and every byte
    #         is 0x21..0x7e; version is HTTP/<digit>.<digit>  -> any failure is "400".
    # TODO 4: method not in GET HEAD POST PUT DELETE OPTIONS PATCH -> "501".
    # TODO 5: version not HTTP/1.0 or HTTP/1.1 -> "505".
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
