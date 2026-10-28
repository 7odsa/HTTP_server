import sys
from judge_http_req import readAndManipulateHttpReq


TOKEN = set("!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")



import sys

TOKEN = set("!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def parse_headers(data):
    pos = 0
    names = []
    values = {}

    while True:
        end = data.find("\r\n", pos)
        if end < 0:
            return "400 incomplete"

        line = data[pos:end]
        pos = end + 2

        if line == "":
            break

        if "\r" in line or "\n" in line:
            return "400 line-ending"

        if line.startswith((" ", "\t")):
            return "400 fold"

        if ":" not in line:
            return "400 no-colon"

        name, value = line.split(":", 1)

        if not name or any(char not in TOKEN for char in name):
            return "400 bad-name"

        name = name.lower()
        value = value.strip(" \t")

        if name not in values:
            names.append(name)
            values[name] = []

        values[name].append(value)

    if len(values.get("host", [])) != 1:
        return "400 host"

    result = []
    for name in names:
        value = ", ".join(values[name])
        if value:
            result.append(f"{name}: {value}")
        else:
            result.append(f"{name}:")

    return "\n".join(result)





def main():
    # Read bytes, not text: text mode would rewrite \r\n as \n before you ever see it.
    data = sys.stdin.buffer.read().decode("latin-1")
    sys.stdout.buffer.write((parse_headers(data) + "\n").encode("latin-1"))

main()
