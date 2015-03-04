import json
import terminal


print terminal.setup_credentials(None, None,'creds.json')

def get_public_key(key_file):
    with open(key_file) as f:
        content = f.readlines()[0].rstrip('\n')
    return content

# Creating
# request = terminal.start_snapshot('7067f369f7b76f0a3276beb561820a21c9b5204ab60fbd90524560db96d7cb38',None,None,'TESTING')
list = terminal.list_terminals()['terminals']
for i in range(len(list)):
    print '%s - %s' % (list[i]['name'],list[i]['container_key'])


# terminal.delete_terminal('109a976f-3713-400a-9457-dd5eeae28bf2')
# TESTING - 2f22ef3f-7a46-42ae-8fd4-396fe405e3a2
snapshot_id = '7067f369f7b76f0a3276beb561820a21c9b5204ab60fbd90524560db96d7cb38'
container_key = '6e1c7266-cb55-40f9-b76f-2f51cfcfe883'

publicKey=get_public_key('pemfile.pub')
#print terminal.get_terminal(container_key)
print terminal.add_authorized_key_to_terminal(container_key, publicKey)
#print terminal.balance()['balance']

print publicKey

