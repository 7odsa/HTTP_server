import sys


def esc(s):
    """Escape for the body line: \\ \\r \\n \\t and non-printing bytes as \\xNN."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif o < 0x20 or o > 0x7E:
            out.append("\\x%02x" % o)
        else:
            out.append(ch)
    return "".join(out)


def read_headers(data):
    """Returns (cl_values, te_values, body_start), or None when the header block never ends.
    cl_values / te_values are the trimmed values of every Content-Length / Transfer-Encoding line."""
    pos = 0
    cl, te = [], []
    while True:
        end = data.find("\r\n", pos)
        if end < 0:
            return None
        line = data[pos:end]
        pos = end + 2
        if line == "":
            return cl, te, pos
        colon = line.find(":")
        if colon < 0:
            continue
        name = line[:colon].lower()
        value = line[colon + 1:].strip(" \t")
        if name == "content-length":
            cl.append(value)
        elif name == "transfer-encoding":
            te.append(value)


def decode(data):
    hdr = read_headers(data)

    if hdr is None:
        return "400 truncated"

    cl, te, pos = hdr

    if cl and te:
        return "400 both"

    if te:
        if len(te) != 1 or te[0].lower() != "chunked":
            return "400 bad-encoding"

        body_parts = []

        while True:
            end = data.find("\r\n", pos)

            if end < 0:
                return "400 truncated"

            size_line = data[pos:end]
            pos = end + 2

            size_text = size_line.split(";", 1)[0]

            if (
                not size_text
                or len(size_text) > 8
                or any(ch not in "0123456789abcdefABCDEF"
                       for ch in size_text)
            ):
                return "400 bad-chunk"

            size = int(size_text, 16)

            if size == 0:
                while True:
                    end = data.find("\r\n", pos)

                    if end < 0:
                        return "400 truncated"

                    trailer = data[pos:end]
                    pos = end + 2

                    if trailer == "":
                        body = "".join(body_parts)
                        rest = len(data) - pos

                        return (
                            f'framing: chunked\n'
                            f'body: "{esc(body)}"\n'
                            f'rest: {rest}'
                        )

            if len(data) - pos < size:
                return "400 truncated"

            chunk = data[pos:pos + size]
            pos += size

            body_parts.append(chunk)

            if data[pos:pos + 2] != "\r\n":
                if len(data) - pos < 2:
                    return "400 truncated"
                return "400 bad-chunk"

            pos += 2

    if cl:
        if not all(value.isdigit() for value in cl):
            return "400 bad-length"

        if len(set(cl)) != 1:
            return "400 bad-length"

        length = int(cl[0])
        available = len(data) - pos

        if length > available:
            return "400 truncated"

        body = data[pos:pos + length]
        rest = len(data) - (pos + length)

        return (
            f'framing: content-length\n'
            f'body: "{esc(body)}"\n'
            f'rest: {rest}'
        )

    return f'framing: none\nbody: ""\nrest: {len(data) - pos}'
   

