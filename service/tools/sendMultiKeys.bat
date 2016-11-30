@if (@X)==(@Y) @end /* JScript comment 
        @echo off 
       
        rem :: the first argument is the script name as it will be used for proper help message 
        cscript //E:JScript //nologo "%~f0" "%~nx0" %* 
        exit /b %errorlevel% 
@if (@X)==(@Y) @end JScript comment */ 

var sh=new ActiveXObject("WScript.Shell"); 
var ARGS = WScript.Arguments; 
var keys="";

function parseArgs(){ 
	keys=ARGS.Item(1);
}

parseArgs();

var nbKeysToSend = keys.length;
var index = 0;

while (index < nbKeysToSend) {
	sh.SendKeys(keys.charAt(index));
	index = index + 1;
}
WScript.Quit(0);
