import functools
import re

import click
import dns.rdatatype
import dns.rdtypes.ANY.MX
import dns.resolver


@functools.cache
def get_mailserver(email_address: str) -> str:
    domain = email_address.rpartition("@")[-1]

    answer = dns.resolver.resolve(domain, "MX")
    assert answer.rdtype == dns.rdatatype.RdataType.MX

    replies = answer.rrset
    assert replies is not None and len(replies) > 0

    reply = next(r for r in replies if dns.rdtypes.ANY.MX.MX)
    assert reply is not None

    name = reply.exchange.to_text().removesuffix(".")
    return name


def replace_bare_newlines(data: bytes) -> bytes:
    # use negative lookbehind regex to find and replace bare "\n"s
    return re.sub(b"(?<!\r)\n", b"\r\n", data, flags=re.MULTILINE)


class DummySocket:
    class DummyFile:
        def __init__(self, sock):
            self.sock = sock

        def readline(self, n=1024):
            return self.sock._file_readline()

        def close(self):
            pass

    def __init__(self, host, port):
        self._last_command: str | None = None
        self._send_buffer: List[str] = []

        self.connect((host, port))

    def connect(self, address):
        host, port = address
        click.secho(f"Would connect to {host}:{port} ...", fg="blue", err=True)

    def sendall(self, bytes: bytes, flags=0):
        self._last_command = bytes.decode("utf-8", "replace").splitlines()[0].strip()
        click.secho(bytes.decode("utf-8", "replace"), dim=True, err=True, nl=False)

    def close(self):
        click.secho("Closing connection.", fg="blue", err=True)

    def makefile(self, *args, **kwargs):
        return DummySocket.DummyFile(self)

    def _file_readline(self):
        if self._send_buffer:
            resp = self._send_buffer.pop()
        elif self._last_command:
            cmd = self._last_command.strip().lower().split()[0]
            resp = self._dummy_response(cmd)
        else:
            resp = "250 ok"

        return resp.encode("utf-8") + b"\r\n"

    def _dummy_response(self, cmd: str) -> str:
        if cmd == "data":
            return "354 Go ahead."
        elif cmd == "quit":
            return "221 Goodbye."
        elif cmd == "auth":
            return "235 Authentication succeeded"
        elif cmd == "ehlo":
            self._send_buffer.append("250 AUTH PLAIN LOGIN")
            self._send_buffer.append("250-SMTPUTF8")
            self._send_buffer.append("250-SIZE 14680064")
            return "250-Hello, I'm dummy. Glad to meet you."

        return "250 OK"

