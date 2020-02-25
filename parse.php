<?php 
/**
 *	Súbor:	parse.php
 *	Autor:	Daniel Miloslav Očenáš (login:xocena06)
 *	Dátum:	Február 2020
 *	Popis:	Projekt 1 predmetu IPP, VUT FIT 2020.
 *			Skript vykonáva syntaktickú a lexikálnu analýzu
 *			jazyka IPPcode2020, z ktorého jeho vytvára XML reprezentáciu.
 */

define("ERR_INV_SCRIPT_PARAM", 10);
define("ERR_USING_INPUT_FILE", 11);
define("ERR_USING_OUTPUT_FILE", 12);
define("ERR_MISSING_FILE_HEADER", 21);
define("ERR_WRONG_OP_CODE", 22);
define("ERR_LEX_SYNT", 23);

$stats = new Statistics();

checkArgs($stats);

$parser = new Parser($stats);
$generator = new XMLGen();

// Hlavne telo programu, kde su instrukcie spracovavane a po riadkoch
// nacitane zo stdin. Parser vykona syntakticku a lexikalnu analyzu
// a vrati pole s intrukciami a ich argumentmi pre generator XML kodu
while (($parsedLine = $parser->parse()) !== FALSE) {
	if($parsedLine != NULL){
		$generator->genLine($parsedLine);
	}
}

$generator->XMLEnd();

return 0;

/**
 *	Funkcia na kontrolu spravnosti argumentov
 *	V pripade ze je zadany argument --help, vypise napovedu a ukonci skript.
 *	Povoleny len argument --help alebo ziadny argument, inak sa jedna o chybu.
 */
function checkArgs($stats){
	global $argv, $argc;

	if($argc == 1){
		return 0;
	}
	elseif($argc > 1){
		$optsArray = array('--comments','--labels','--jumps','--loc','--help',"parse.php");
		foreach ($argv as $key) {
			if(!((strpos($key, '--stats') !== false ) || in_array($key,$optsArray))){
				fwrite(STDERR, "$key is unsupported script parameter (run script with param --help for more info)");
				exit(ERR_INV_SCRIPT_PARAM);
			}
		}

		$opts = getopt("",["stats::","comments","labels","jumps","loc","help"]);
		if(array_key_exists("stats", $opts) && !array_key_exists("help", $opts)){
			
			$stats->setFileName($opts['stats']);

			if(array_key_exists("comments", $opts)){
				$stats->setComments(1);
			}
			if(array_key_exists("labels", $opts)){
				$stats->setLabels(1);
			}
			if(array_key_exists("jumps", $opts)){
				$stats->setJumps(1);
			}
			if(array_key_exists("loc", $opts)){
				$stats->setLoc(1);
			}
			return 0;
		}
		elseif (array_key_exists("help", $opts) && $argc == 2){
			fwrite(STDOUT, "\nNápoveda\nSúbor:parse.php\nAutor:Daniel Očenáš (xocena06)\nTento skript kontroluje lexikálnu a syntaktickú správnosť\nkódu IPPcode20 a na štandardný výstup vypíše XML reprezentáciu kódu\nZdrojový kód pre tento skript je načítany zo STDIN\n\nPovolene parametre --help, --stats[=filename][--loc|--comments|--jumps|--labels]* \n");
			exit(0);
		}

	}

	terminateScript("Invalid script parameter/s (run script with param --help for more info)\n",ERR_INV_SCRIPT_PARAM);		
}

/**
 *	Funckia na vypis chyboveho vystupu
 *	a ukoncenie programu so predpokladanym chybovym kodom
 */
function terminateScript($errMsg, $errCode){
	fwrite(STDERR, $errMsg);
	exit($errCode);
}

/**
 *	Trieda generujuca vysledny XML dokument
 */
class XMLGen{
	private $xml;

	/**
	 *	Kontstruktor triedy XMLGen
	 */
	public function __construct(){
		$this->xml = new XMLwriter();
		$this->xml->openMemory();
		$this->xml->setIndent(true);
		$this->xml->startDocument( '1.0' , 'UTF-8' );

		$this->xml->startElement('program');
		$this->xml->writeAttribute('language','IPPcode20');
	} 

	/**
	 *	Ukoncenie vygenerovaneho xml dokumentu
	 *	Volane v pripade ze analyza zdrojoveho kodu prebehne uspesne
	 */
	public function XMLEnd(){
		$this->xml->endElement(); // end program
		$this->xml->endDocument();// end document
		echo $this->xml->outputMemory(TRUE); // print xml
	}



	/**
	 *
	 */
	public function genAttribute($elem,$arg){
		$this->xml->startElement($elem);
		$this->xml->writeAttribute('type',$arg['type']);
		$this->xml->text($arg['text']);
		$this->xml->endElement();
	}

	/**
	 *
	 */
	public function genLine($line){
		$this->xml->startElement('instruction');
		$this->xml->writeAttribute('order',$line['insOrder']);
		$this->xml->writeAttribute('opcode',strtoupper($line[0]));



		if (array_key_exists('arg1', $line)) {
			$this->genAttribute('arg1',$line['arg1']);
			if (array_key_exists('arg2', $line)) {
				$this->genAttribute('arg2',$line['arg2']);
				if (array_key_exists('arg3', $line)) {
					$this->genAttribute('arg3',$line['arg1']);				
				}	
			}	
		}


		$this->xml->endElement();
		
	}

}

/**
 *	Trieda vykonavajuca syntakticku a lexikalnu analyzu 
 *	zdrojoveho kodu IPPcode20. 
 *	Vyuziva triedu Statistics, kde pocas behu analyzy zapisuje statistiky
 *	spracovavanych instrukci.
 **/
class Parser{
	private $stats;//odkaz na triedu statistiky
	private $line; //aktualne spracovavany riadok
	private $lineNmr;
	private $insOrder;
	private $argOrder;

	/**
	 *	Konstruktor triedz Parser
	 */
	public function __construct($stats){
		$this->stats = $stats;
		$this->insOrder = 0;
		$this->lineNmr = 0;
		$this->argOrder = 1;
	}

	/**
	 *
	 */
	public function parse(){
		if(feof(STDIN)){
			if($this->insOrder == 0){
				if(strpos(strtoupper($this->line),'.IPPCODE20') === false){
					terminateScript("Missing or incorrect code header.",ERR_MISSING_FILE_HEADER);
				}/*
				else{
					return TRUE;
				}*/
			}
			else {
				return FALSE;
			}
		}
		$this->line = fgets(STDIN);
		$this->lineNmr++;

		$this->removeComments();
		$this->line = trim($this->line);
		$this->removeEmptyLine();

		if(strlen($this->line) == 0){
			return null;
		}

		if($this->insOrder == 0){
			if(strpos(strtoupper($this->line),'.IPPCODE20') === false){
				terminateScript("Missing or incorrect code header.",ERR_MISSING_FILE_HEADER);
			}
			else{
				$this->insOrder++;
				return null;
			}

		}
//		echo 'trimmed decomented :'.$this->line.':'.PHP_EOL;

		$this->line = explode(' ', $this->line);

		$this->argOrder = 1;
		$this->line['argCount'] = count($this->line) - 1;
		$this->line['insOrder'] = $this->insOrder;

		$this->analyzer();

		$this->insOrder++;
		return $this->line;
	}

	/**
	 *
	 */
	private function analyzer(){
		if($this->line['argCount'] < 0 || $this->line['argCount'] > 3){
			terminateScript("Err line $this->lineNmr, Wrong count of operands",ERR_LEX_SYNT);
		}
		strtoupper($this->line[0]);

		switch ($this->line[0]) {
			// OPCODE	
			case 'CREATEFRAME':
			case 'PUSHFRAME':
			case 'POPFRAME':
			case 'BREAK':	
				if($this->line['argCount'] == 0){

				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			// OPCODE <label>
			case 'CALL':
			case 'LABEL':
			case 'JUMP':
				if($this->line['argCount'] == 1){
					if($this->checkLabel($this->line[1])){

					}
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			// OPCODE <symb>
			case 'RETURN':
			case 'PUSHS':
			case 'WRITE':
			case 'EXIT':	
			case 'DPRINT':	
				if($this->line['argCount'] == 1){
					if($this->checkSymb($this->line[1])){
						
					}					
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			// OPCODE <var>
			case 'DEFVAR':
			case 'POPS':
				if($this->line['argCount'] == 1){
					if($this->checkVar($this->line[1])){
						
					}					
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
								
				break;

			// OPCODE <var> <symb>
			case 'MOVE':
			case 'STRLEN':
			case 'TYPE':
			case 'INT2CHAR':
				if($this->line['argCount'] == 2){
					if($this->checkVar($this->line[1]) && $this->checkSymb($this->line[2])){
						
					}					
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			// OPCEDE <var> <type>
			case 'READ':
				if($this->line['argCount'] == 2){
					if($this->checkVar($this->line[1]) && $this->checkType($this->line[2])){
						
					}
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			// OPCODE <var> <symb1> <symb2>
			case 'ADD':
			case 'SUB':
			case 'MUL':
			case 'IDIV':
			case 'LT':
			case 'GH':
			case 'EQ':
			case 'AND':
			case 'OR':
			case 'NOT':
			case 'STRI2INT':
			case 'CONCAT':
			case 'GETCHAR':
			case 'SETCHAR':
				if($this->line['argCount'] == 3){
					if($this->checkVar($this->line[1]) && $this->checkSymb($this->line[2]) && $this->checkSymb($this->line[3])){
						
					}
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			// OPCODE <label> <symb1> <symb2>
			case 'JUMPIFEQ':
			case 'JUMPIFNEQ':
				if($this->line['argCount'] == 3){
					if($this->checkLabel($this->line[1]) && $this->checkSymb($this->line[2]) && $this->checkSymb($this->line[3])){
						
					}
				}
				else{
					terminateScript("Err line $this->lineNmr, Invalid arg count",ERR_LEX_SYNT);
				}
				break;

			default:
				terminateScript('Err line '.$this->lineNmr.', '.$this->line[0].' is unknown instruction',ERR_WRONG_OP_CODE);
				break;
		}
	}

	/**
	 *	Funckia odstranujuca komentare a zapisujuca ich vyskyt do statistik
	 */
	private function removeComments(){
		if(strpos($this->line, '#') !== false){
			$this->stats->incCount('comments');
			$arr = explode('#',$this->line);
			$this->line = $arr[0];
		}
	}

	/**
	 *
	 */
	private function removeEmptyLine(){
		$this->line = preg_replace('/^[ \t]*[\r\n]+/m', '', $this->line);
	}

	/**
	 *
	 */
	private function checkVar($var){
		if (preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[a-zA-Z])(_|-|\$|&|%|\*|!|\?|[a-zA-Z0-9])*$/', $var)) {
        	$this->line[ "arg".$this->argOrder] = array(
        		"type" => "var",
        		"text" => $var
        	);
        	$this->argOrder++;
			return true;
		}
		else{
			terminateScript("Err line $this->lineNmr, $var is not a variable", ERR_LEX_SYNT);
		}
	}

	/**
	 *
	 */
	private function checkType($type){
		if (preg_match('/^(int|bool|string|nil)$/', $type)) {
        	$this->line[ "arg".$this->argOrder] = array(
        		"type" => "type",
        		"text" => $type
        	);
        	$this->argOrder++;
			return true;
		}
		else{
			terminateScript("Err line $this->lineNmr, $type is not a type", ERR_LEX_SYNT);
		}
	}

	/**
	 *
	 */
	private function checkLabel($label){		
		if (preg_match('/^(_|-|\$|&|%|\*|!|\?|[a-zA-Z])(_|-|\$|&|%|\*|!|\?|[a-zA-Z0-9])*$/', $label)){
			$this->stats->incCount('labels');
        	$this->line[ "arg".$this->argOrder] = array(
        		"type" => "label",
        		"text" => $label
        	);
        	$this->argOrder++;
			return true;
		}
		else{
			terminateScript("Err line $this->lineNmr, $label is not a label", ERR_LEX_SYNT);
		}	
	}

	/**
	 *
	 */
	private function checkSymb($symb){
        if (preg_match('/^(int|bool|string|nil)@.*$/', $symb)) {
            $symb = explode('@', $symb, 2);
            if ($symb[0] == "int") { // int
                if ($symb[1] == "") {
                    terminateScript("Err line $this->lineNmr, int value is undefined",ERR_LEX_SYNT);
                }
                else {
                	$this->line[ "arg".$this->argOrder] = array(
                		"type" => "int",
                		"text" => $symb[1]
                	);
                	$this->argOrder++;

                    return true;
                }
            }
            elseif ($symb[0] == "bool") { // bool
                //$symb[1] = strtolower($symb[1]);
                if (preg_match('/^(true|false)$/', $symb[1])) {                	
                	$this->line[ "arg".$this->argOrder] = array(
                		"type" => "bool",
                		"text" => $symb[1]
                	);
                	$this->argOrder++;


                    return true;
                }
                else{
                    terminateScript("Err line $this->lineNmr,". $symb[1] ."is not a valid symbol",ERR_LEX_SYNT);
                }
            }
            else { // string
            	//whitespaces and comments are removed, need to match only string withou \ 
                if (preg_match('/^(\\\\[0-9]{3}|[^\\\\])*$/', $symb[1])) { // TODO ????
                	$this->line[ "arg".$this->argOrder] = array(
                		"type" => "string",
                		"text" => $symb[1]
                	);
                	$this->argOrder++;
                    return true;
                }
                else{
                    terminateScript("Err line $this->lineNmr,". $symb[1] ." is not a valid symbol",ERR_LEX_SYNT);
                }
            }
        }
        elseif (preg_match('/^(LF|TF|GF)@.*$/', $symb)) { // var
            $this->checkVar($symb);
            return true;
        }
		else{
			terminateScript("Err line $this->lineNmr, $symb is not a symbol", ERR_LEX_SYNT);
		}	
	}
}


/**
 *
 */
class Statistics{
	private $outputFile = FALSE;//file to store stats

	private $comments = FALSE;	//comments
	private $loc = FALSE;		//instructions
	private $labels = FALSE;	//labels
	private $jumps = FALSE;		//jumps

	public function setFileName($name){
		$this->outputFile = $name;
	}

	public function setComments($number){
		$this->comments = $number;
	}

	public function setLoc($number){
		$this->loc = $number;
	}

	public function setLabels($number){
		$this->labels = $number;
	}

	public function setJumps($number){
		$this->jumps = $number;
	}

	public function incCount($type){
		switch ($type) {
			case 'comments':
				$this->comments++;
				break;
			case 'loc':
				$this->loc++;
				break;
			case 'labels':
				$this->labels++;
				break;
			case 'jumps':
				$this->jumps++;
				break;
		}
	}

	public function printVals(){
		if($this->comments)
			echo 'comments '.--$this->comments.''.PHP_EOL;
		if($this->loc)
			echo 'loc '.--$this->loc.''.PHP_EOL;
		if($this->labels)
			echo 'labels '.--$this->labels.''.PHP_EOL;
		if($this->jumps)
			echo 'jumps '.--$this->jumps.''.PHP_EOL;
		if($this->outputFile)
			echo "fileName $this->outputFile\n";
	}
}
?>