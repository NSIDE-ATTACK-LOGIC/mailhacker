import os
import pathlib
import sys
import typing
from email import message_from_binary_file

import click

try:
    import dkim as dkimpy
except ImportError:
    dkimpy = None


@click.command()
@click.option(
    "-p",
    "--private-key",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    help="PEM-encoded private key for signing the message.",
)
@click.option(
    "-s",
    "--selector",
    default="selector",
    help="DKIM selector, used when querying the public key.",
)
@click.option(
    "-d",
    "--domain",
    default=os.environ.get("HOST"),
    help="Domain for querying the public key.",
)
@click.argument("message", type=click.File("rb"), default="-")
def dkim(
    private_key: pathlib.Path, selector: str, domain: str, message: typing.BinaryIO
):
    """Sign the given email message with DKIM."""

    if dkimpy is None:
        click.secho(
            "DKIM signing requires the Python package 'dkim'.", err=True, fg="red"
        )
        return

    msg = message_from_binary_file(message)

    header = dkimpy.sign(
        msg.as_bytes(),
        selector.encode(),
        domain.encode(),
        private_key.read_bytes(),
    )
    assert header.startswith(b"DKIM-Signature: ")
    name, _, value = header.decode().partition(": ")

    msg.add_header(name, value)

    print(msg.as_string(), end="")


if __name__ == "__main__":
    dkim()
