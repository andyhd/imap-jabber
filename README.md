IMAP Jabber Bot
===============

This is a simple script that connects to an IMAP server, checks for new mail
every 10s and sends jabber messages to a specified account for each new mail.

You can send a message to the bot in the form "read x", where x is the number
of the mail, and it will reply with the body of the email.

You need to create a `config.py` file in the same directory, which looks like
this:

    config = {
        'imap_host': 'imap.example.com',
        'imap_user': 'andy@example.com',
        'imap_pass': 'imap password',
        'jabber_to': 'example.jabberid@jabber.org',
        'jabber_user': 'your.jabberid@jabber.org',
        'jabber_pass': 'jabber password'
    }

Why?
----

It's just a quick hack I wrote to give me convenient access to my emails, since
I always have a chat window open for IRC anyway.
