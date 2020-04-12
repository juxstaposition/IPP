<?php
// php parse.php < ./both/spec_example.src > xml.out
//java -jar /pub/courses/ipp/jexamxml/jexamxml.jar vas_vystup.xml referencni.xml delta.xml /pub/courses/ipp/jexamxml/options
/**
 *	Súbor:	test.php
 *	Autor:	Daniel Miloslav Očenáš (login:xocena06)
 *	Dátum:	Apr9l 2020
 *	Popis:	Projekt 2 predmetu IPP, VUT FIT 2020.
 */

define("ERR_INV_SCRIPT_PARAM", 10);
define("ERR_USING_INPUT_FILE", 11);
define("ERR_USING_OUTPUT_FILE", 12);

$test = new Test();

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
 *
 *
 */
function testFileParam($param,$opts,$test){
	if(gettype($opts[$param]) == 'string' || gettype($opts[$param]) == 'boolean'){
		$opts[$param] = explode(' ',$opts[$param]);
	}
	foreach ($opts[$param] as $key) {
		// var_dump($key);
		// var_dump(gettype($opts[$param]));
		if ($param != 'directory' && is_file($key)) {
			$test->scripts[$param] = $key;
		}
		else if($param == 'directory' && is_dir($key)){
			array_push($test->testDir, $key);	
		}
		else{
			$msg = '';
			if($param == 'directory' ){
				$msg = "'$key' v parametri $param nie je platny priecinok\n";
			}
			else{
				$msg = "'$key' v parametri $param nie je platny subor\n";
			}
			terminateScript($msg,ERR_USING_INPUT_FILE);
		}
	}
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
				terminateScript("$key nepodporovany parameter skriptu (pre viac info pouzi parameter --help)\n", ERR_INV_SCRIPT_PARAM);
			}
		}
		$opts = getopt("",["directory::","recursive","parse-script::","int-script::","parse-only","int-only","jexamxml::","help"]);
		
		if(array_key_exists("help", $opts) && $argc == 2){
			fwrite(STDOUT, "\nNápoveda\nSúbor:test.php\nAutor:Daniel Miloslav Očenáš (xocena06)\n\nTento skript vykonáva testy vstupných a výstupných súborov pre skripty parse.php a interpret.py\nnachádzajúcich sa v aktuálnom priečinku\nAko výstup vytvorí HTML stránku pre prehľad výsledku testov\n\nPovolene parametre:\n--help: vypíše nápovedu\n--directory: vykona testy vo zvolenom priecinku\n--recursive: vykoná rekurzívne testy aktuálneho priečinka\n(--parse-script|--int-script)=filename: špecifikovanie súboru parseru a interpretu\n    nesmie sa kombinovať s opačným parametrom --xxx-only a --xxx-script\n--jexamxml=file: súbor s JAR balíčkom s nástrojom A7Soft JExamXML\n--parse-only: testovaný iba skript parse.php\n--int-only: testoavný iba skript interpret.py \n");
			exit(0);
		}
		else if(array_key_exists("help", $opts) && $argc > 2){
			terminateScript("Parameter --help musi byt pouzity samostatne");
		}
		
		if(array_key_exists("recursive", $opts)){
			$test->recursive = true;
		}

		if(array_key_exists("jexamxml", $opts)){
			if (is_file($opts['jexamxml'])) {
				$test->scripts['jexamxml'] = $opts['jexamxml'];
			}
			else{
				terminateScript('\''.$opts['jexamxml'] .'\' is not a valid file'.PHP_EOL,ERR_USING_INPUT_FILE);
			}
		}

		// spravna kombinacia int only - spracuj
		if (array_key_exists("int-only", $opts) && !array_key_exists("parse-only", $opts) && !array_key_exists("parse-script", $opts) ){
			unset($test->scripts['parse-script']);
		}
		// spravna kombinacia parse only - spracuj
		else if (array_key_exists("parse-only", $opts) && !array_key_exists("int-only", $opts) && !array_key_exists("int-script", $opts) ){
			unset($test->scripts['int-script']);
		}
		// nespravna kombinacia int only - ukonci
		else if (array_key_exists("int-only", $opts) && (array_key_exists("parse-only", $opts) || array_key_exists("parse-script", $opts)) ){
			terminateScript("$key nepodporovana kombinacia parametrov skriptu (pre viac info pouzi parameter --help)\n", ERR_INV_SCRIPT_PARAM);	
		}
		// nespravna kombinacia parse only - ukonci
		else if (array_key_exists("parse-only", $opts) && (array_key_exists("int-only", $opts) || array_key_exists("int-script", $opts)) ){
			terminateScript("$key nepodporovana kombinacia parametrov skriptu (pre viac info pouzi parameter --help)\n", ERR_INV_SCRIPT_PARAM);		
		}

		// potreba testovania, ci bolo zadanych viac parametrov directory, int-script, parse-script
		if (array_key_exists("directory", $opts)){
			unset($test->testDir);
			$test->testDir = [];
			testFileParam('directory',$opts,$test);
		}

		if (array_key_exists("int-script", $opts)){
			unset($test->scripts['int-script']);
			testFileParam('int-script',$opts,$test);
		}
		
		if (array_key_exists("parse-script", $opts)){
			unset($test->scripts['parse-script']);
			testFileParam('parse-script',$opts,$test);			
		}

		echo "params ok\n";
		return true;
	}
	terminateScript("Invalid script parameter/s (run script with param --help for more info)\n",ERR_INV_SCRIPT_PARAM);		
}

/**
 *	Trieda Automatickych testov
 */
class Test{
	public $testDir; /* */
	public $scripts;
	public $recursive;

	function __construct(){
		$this->testDir= array('./');
		$this->scripts= array(
			'parse-script' 	=> array('./parse.php'),
			'int-script'	=> array('./interpret.py'),
			'jexamxml'		=> '/pub/courses/ipp/jexamxml/jexamxml.jar'
		);
	}

	public function makeTests(){
		echo "Make tests Test Dir:";
		var_dump($this->testDir);
		var_dump($this->scripts);
		var_dump($this->recursive);
		
		$dirIterator ;
		if($this->recursive){
			$directory = new RecursiveDirectoryIterator($this->testDir[0], RecursiveDirectoryIterator::SKIP_DOTS);
			$dirIterator = new RecursiveIteratorIterator($directory);
		}
		else{
			$dirIterator = new DirectoryIterator($this->testDir[0]);
		}
		
		$srcFiles = [];
		foreach ($dirIterator as $iterator){
			// var_dump($iterator->getPath()); 
			// var_dump($iterator->getPathname());
			if(strcmp($iterator->getExtension(),'src') == 0){
				$srcFile = array(
					"name" => $iterator->getBasename('.src'),
					"path" => $iterator->getPath(),
				);
				array_push($srcFiles, $srcFile);
			}
		}
		var_dump($srcFiles);	
		foreach($srcFiles as $srcFile){

			$files = $this->openFiles($srcFile['name'],$srcFile['path']);
			$this->closeFiles($files);
			var_dump(is_file($srcFile['path'].'/'.$srcFile['name'].'.rc'));
		}

	}
	
	private function openFiles($filename,$path){
		$rcExists = false;
		
		if( is_file($path.'/'.$filename.'.rc') ){
			$rcExists = true;
		}
		
		$files = array(
			'src' => fopen($filename.'src', "w+") ,
			'rc' =>fopen($filename.'rc', "w+"),
			'in' =>fopen($filename.'in', "w+"),
			'out' =>fopen($filename.'out', "w+"),
		);

		if(!$rcExists){
			fwrite($files['rc'],0);
		}
		return $files;
	}

	private function closeFiles($files){
		foreach($files as $file){
			fclose($file);
		}
	}
}
?>