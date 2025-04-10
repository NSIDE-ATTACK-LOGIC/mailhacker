import datetime
import typing
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid, parseaddr

import click


@click.command()
@click.option(
    "-f",
    "--from",
    "from_addr",
    required=True,
    help='The email address to be specified in the "From" header.',
)
@click.option(
    "-t",
    "--to",
    "to_addr",
    required=True,
    multiple=True,
    help='One or more email addresses for the "To" header.',
)
@click.option("-s", "--subject", help="The message's subject.")
@click.option(
    "-H",
    "--header",
    multiple=True,
    help='(Optional) custom headers, provided as "Name: Value" pairs.',
)
@click.option(
    "--html",
    is_flag=True,
    help="Whether to compose the mail as HTML (default: plain text).",
)
@click.argument("body", type=click.File("r"), default="-")
def compose(
    from_addr: str,
    to_addr: tuple[str, ...],
    subject: str | None,
    header: tuple[str, ...],
    html: bool,
    body: typing.TextIO,
):
    """Compose a new email message.

    The message's body must be passed via stdin.
    """

    if body.isatty():
        click.echo("Enter mail body (terminate with Ctrl+D): ", err=True)

    body_text = body.read()

    msg = EmailMessage()
    msg.set_payload(body_text)
    msg.set_charset("utf-8")

    if html:
        msg.set_type("text/html")

    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addr)

    msg["Date"] = format_datetime(datetime.datetime.now())

    message_id_domain = parseaddr(from_addr)[1].rpartition("@")[-1]
    msg["Message-ID"] = make_msgid(idstring="mailhacker", domain=message_id_domain)

    if subject:
        msg["Subject"] = subject

    for item in header:
        key, _, value = item.partition(": ")
        msg[key] = value

    print(msg.as_string(), end="")


if __name__ == "__main__":
    compose()
