#!/usr/bin/env python

import argparse
from terminalcloud import terminal

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('email', type=str, help='account email receiving the credit')
    parser.add_argument('amount', type=int, help='how much to share, in cents')
    parser.add_argument("-u", "--utoken", type=str, default=None ,help="Your user token")
    parser.add_argument("-a", "--atoken", type=str, default=None, help="Your access token")
    parser.add_argument("-c", "--creds", type=str, default='creds.json', help="A credentials json file")
    parser.description="Utility to share Terminal.com credit"
    args = parser.parse_args()

    terminal.setup_credentials(args.utoken, args.atoken, args.creds)
    print terminal.gift(args.email, args.amount)