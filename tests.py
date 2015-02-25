import json
import time
import terminal

terminal.setup_credentials(None, None,'creds.json')
request_id=json.loads(terminal.start_snapshot('7067f369f7b76f0a3276beb561820a21c9b5204ab60fbd90524560db96d7cb38'))['request_id']
while True:
    print terminal.request_progress(request_id)
    time.sleep(1)