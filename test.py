#!/usr/bin/env python

import urllib2
import json
url = "https://www.terminal.com/api/v0.2/add_terminal_links"
headers = {
  "user-token": "dee99f538f754cdf52db7375cc220b3c434d39facb9dec0605b94b93c2951873",
  "access-token": "OuL19GPNBkTXfPl5LTmW6cPbWCoHqxyi",
  "Content-Type": "application/json"
}
params = {
  "container_key": "7a7040cb-1d9b-4fad-823a-bc20872222bb",
  "links": [
    {
      "source": "terminal30980",
      "port": "*"
    }
  ]
}
data = json.dumps(params)
print data
req = urllib2.Request(url, data, headers)
response = json.loads(urllib2.urlopen(req).read())
print response