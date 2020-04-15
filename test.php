<?php
/**
 *	Súbor:	test.php
 *	Autor:	Daniel Miloslav Očenáš (login:xocena06)
 *	Dátum:	April 2020
 *	Popis:	Projekt 2 predmetu IPP, VUT FIT 2020.
 */
define("ERR_INV_SCRIPT_PARAM", 10);
define("ERR_USING_INPUT_FILE", 11);
define("ERR_USING_OUTPUT_FILE", 12);
define("PHP_SCRIPT_CMD","php7.4"); // php7.4 / php
define("PYTHON_SCRIPT_CMD","python3.8"); // python3.8 / py

/**
 * MAIN
 */
$test = new Test();

checkArgs($test);

$test->makeTests();

testsOutput($test->testResults);

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
 * Funkcia kontroluje ci hodnota zadana parametru je validny subor alebo priecinok
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
				$msg = "Priečinok '$key' v parametri $param neexistuje\n";
			}
			else{
				$msg = "Súbor '$key' v parametri $param neexistuje\n";
			}
			terminateScript($msg,ERR_USING_INPUT_FILE);
		}
	}
}

/**
 *	Funkcia kontroluje spravnost argumentov
 *	podla zadanych argumentov predava triede test
 *	informaciu o nasteveni testov
 *  @param test instancia triedy test
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
				terminateScript("$key nepodporovaný parameter skriptu (pre viac info použi parameter --help)\n", ERR_INV_SCRIPT_PARAM);
			}
		}
		$opts = getopt("",["directory::","recursive","parse-script::","int-script::","parse-only","int-only","jexamxml::","help"]);
		
		if(array_key_exists("help", $opts) && $argc == 2){
			fwrite(STDOUT, "\nNápoveda\nSúbor:test.php\nAutor:Daniel Miloslav Očenáš (xocena06)\n\nTento skript vykonáva testy vstupných a výstupných súborov pre skripty parse.php a interpret.py\nnachádzajúcich sa v aktuálnom priečinku\nAko výstup vytvorí HTML stránku pre prehľad výsledku testov\n\nPovolene parametre:\n--help: vypíše nápovedu\n--directory: vykona testy vo zvolenom priecinku\n--recursive: vykoná rekurzívne testy aktuálneho priečinka\n(--parse-script|--int-script)=filename: špecifikovanie súboru parseru a interpretu\n    nesmie sa kombinovať s opačným parametrom --xxx-only a --xxx-script\n--jexamxml=file: súbor s JAR balíčkom s nástrojom A7Soft JExamXML\n--parse-only: testovaný iba skript parse.php\n--int-only: testoavný iba skript interpret.py \n");
			exit(0);
		}
		else if(array_key_exists("help", $opts) && $argc > 2){
			terminateScript("Parameter --help musí byť použitý samostatne");
		}
		
		if(array_key_exists("recursive", $opts)){
			$test->recursive = true;
		}

		if(array_key_exists("jexamxml", $opts)){
			if (is_file($opts['jexamxml'])) {
				$test->scripts['jexamxml'] = $opts['jexamxml'];
			}
			else{
				terminateScript(''.$opts['jexamxml'] .'nieje platny subor'.PHP_EOL,ERR_USING_INPUT_FILE);
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
			terminateScript("$key nepodporovaná kombinácia parametrov skriptu (pre viac info pouzi parameter --help)\n", ERR_INV_SCRIPT_PARAM);	
		}
		// nespravna kombinacia parse only - ukonci
		else if (array_key_exists("parse-only", $opts) && (array_key_exists("int-only", $opts) || array_key_exists("int-script", $opts)) ){
			terminateScript("$key nepodporovaná kombinácia parametrov skriptu (pre viac info pouzi parameter --help)\n", ERR_INV_SCRIPT_PARAM);		
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

		return true;
	}
	terminateScript("Nesprávna kombinácia parametrov skriptu\n",ERR_INV_SCRIPT_PARAM);		
}

/**
 *	Trieda Automatickych testov
 */
class Test{
	public $testDir; /* Pole skumanych priecinkov */
	public $scripts; /* Pole nazvov testovanych skriptov, moze byt zdanych viac */
	public $recursive; /* Boolean, Oznacuje rekurzivne prehladavanie precinkov, aktivuje sa pomocou parametru --recursive */
	public $testResults; /* Pole vysledkov testov */

	/**
	 * Konstruktor triedy test
	 * Inicializacia defaultnych nazvov skriptov a nastroja jexamxml
	 */
	function __construct(){
		$this->testDir= array('./');
		$this->scripts= array(
			'parse-script' 	=> array('./parse.php'),
			'int-script'	=> array('./interpret.py'),
			'jexamxml'		=> '/pub/courses/ipp/jexamxml/jexamxml.jar'
		);
		$this->recursive = false;
		$this->testResults = array();
	}

	/**
	 * Funkcia vykonava testy skriptov parse a interpret
	 */
	public function makeTests(){
		foreach($this->testDir as $testDir){ 

			// iterator priecinkov
			$dirIterator;

			// ak je zadany parameter --recursive, pouzije sa rekurzivny iterator priecinkov
			if($this->recursive){
				$directory = new RecursiveDirectoryIterator($testDir, RecursiveDirectoryIterator::SKIP_DOTS);
				$dirIterator = new RecursiveIteratorIterator($directory);
			}
			// iterator zadaneho priecinka alebo ./
			else{
				$dirIterator = new DirectoryIterator($testDir);
			}
			
			// pomocou iteratoru sa vyhladaju vsetky src subory
			$srcFiles = [];
			foreach ($dirIterator as $iterator){
				if(strcmp($iterator->getExtension(),'src') == 0){
					$srcFile = array(
						"name" => $iterator->getBasename('.src'),
						"path" => $iterator->getPath(),
					);
					array_push($srcFiles, $srcFile);
				}
			}

			// test kazdeho najdenho src suboru
			foreach($srcFiles as $srcFile){
				$expectedResults = $this->checkInputFiles($srcFile['name'],$srcFile['path']);
				$srcFullPath = $srcFile['path'].'/'.$srcFile['name'].'.src';
				
				// vykona int only testy
				if(array_key_exists('parse-script',$this->scripts) === false && array_key_exists('int-script',$this->scripts) == true  ){
					$this->execInterpret($srcFullPath,$srcFile['path'],$srcFile['name'],$expectedResults );
				}
				else {					
					// Test pre vsetky php skripty zadane opakovnaym parametrom --parse-script
					// defaultne pouzity skript ./parse.php
					foreach($this->scripts['parse-script'] as $phpScript){
						unset($parseOutput);
						exec(PHP_SCRIPT_CMD .' '. $phpScript . ' < ' . $srcFullPath.' 2>&1',  $parseOutput, $parseReturnCode);
						
						// parser sa ukoncil spravne
						if($parseReturnCode == 0  ){

							$srcInterpretFullPath = $srcFile['path'].'/'.$srcFile['name'].'.xml';
								
							file_put_contents($srcInterpretFullPath,  implode(PHP_EOL, $parseOutput) );

							//parse only testy
							if(array_key_exists('parse-script',$this->scripts) === true && array_key_exists('int-script',$this->scripts) == false  ){
								// /pub/courses/ipp/jexamxml/jexamxml.jar vas_vystup.xml referencni.xml delta.xml 
								if ( $expectedResults['rc'] == 0){
									
									$outFile =  $srcFile['path'].'/'.$srcFile['name'].'.out';

									$returnFile =  $srcFile['path'].'/'.$srcFile['name'].'delta.xml';
									
									exec('java -jar '.$this->scripts['jexamxml'].' '.$srcInterpretFullPath.' '.$outFile.' '.$returnFile. ' /pub/courses/ipp/jexamxml/options',$xmlOutput, $xmlRetCode);
									
									
									if ( $xmlRetCode == 0 ){								
										$this->addTestResult($srcFullPath,'','',$expectedResults['rc'],$parseReturnCode,true, 'Výstup skriptu vyhodnotený nástrojom A7Soft JExamXML ako zhodný');
									}else{
										$this->addTestResult($srcFullPath,$xmlOutput,'Výstup sa nezhoduje s referenčným',$expectedResults['rc'],$parseReturnCode,false, 'Výstup skriptu vyhodnotený nástrojom A7Soft JExamXML ako odlišný');
									}	
								}else{
									
									$this->addTestResult($srcFullPath,'','Návratové kódy sa nezhodujú',$expectedResults['rc'],$parseReturnCode,false,'Návratovy kód sa nezhoduje s referenčným');
								}
							}
							// vykonanie parse aj interpret testu
							else{
								$this->execInterpret($srcInterpretFullPath, $srcFile['path'],$srcFile['name'],$expectedResults);
								
							} // parse only 
						}
						// parser ukonceny s chybou
						else{
							// porovnanie ocakavaneho kodu a navratoveho kodu parsru a zapisanie statistik
							if(intval($expectedResults['rc']) == $parseReturnCode){
								$this->addTestResult($srcFullPath,'','Chybové návratové kódy sa zhodujú',$expectedResults['rc'],$parseReturnCode,true, 'TEST OK');
							}
							else{
								$this->addTestResult($srcFullPath,'',$parseOutput,$expectedResults['rc'],$parseReturnCode,false,'Návratovy kód sa nezhoduje s referenčným');
							}
						}
					}

				}	// end for each .src file
			}	// end int only
		}	// end foreach test dir

	}	// end function make test
	
	/**
	 * @param srcInterpretFullPath
	 * @param srcPath
	 * @param srcName
	 * @param expectedResults
	 */
	private function execInterpret($srcInterpretFullPath, $srcPath, $srcName, $expectedResults){
		$inputInterpretFileName = $srcPath.'/'.$srcName.'.in';
		
		foreach($this->scripts['int-script'] as $intScript){
			exec(PYTHON_SCRIPT_CMD.' '.$intScript.' --source='.$srcInterpretFullPath.' --input='.$inputInterpretFileName.' 2>&1', $intOutput, $intReturnCode);

			// navratove kody sa zhoduju
			if($intReturnCode == 0 && intval($expectedResults['rc']) == 0){
				$outputFile = $srcPath.'/'.$srcName.'.out';
				$interpretOutputFile = $srcPath.'/'.$srcName.'.myout';
				

				file_put_contents($interpretOutputFile,implode(PHP_EOL, $intOutput));

				exec('diff ' . $interpretOutputFile . ' ' . $outputFile , $output , $diffReturnCode);
				// nastroj diff vyhodnoti vystupne subory ako zhodne
				if($diffReturnCode == 0 ){
					$this->addTestResult("$srcName.src",$expectedResults['out'],$intOutput,$expectedResults['rc'],$intReturnCode,true,'TEST OK');
				}else{
					$this->addTestResult("$srcName.src",$expectedResults['out'],$intOutput,$expectedResults['rc'],$intReturnCode,false,'Výstup sa nezhoduje s referenčným, výsledok diff:'.PHP_EOL.implode(PHP_EOL, $output));
				}
			}else{
				if($intReturnCode == intval($expectedResults['rc']) ){
					$this->addTestResult("$srcName.src",'','Chybové návratové kódy sa zhodujú',$expectedResults['rc'],$intReturnCode,true,'TEST OK');
				}else{
					if(intval($expectedResults['rc']) == 0){
						$this->addTestResult("$srcPath/$srcName.src",$expectedResults['out'],$intOutput,$expectedResults['rc'],$intReturnCode,false,'Návratovy kod sa nezhoduje s referenčným');
					}else{
						$this->addTestResult("$srcPath/$srcName.src",'',$intOutput,$expectedResults['rc'],$intReturnCode,false,'Návratový kód sa nezhoduje s referenčným');
					}
				}
			}
		}
	}

	/**
	 * Funkcia uklada vysledok testu
	 * 
	 * @param path testovany subor
	 * @param expectedReturn Obsah zadaneho in suboru
	 * @param return Vysledok testu
	 * @param expectedRetCode ocakavany navratovy kod
	 * @param retCode navratovy kod testu
	 * @param passed hodnota true pre uspesny test, false neuspesny test
	 */
	private function addTestResult($path,$expectedReturn,$return,$expectedRetCode, $retCode,$passed,$msg){
		if(is_array($expectedReturn)){
			$expectedReturn = implode('&#10;',$expectedReturn);
		}		
		if(is_array($return)){
			$return = implode('&#10;',$return);
		}
		$path = str_replace("\\", "/", $path);
		array_push($this->testResults,array(
			'path' => $path,
			'expectedReturn' => $expectedReturn,
			'return' => $return,
			'expectedRetCode' => $expectedRetCode,
			'retCode' => $retCode,
			'result' => $passed,
			'description' => $msg
		));
	}


	/**
	 * Funkcia vykona kontrolu vstupnych suborov podla nazvu testoveho suboru
	 * V pripade, ze k testu chybaju suboru rc/in/out, chybajuci subor je dogenerovany
	 * 
	 * @param filename nazov suboru
	 * @param path cesta k suboru
	 */
	private function checkInputFiles($filename,$path){
		
		$files = array();
		
		foreach (['rc', 'in', 'out'] as $extension){
			
			if( is_file($path.'/'.$filename.'.'.$extension) ){
				$files[$extension] = file_get_contents($path.'/'.$filename.'.'.$extension);
				if( $files[$extension] === false){
					terminateScript('Problém s použitím vstupného súboru',ERR_USING_INPUT_FILE);
				}
			}else{
				$file = fopen($path.'/'.$filename.'.'.$extension, "w+")
					or terminateScript('Problém s použitím vstupného súboru',ERR_USING_INPUT_FILE);
				if(strcmp($extension,'rc') == 0){
					$files[$extension] = '0';
					fwrite($file,0);
				}
				else{
					$files[$extension] = false;
				}
				fclose($file);
			}
		}
				
		return $files;
	}
}

/**
 * Funkcia vypise na stdin HTML kod obsahujuci vysledky testov
 * 
 * @param results obsahuje pole vysledkov testov
 */
function testsOutput($results){ 
$successFull=0;
foreach($results as $test){
	if( $test['result'] == true){
		$successFull++;
	}
}
?>	
<!doctype html>
	<head>
		<title>Projekt IPP - výsledky testov, xocena06</title>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	</head>

	<body style="background: black; color: white; text-align: center; font-family: helvetica,sans-serif;">
		<header style="background: #262626; padding: 10px; margin: 10px; width: fit-content; 
						display: inline-block; border-radius: 10px; box-shadow: 5px 5px 10px 4px rgba(26,26,26,1); ">
			<div >
				<h1>Výsledky testov IPPCode</h1>
				<h2>Táto stránka bola vygenerovaná skriptom test.php</h2>
				<p>Autor: Daniel Miloslav Očenáš</p>
				<p>login: xocena06</p>	
			</div>
		</header>
		<div>
			<table style="margin: 0 auto; background: #262626; text-align:left; border-radius: 10px; padding: 5px; box-shadow: 5px 5px 10px 4px rgba(26,26,26,1);" >
				<tr>
					<td>Počet testov:</td>
					<td><?php echo count($results); ?></td>
					<td style="text-align: center; ">
						<button onclick="showAll()" id="all" style="background-color: white; margin: 10px; border: none; padding: 5px; cursor: pointer; border-radius: 5px;">
							Zobrazit všetky testy
						</button>		
					</td>
				</tr>
				<tr style="color: green">
					<td>Počet úspešných testov</td>
					<td><?php echo $successFull; ?></td>
					<td style="text-align: center; ">
						<button onclick="showPassed()" id="passed" style="background-color: green; margin: 10px; border: none; padding: 5px;cursor: pointer; border-radius: 5px;" >
							Zobrazit úspešné testy
						</button>
					</td>
				</tr>
				<tr style="color: red">
					<td>Počet neúspešných testov:</td>
					<td><?php echo count($results) - $successFull; ?></td>
					<td style="text-align: center; ">
						<button onclick="showNotPassed()" id="not-passed" style="background-color: red; margin: 10px; border: none; padding: 5px;cursor: pointer; border-radius: 5px;" >
							Zobrazit neúspešné testy
						</button>
					</td>
				</tr>
				<tr>
					<td>Percentuálna úspešnosť:</td>
					<td><?php echo round($successFull / count($results) *100,2) ; ?>%</td>
				</tr>
			</table>
		</div>

		<table style="margin: 0 auto; " >
			<tr>
				<th style="border-bottom: 1px solid #1a1a1a; padding: 3px 5px;">
					Názov suboru .src		
				</th>
				<th style="border-bottom: 1px solid #1a1a1a; padding: 3px 5px;">
					Očakávaný výstup testu
				</th>
				<th style="border-bottom: 1px solid #1a1a1a; padding: 3px 5px;">
					Výstup testu
				</th>
				<th style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">
					Očakávaný návratový kód				
				</th>
				<th style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">
					Návratový kód
				</th>
				<th style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">
					Popis
				</th>
			</tr>
<?php

foreach($results as $result){

?>
				<tr 				
				<?php 
				if($result['result'] == true){
					echo "class=\"passed\"";					
				}
				else{
					echo "class=\"notPassed\" ";
				}
				?>
				style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;
				<?php 
				if($result['result'] == true){
					echo "color: green";
				}
				else{
					echo "color: red";
				}?>
				">
				<td  style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">
					<?php echo $result['path']; ?>					
				</td>
				<td  style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">
					<?php echo $result['expectedReturn']; ?>						
				</td>
				<td  style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">
					<?php echo $result['return']; ?>						
				</td>
				<td  style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">	
					<?php echo $result['expectedRetCode']; ?>				
				</td>
				<td  style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">					
					<?php echo $result['retCode']; ?>	
				</td>
				<td  style="border-bottom: 1px solid #1a1a1a; padding: 3px 15px;">					
					<?php echo $result['description']; ?>	
				</td>
			</tr>
<?php

}

?>
		</table>
	</body>
	<script>
		function showAll() {
			
			var x = document.getElementsByClassName("passed");
			for (var i = 0; i < x.length; i++) {
				x[i].style.display = 'table-row';
			}
			var y = document.getElementsByClassName("notPassed");
			for (var i = 0; i < y.length; i++) {
				y[i].style.display = 'table-row';
			}
		}
		function showPassed() {
			var x = document.getElementsByClassName("passed");
			for (var i = 0; i < x.length; i++) {
				x[i].style.display = 'table-row';
			}
			var y = document.getElementsByClassName("notPassed");
			for (var i = 0; i < y.length; i++) {
				y[i].style.display = 'none';
			}
		}
		function showNotPassed() {
			var x = document.getElementsByClassName("passed");
			for (var i = 0; i < x.length; i++) {
				x[i].style.display = 'none';
			}
			var y = document.getElementsByClassName("notPassed");
			for (var i = 0; i < y.length; i++) {
				y[i].style.display = 'table-row';
			}
		}
	</script>
</html> 
<?php
}

?>