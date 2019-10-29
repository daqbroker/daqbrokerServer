import os
import sys
import random
import string
import platform
from pathlib import Path
from subprocess import call


class rsyncServer:
	def __init__(self, backupRoot = ""):
		allchar = string.ascii_letters + string.digits
		self.port = 9000
		self.user = "daqbroker"
		self.passwd = "test" #"".join(random.choice(allchar) for x in range(random.randint(8, 12)))
		self.command = ""
		self.paths = {
			"backupRoot": Path("./fileBackups"),
			"secrets": Path("rsyncd.secrets"),
			"config": Path("rsyncd.conf")
		}

		#Sets up the command for calling rsync
		self.setupCommand()

		#Create secrets file
		self.setupSecrets()

		#Create config file
		self.setupConfig()

	def setupSecrets(self):
		secretsfh = open(self.paths["secrets"], 'w')
		secretsfh.write(self.user + ':' + self.passwd)
		secretsfh.close()

	def setupConfig(self):
		rsyncConfig = open(self.paths["config"], 'w')
		rsyncConfig.write("use chroot = false\n")
		rsyncConfig.write("log file = rsyncd.log\n")
		rsyncConfig.write("lock file = rsyncd.lock\n")
		rsyncConfig.write("[daqbroker]\n")
		rsyncConfig.write("   path = " + self.paths["backupRoot"].as_posix() + "\n")
		rsyncConfig.write("   comment = DAQBroker backup server\n")
		rsyncConfig.write("   strict modes = no\n")
		rsyncConfig.write("   auth users = daqbroker\n")
		rsyncConfig.write("   secrets file = " + self.paths["secrets"].as_posix() + "\n")
		rsyncConfig.write("   read only = false\n")
		rsyncConfig.write("   list = false\n")
		rsyncConfig.write("   fake super = yes\n")
		rsyncConfig.close()

	def setupBackup(self):
		full_folder = self.paths["backupRoot"]
		if not os.path.isdir(full_folder):
			os.makedirs(full_folder)

	def setupCommand(self):
		if(platform.system() == 'Windows'):  # Running on windows machine
			self.command = str(Path(__file__).parent) + "\\rsync\\rsync --daemon --port=" + str(self.port) +" --config=" + self.paths["config"].as_posix() + " --no-detach --log-file=logFile.log"
		else:
			self.command = "rsync --daemon --port=" + str(self.port) +" --config=" + self.paths["config"].as_posix() + " --no-detach --log-file=logFile.log"

	def serve(self):
		self.setupBackup()
		print(self.command)
		call(self.command, shell=True)

