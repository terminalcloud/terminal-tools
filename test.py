#!/usr/bin/env python

from terminalcloud import terminal

terminal.setup_credentials(None,None,'creds_damian.json')
print terminal.get_terminal(None,'damian3')
terminal.add_authorized_key_to_terminal('2f7955e7-10e6-4861-96ce-68544f78ff85',
                                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCvmV/cTrjIn+F1wJwY0eC/nI/aoRJ8ZZJ0b6QfA7VG/iImQtQRq4sLRMSRy858N9eyxx3IMA46JGb4KN2epPULOm/fLoTCouz5ZjQK30aFqmU4AiK4q0JZ5VLfx1BvoLCuWt9kM/gvliydGIp910Ab0w6tPJgz3gaXBUjjHCDLQf3T/JERIfdqB79n6Cjai8+EB0LXYpET4o+fOK/aHifTl938NrNCaE0t5G+VQu0W7Y9x5kcvLVyNd/KzS+xvp9IaPfQq5z/94R3c+VWBivCSWWDT9D71jUnUjZZ8l+VtsnSpymkR6rPMagtkXYTmY1XzRqvdzxn1lRwal3FkgVPP concien1@econci')