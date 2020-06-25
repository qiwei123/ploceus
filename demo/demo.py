# -*- coding: utf-8 -*-
import ploceus

client = ploceus.ssh.SSHClient()
client.connect('example.com')

stdin, stdout, stderr, rc = client.exec_command('ls -lah')

for line in stdout:
    print(line.strip())
print(rc)
