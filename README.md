# smbDumper
smbDumper  

smbDumper crawls anonymous SMB shares (adding authentication soon!) for "interesting" documents like doc, docx, xls, xlsx, txt, zip, pst, pdf, vmdk or filenames containing the word "password" or "pass".    

In additional, if you supply credentials to the script, it will attempt to connect to the registry of the remote host and extracts credentials as shown in the below article.
http://www.nirsoft.net/articles/saved_password_location.html
  
If it is a Windows domain controller, it will attempt to check the Netlogon folder and checks for GPO password
Refer to http://blog.spiderlabs.com/2013/09/top-five-ways-spiderlabs-got-domain-admin-on-your-internal-network.html  
    
It allow finds the below files and extract the credentials (to be implemented)  
-	Firefox credentials files (key3.db and signons.sqlite)  
-	Filezilla (sitemanager.xml and filezilla.xml)   
-	Microsoft Live Mail (.oeaccount)  
-	Thunderbird (.s)  

Below is a sample screenshot of the script.    
![alt tag](https://raw.githubusercontent.com/milo2012/smbDumper/master/smbDumper.png)

