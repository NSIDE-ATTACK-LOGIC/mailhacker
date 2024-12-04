# MailHacker

MailHacker is a collection of tools for composing, manipulating and sending emails.

MailHacker can be installed using [Pipx](https://github.com/pypa/pipx):

```bash
pipx install 'git+https://github.com/NSIDE-ATTACK-LOGIC/mailhacker'
```

After the installation, the following commands should be (globally) available:

* `mh compose`
* `mh attach`
* `mh dkim`
* `mh send`

All tools are documented in a help text that can be displayed with: `mh <command> --help`. The basic idea of the MailHacker is that complex email messages can be composed by chaining multiple scripts using shell pipes.

Mails can be composed with `mh compose`, for example:

```console
$ echo "Hello World" | mh compose -f 'sender@example.org' -t 'recipient@example.com'
From: sender@example.org
To: recipient@example.com
Date: Wed, 19 Feb 2025 11:06:01 -0000
Message-ID: <173995956133.106947.8168332187011401181.mailhacker@example.org>

Hello World
```

Thanks to bash pipes you can already send this message with `mh send` (`-n`/`--dry` starts `mh send` in "dry mode", without actually sending things):

```console
$ echo "Hello World" | mh compose -f 'sender@example.org' -t 'recipient@example.com' | mh send -n
Would connect to :25 ...
ehlo [127.0.1.1]
mail FROM:<sender@example.org>
rcpt TO:<recipient@example.com>
data
From: sender@example.org
To: recipient@example.com
Date: Wed, 19 Feb 2025 11:08:22 -0000
Message-ID: <173995970240.108854.12926488992456421901.mailhacker@example.org>

Hello World
.
QUIT
Closing connection.
```

Alternatively, you can always save the message in a file, modify it and send it later, e.g:

```console
$ echo "Hello World" | mh compose -f 'sender@example.org' -t 'recipient@example.com' > hello_world.eml
$ sed -i 's/Hello/Bye/' hello_world.eml
$ mh send -n hello_world.eml
Would connect to :25 ...
ehlo [127.0.1.1]
mail FROM:<sender@example.org>
rcpt TO:<recipient@example.com>
data
From: sender@example.org
To: recipient@example.com
Date: Wed, 19 Feb 2025 11:10:16 -0000
Message-ID: <173995981652.110346.14283199267867659891.mailhacker@example.org>

Bye World
.
QUIT
Closing connection.
```

## Installation from Source

As an alternative to Pipx, you can of course also install the project from source (ideally into a virtual environment):

```bash
git clone https://github.com/nside-attack-logic/mailhacker
cd mailhacker

python3 -m venv venv
. venv/bin/activate
pip install -e .
```