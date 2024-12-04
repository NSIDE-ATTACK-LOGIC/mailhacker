import email.policy
import mimetypes
import pathlib
import typing
from email import message_from_binary_file
from email.message import EmailMessage

import click


@click.command()
@click.option(
    "-f",
    "--attachment",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    required=True,
    help="File to attach to the message",
)
@click.option("-n", "--name", help="(Optional) file name of the attachment.")
@click.option("-m", "--mimetype", help="(Optional) mimetype of the attachment.")
@click.argument("message", type=click.File("rb"), default="-")
def attach(
    attachment: pathlib.Path,
    name: str | None,
    mimetype: str | None,
    message: typing.BinaryIO,
):
    """Attach a file to the given email message."""

    msg = message_from_binary_file(message, policy=email.policy.default)  # type: ignore
    assert isinstance(msg, EmailMessage)

    if not name:
        name = attachment.name

    if not mimetype:
        mimetype, _ = mimetypes.guess_type(name)
        if not mimetype:
            mimetype = "application/octet-stream"

    mimetype, subtype = mimetype.split("/", 2)

    msg.add_attachment(
        attachment.read_bytes(), maintype=mimetype, subtype=subtype, filename=name
    )

    print(msg.as_string(), end="")


if __name__ == "__main__":
    attach()
