#!/usr/bin/env python

import email
import logging
import re
from imaplib import IMAP4_SSL
from sleekxmpp import ClientXMPP

from config import config

read_pattern = re.compile(r'^read (\d+)$')

class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)
        self.schedule('Check mail', 10, self._check_mail, repeat=True)
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199')


    def start(self, event):
        imap = IMAP4_SSL(config['imap_host'])
        imap.login(config['imap_user'], config['imap_pass'])
        imap.select('INBOX')
        self.imap = imap
        self.get_roster()
        self.send_presence(pnick='imapbot')


    def _check_mail(self):
        self.imap.check()
        self.imap.recent()
        typ, data = self.imap.search(None, '(UNSEEN)')
        msg_nums = data[0].split()
        for num in msg_nums:
            typ, data = self.imap.fetch(num, '(RFC822.SIZE BODY[HEADER.FIELDS (FROM SUBJECT)])')
            mfrom, _, rest = data[0][1].partition('\r\n')
            msubj, _, _ = rest.partition('\r\n')
            body = '(%(num)s) From %(name)s: %(subject)s' % {
                'subject': msubj.strip()[9:],
                'name': mfrom.strip()[6:],
                'num': num
            }
            self.send_message(mto=config['jabber_to'], mbody=body, mtype='normal', mnick='imapbot')


    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            m = read_pattern.match(msg['body'])
            if m:
                typ, data = self.imap.fetch(m.group(1), '(RFC822)')
                body = email.message_from_string(data[0][1])
                if body.get_content_maintype() == 'multipart':
                    for part in body.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True)
                            break
                self.send_message(mto=msg['from'], mbody=body.strip(), mtype=msg['type'], mnick='imapbot')
            else:
                self.send_message(mto=msg['from'], mbody='Hello', mtype=msg['type'], mnick='imapbot')


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
    xmpp = EchoBot(config['jabber_user'], config['jabber_pass'])
    xmpp.connect()
    xmpp.process(block=True)
