import email
import email.policy
import smtplib
import sys
import typing
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr

import click

from mailhacker.util import get_mailserver, replace_bare_newlines, DummySocket


@click.command()
@click.option(
    "-e", "--ehlo", help="(Optional) server name to be sent in an EHLO command."
)
@click.option(
    "-s",
    "--server",
    help="(Optional) server name to connect to (default: infer from receiver's address).",
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=25,
    help="TCP port to use for the SMTP connection.",
)
@click.option(
    "--tls/--no-tls", is_flag=True, default=True, help="Use/don't use SSL/TLS."
)
@click.option("-f", "--from", "from_addr", help='"MAIL FROM" address.')
@click.option("-t", "--to", "to_addr", multiple=True, help='"RCPT TO" address.')
@click.option("-u", "--username", help="(Optional) username for authentication")
@click.option("-p", "--password", help="(Optional) password for authentication")
@click.option(
    "-n",
    "--dry",
    is_flag=True,
    help="Do not actually send the message.",
)
@click.option("-v", "--verbose", count=True)
@click.argument("message", type=click.File("rb"), default="-")
def send(
    ehlo: str | None,
    server: str | None,
    port: int,
    tls: bool,
    from_addr: str | None,
    to_addr: tuple[str, ...],
    username: str,
    password: str,
    dry: bool,
    verbose: int,
    message: typing.BinaryIO,
):
    """Send an email message using SMTP.

    If not explicitly specified, the destination SMTP server will be guessed
    based on the first recipient address.
    Newlines will be automatically fixed to '\r\n'.
    """

    data = message.read()

    # replace "\n" with "\r\n" because SMTP requires mails to be formatted that way
    data = replace_bare_newlines(data)

    if not from_addr or not to_addr:
        # will attempt to parse the message
        msg = email.message_from_bytes(data, policy=email.policy.default)  # type: ignore
        assert isinstance(msg, EmailMessage)

        if not from_addr:
            _, from_addr = parseaddr(msg["From"])
            if not from_addr:
                raise ValueError('Cannot infer "mail FROM" address from the mail data.')

        if not to_addr:
            rcpts = msg.get_all("To")
            assert rcpts is not None
            to_addr = tuple(t[1] for t in getaddresses(rcpts))

    if not server:
        # infering the mail server from the FIRST to_addr only
        server = get_mailserver(to_addr[0])

    with smtplib.SMTP() as smtp:
        if verbose:
            smtp.set_debuglevel(1)

        if dry:
            smtp.sock = DummySocket(server, port)  # type: ignore
        else:
            smtp.connect(server, port)

            if tls:
                smtp.starttls()

        if ehlo:
            smtp.ehlo(ehlo)

        if username:
            smtp.login(username, password)

        smtp.sendmail(from_addr, to_addr, data)


if __name__ == "__main__":
    send()
