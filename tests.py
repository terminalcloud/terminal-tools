import json
import terminal


terminal.setup_credentials(None, None,'creds.json')
# Creating
# request = terminal.start_snapshot('7067f369f7b76f0a3276beb561820a21c9b5204ab60fbd90524560db96d7cb38',None,None,'TESTING')
#list = terminal.list_terminals()['terminals']
# terminal.delete_terminal('109a976f-3713-400a-9457-dd5eeae28bf2')
# TESTING - 2f22ef3f-7a46-42ae-8fd4-396fe405e3a2
snapshot_id = '7067f369f7b76f0a3276beb561820a21c9b5204ab60fbd90524560db96d7cb38'
container_key = '2f22ef3f-7a46-42ae-8fd4-396fe405e3a2'

print terminal.get_snapshot(snapshot_id)['success']
print terminal.balance()['balance']
