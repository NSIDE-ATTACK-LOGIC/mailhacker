import click

from mailhacker.commands.attach import attach
from mailhacker.commands.compose import compose
from mailhacker.commands.dkim import dkim
from mailhacker.commands.send import send


@click.group()
def cli():
    """MailHacker: a suite of tools to compose and/or send emails.
    
    Copyright (c) 2025 NSIDE ATTACK LOGIC GmbH
    """
    pass


cli.add_command(attach)
cli.add_command(compose)
cli.add_command(dkim)
cli.add_command(send)

if __name__ == "__main__":
    cli()
