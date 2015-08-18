from terminalcloud import terminal
import time

terminal.setup_credentials(None,None,'creds.json')
ubuntu='987f8d702dc0a6e8158b48ccd3dec24f819a7ccb2756c396ef1fd7f5b34b7980'
ipython='e812ebe24e3796846a0a4b930a810a45135af5fbcc5502a32526fc4c80b8e09b'

def start_terminal():
    req_id=terminal.start_snapshot(ipython,'micro',None,'testv2',None,None)
    print req_id['request_id']
    while True:
        time.sleep(2)
        print terminal.request_progress(req_id['request_id'])



#start_terminal()

#print terminal.list_terminals()['terminals'][0]
ckey='7a7040cb-1d9b-4fad-823a-bc20872222bb'
#links = terminal.list_terminal_access(ckey)['links']
#flinks = map(lambda x: {'port':x.split(':')[0],'source':x.split(':')[-1]},links)
#terminal.remove_terminal_links(ckey, flinks)
#print terminal.list_terminal_access(ckey)['links']


#print(terminal.request_progress('1437552001497::terminal@cloudlabs.io:create:2362702::3f35f5f7-a1e9-4431-8dc7-aefe8060e3be'))
print(terminal.get_terminal(ckey))
print terminal.add_terminal_links(ckey,[{"port":"*", "source":"terminal30908"}])

links = terminal.list_terminal_access(ckey)['links']
flinks = map(lambda x: {'port':x.split(':')[0],'source':x.split(':')[-1]},links)

print flinks