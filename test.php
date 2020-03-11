<?php
// php parse.php < ./both/spec_example.src > xml.out
//java -jar /pub/courses/ipp/jexamxml/jexamxml.jar vas_vystup.xml referencni.xml delta.xml /pub/courses/ipp/jexamxml/options
/**
 *	Súbor:	test.php
 *	Autor:	Daniel Miloslav Očenáš (login:xocena06)
 *	Dátum:	Marec 2020
 *	Popis:	Projekt 1 predmetu IPP, VUT FIT 2020.
 */


define("ERR_INV_SCRIPT_PARAM", 10);
define("ERR_USING_INPUT_FILE", 11);
define("ERR_USING_OUTPUT_FILE", 12);


$test = new Test;
checkArgs($test);
$test->makeTests();

exit(0);

/**
 *	Funckia na vypis chyboveho vystupu
 *	a ukoncenie programu so predpokladanym chybovym kodom
 */
function terminateScript($errMsg, $errCode){
	fwrite(STDERR, $errMsg);
	exit($errCode);
}

/**
 *	Funkcia na kontrolu spravnosti argumentov
 *	V pripade ze je zadany argument --help, vypise napovedu a ukonci skript.
 *	Povoleny len argument --help alebo ziadny argument, inak sa jedna o chybu.
 */
function checkArgs($test){
	global $argv, $argc;

	if($argc == 1){
		return true;
	}
	elseif($argc > 1){
		$optsArray = array('--recursive','--directory','--parse-script','--int-script','--parse-only','--int-only','--jexamxml','--help',"test.php");
		foreach ($argv as $key) {
			if(!((strpos($key, '--parse-script') !== false ) ||(strpos($key, '--directory') !== false ) || (strpos($key, '--int-script') !== false ) || in_array($key,$optsArray))){
				fwrite(STDERR, "$key is unsupported script parameter (run script with param --help for more info)\n");
				exit(ERR_INV_SCRIPT_PARAM);
			}
		}
		$opts = getopt("",["directory::","recursive","parse-script:","int-script:","parse-only","int-only","jexamxml:","help"]);

		// potreba testovania, ci bolo zadanych viac parametrov directory 
		if (array_key_exists("directory", $opts)){
			unset($test->testDir);
			$test->testDir = [];
			if(gettype($opts['directory']) == 'string'){
				$opts['directory'] = explode(' ',$opts['directory']);
			}
			foreach ($opts['directory'] as $key) {
				if (is_dir($key)) {
					array_push($test->testDir, $key);
				}
				else{
					terminateScript("$key is not a valid directory\n",ERR_USING_INPUT_FILE);
				}
			}
		}


		if(array_key_exists("help", $opts) && $argc == 2){
			fwrite(STDOUT, "\nNápoveda\nSúbor:test.php\nAutor:Daniel Miloslav Očenáš (xocena06)\n\nTento skript vykonáva testy vstupných a výstupných súborov pre skripty parse.php a interpret.py\nnachádzajúcich sa v aktuálnom priečinku\nAko výstup vytvorí HTML stránku pre prehľad výsledku testov\n\nPovolene parametre:\n--help: vypíše nápovedu\n--directory: vykona testy vo zvolenom priecinku\n--recursive: vykoná rekurzívne testy aktuálneho priečinka\n(--parse-script|--int-script)=filename: špecifikovanie súboru parseru a interpretu\n    nesmie sa kombinovať s opačným parametrom --xxx-only a --xxx-script\n--jexamxml=file: súbor s JAR balíčkom s nástrojom A7Soft JExamXML\n--parse-only: testovaný iba skript parse.php\n--int-only: testoavný iba skript interpret.py \n");
			exit(0);
		}
		else if(array_key_exists("help", $opts) && $argc != 2){

		}
		
		if (array_key_exists("int-only", $opts) && !array_key_exists("parse-only", $opts) && !array_key_exists("parse-script", $opts) ){

		}
		else if (array_key_exists("parse-only", $opts) && !array_key_exists("int-only", $opts) && !array_key_exists("int-script", $opts) ){

		}/*
		else{	
			terminateScript("Invalid script parameter/s (run script with param --help for more info)\n",ERR_INV_SCRIPT_PARAM);		
		}*/

		return true;
		/*elseif (array_key_exists("help", $opts) && ){
		}*/

	}
	terminateScript("Invalid script parameter/s (run script with param --help for more info)\n",ERR_INV_SCRIPT_PARAM);		
}

/**
 * 
 */
class Test{
	public $testDir; /* */
	public $scripts;


	private $recursive;
	private $parseScript;
	private $intScript;
	private $jexamxml;

	function __construct(){
		$this->recursive = false;
		$this->testDir= array('./');
		$this->scripts= array(
			'parseScript' 	=> array('./parse.php'),
			'intScript'		=> array('./interpret.py'),
			'jexamxml'		=> '/pub/courses/ipp/jexamxml/jexamxml.jar'
		);
		// $this->parseScript = './parse.php';
		// $this->intScript = './interpret.py';
		// $this->jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar';
	}

	public function makeTests(){
		foreach ($this->scripts as $key) {
			if(is_array($key)){
				foreach ($key as $key1 ) {
					if (!is_file($key1)){
						echo "file $key not found\n";
					}	
				}	
			}
		}
	}
}
?>