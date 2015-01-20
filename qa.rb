#!/usr/bin/env ruby

require 'terminal.com/api'
require 'date'
require 'json'

# Usage: ./qa.rb [production Terminal container_key] [how many Terminals to spin up] [Git ref]
def usage
  abort("Usage: #{$0} [container_key] [terminals_number] [git_ref]")
end

container_key = ARGV.shift || usage
terminal_count = ARGV.shift.to_i || usage
git_ref = ARGV.shift || usage
creds= JSON.parse(File.read('creds.json'))


api = Terminal::API.new(creds['user_token'],creds['access_token'])

# https://www.terminal.com/api/docs#snapshot-terminal
puts "~ Taking a snapshot of the production environment."
response = api.snapshot_terminal(container_key, title: "Backup #{Time.now.strftime('%Y-%m-%d-%H-%M')}")
request_id = response['request_id']

snapshot_id = loop do
  print "."
  response = Terminal.request_progress(request_id)
  snapshot_id = response['result']
  if snapshot_id
    break snapshot_id
  elsif response['status'] == 'failed'
    abort "\nError occurred when trying to snapshot the production Terminal: #{response.inspect}"
  end
  sleep 1
end

puts "\n~ Snapshot is ready, spinning up Terminals ..."

# https://www.terminal.com/api/docs#start-snapshot
startup_script = DATA.read.gsub(/%GIT_REF%/, git_ref)
terminal_count.times.map do |i|
  name = "QA #{git_ref} #{i}"
  puts "~ Spinning up Terminal #{name}"
  api.start_snapshot(snapshot_id, name: name, startup_script: startup_script)
end

__END__
cd /var/www/expense-tracker/server;
stop expense-tracker-server;
git fetch;
git checkout %GIT_REF% ;
start expense-tracker-server;