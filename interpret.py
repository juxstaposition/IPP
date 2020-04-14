#!/usr/bin/env python3

###
#	Súbor:	interpret.py
#	Autor:	Daniel Miloslav Očenáš (login:xocena06)
#	Dátum:	Marec 2020
#	Popis:	Projekt 2 predmetu IPP, VUT FIT 2020.

import sys
import re
import codecs
import os.path as path
import xml.etree.ElementTree as ET 

debug = True


def main():
	""" 
	Hlavne riadenie skriptu interpret.py
	:return: navratovy kod 0, uspesne ukoncenie programu     
	"""
	files = checkArgs()
	# DEBUG print
	debugPrint(files)

	interpret = Interpret(files['source'])
	interpret.start()
	
	sys.exit(0)

class Interpret:
	"""
	Trieda Interprete
	Zabezpecuje riadenie interpretacie
	"""
	def __init__(self,xml):
		"""
		Konstruktor triedy Interpret
		Inicializuje poradie instrukcie na 0, nezapornu hodnotu
		:param xml: odkaz na korenovy element xml suboru
		"""
		self.xml = xml
		self.insOrder = 0
		self.lastInsOrder = 0
		self.FRAME = Frame()

	def start(self):
		"""
		Funkcia vykona kontrolu a interpretaciu zdrojoveho programu
		V pripade vyskytu chyby pouzije triedu Error
		Nacitava zdrojovy xml subor po uzloch(instrukciach), z ktorych vytvara
		instanciu triedy Instruction
		"""
		
		self.checkXMLRoot(self.xml)

		self.FRAME.printFrames()
		
		self.xml = self.xml.findall("./")

		while self.insOrder < len(self.xml):

			child = self.xml[self.insOrder]
			instruction = Instruction(child, self.lastInsOrder, self.FRAME)
			
			self.lastInsOrder = instruction.checkInstruction()
			
			instruction.insIdentifyExecute()
			
			self.insOrder += 1
			
			self.FRAME.printFrames()

				# lastInsOrderChanged = int(self.xml[2].attrib['order'])
				# print(lastInsOrderChanged)
				# self.lastInsOrder = lastInsOrderChanged - 1
				# self.insOrder = 2	
				


	def checkXMLRoot(self,root):
		"""
		Funkcia vykonava kontrolu korenoveho uzlu xml dokumentu
		:param root: korenovy uzol
		"""
		try:

			if(root.tag != 'program'):
				Error(Error.UnexpectedXML,'Nespravny tvar korenoveho uzlu XML dokumentu')
		except:
			Error(Error.InvalidXMLForm,'XML zdroj nieje well formed')
		
		if(len(root.attrib) > 3):
			Error(Error.UnexpectedXML,'Nespravny poces atributov korenoveho uzlu program')
		
		attr = ['language','name','description']
		for x in root.attrib:
			if (x not in attr):
				Error(Error.UnexpectedXML,"Nespravny atribut korenoveho uzlu program: '{0}' ".format(x))
		
		if ( root.attrib['language'].upper() != 'IPPCODE20' ):
			Error(Error.UnexpectedXML,'Nespravna hlavicka programu')

		sortXMLNodeByAttribute(root,'order')
	
def sortXMLNodeByAttribute(parent, attr):
	"""
	Funkcia zoradi potomkov uzlu podla atributu vzostupne
	:param parent: hlavny uzol
	:param attr: atribut podla ktoreho hodnot sa zoraduje
	"""
	if attr == 'order':
		parent[:] = sorted(parent, key=lambda child: int(child.get(attr)))
	else:
		parent[:] = sorted(parent, key=lambda child: child.get(attr))


class Instruction:
	"""
	Trieda instruction
	Vykonava operacie pre instrukcie z xml suboru
	"""
	def __init__(self, instruction, insOrder, FRAME):
		"""
		Kontruktor triedy instruction
		:param instruction: aktualne spracovavany uzol  
		:param insOrder: aktualne poradie instrukcie programu
		"""
		self.instruction = instruction
		self.lastInsOrder = insOrder
		self.FRAME = FRAME

	def checkInstruction(self):
		"""
		Funkcia vykona kontrolu instrukcie
		Ak je instrukcia chybna, pouziva triedu Error
		return poradie aktualne spracovavanej instrukcie
		"""
		# DEBUG print
		debugPrint(self.instruction.tag,end='')
		debugPrint(self.instruction.attrib, end='')
		debugPrint(self.instruction.text)

		if(self.instruction.tag != 'instruction'):
			Error(Error.UnexpectedXML,'Nespravny tvar xml instrukcie')
		
		self.checkInsAtribs()

		newInsOrder = int(self.instruction.attrib['order'])
		if(self.lastInsOrder >= newInsOrder):
			Error(Error.UnexpectedXML,'Nespravne poradie instrukcie')
			
		return newInsOrder

	def checkInsAtribs(self):
		"""
		Funkcia vykona lex kontrolu argumentov instrukcie
		Ak su argumenty chybne, pouziva triedu Error
		"""
		if(len(self.instruction.attrib) != 2):
			Error(Error.UnexpectedXML,'Nespravny poces atributov instrukcie')
		attr = ['opcode','order']
		for x in self.instruction.attrib:
			if (x not in attr):
				Error(Error.UnexpectedXML,"Nespravny atribut instrukcie: '{0}' ".format(x))

	def checkArgsCount(self,argcCount):
		"""
		Funkcia vykona syntakticku a lex kontrolu argumentov instrukcie
		a vrati ich hodnotu
		:param argcCount: ocakavany pocet argumentov instrukcie
		"""
		if (len(list(self.instruction)) != argcCount):
			Error(Error.UnexpectedXML,"Nespravny pocet argumentov instrukcie: '{0}' ".format(self.instruction.attrib['opcode']))
		if (argcCount > 0):
			argValues = []
			self.instruction[:] = sorted(self.instruction,key=lambda child: child.tag )
			args = ['arg1','arg2','arg3']
			x = 0
			for child in self.instruction:
				if( child.tag != args[x] or len(child.attrib) != 1 or 'type' not in child.attrib):
					Error(Error.UnexpectedXML,"Nespravny tvar argumentov instrukcie: '{0}' ".format(self.instruction.attrib['opcode']))
				
				argValues.append({
					'type': child.attrib['type'],
					'value': child.text 
				})
				x += 1

			# DEBUG print
			debugPrint(argValues)
			return argValues

		
	def arithmeticInstruction(self,args,operation):
		"""
		Vykona artimeticku operaciu zadanu parametrom operation a vysledok ulozi do var
		:param args: operandy instrukcie v poradi <var> <symb> <symb>
		:param operation: aritmeticka operacia
		"""	
		arg1 = Symb(args[1]['type'], args[1]['value'])
		arg1Value = arg1.checkSymb()

		arg2 = Symb(args[2]['type'], args[2]['value'])
		arg2Value = arg2.checkSymb()

		if(arg1Value['type'] == 'var'):
			arg1Value = self.FRAME.getVar(arg1Value['value'])

		if(arg2Value['type'] == 'var'):
			arg2Value = self.FRAME.getVar(arg2Value['value'])

		if arg1Value['type'] != 'int' or arg2Value['type'] != 'int':
			Error(Error.WrongOPType,'Aritmeticky operator nieje typu int ')

		var1 = Var(args[0]['type'], args[0]['value'])
		var1.checkVar()

		result =  {'type':'int'}
		if(operation == 'ADD'):
			result['value'] = arg1Value['value'] + arg2Value['value']
		if(operation == 'SUB'):
			result['value'] = arg1Value['value'] - arg2Value['value']
		if(operation == 'MUL'):
			result['value'] = arg1Value['value'] * arg2Value['value']
		if(operation == 'IDIV'):
			if arg2Value['value'] == 0:
				Error(Error.WrongOpValue,('Delenie nulou'))
			result['value'] = arg1Value['value'] // arg2Value['value']

		self.FRAME.setVar(args[0]['value'],result)

	def insIdentifyExecute(self):
		"""
		Identifikacia instrukcie a vykonanie jej prislusnych operacii 
		"""

		opCode = self.instruction.attrib['opcode'].upper()

		# Tvar Instrukcie: OPCODE
		# Instrukcia CREATEFRAME
		if (opCode == 'CREATEFRAME'):
			self.checkArgsCount(0)
			self.FRAME.createFrame()

		# Instrukcia PUSHFRAME
		elif (opCode == 'PUSHFRAME'):
			self.checkArgsCount(0)
			self.FRAME.pushFrame()

		# Instrukcia POPFRAME
		elif (opCode == 'POPFRAME'):
			self.checkArgsCount(0)
			self.FRAME.popFrame()
		
		# Instrukcia BREAK
		elif (opCode == 'BREAK'):
			self.checkArgsCount(0)
			print('Ladiaci výpis inštrukcie break', file=sys.stderr)


		# Tvar Instrukcie: OPCODE <label>
		# TODO Instrukcia JUMP
		elif (opCode == 'JUMP'):
			args = self.checkArgsCount(1)

		# TODO Instrukcia CALL
		elif (opCode == 'CALL'):
			args = self.checkArgsCount(1)

		# TODO Instrukcia Label
		elif (opCode == 'LABEL'):
			args = self.checkArgsCount(1)

	
		# Tvar Instrukcie: OPCODE <symb>
		# TODO Instrukcia RETURN
		elif (opCode == 'RETURN'):
			args = self.checkArgsCount(1)

		# Instrukcia PUSHS
		elif (opCode == 'PUSHS'):
			args = self.checkArgsCount(1)

			arg1 = Symb(args[0]['type'], args[0]['value'])
			arg1Value = arg1.checkSymb()

			if arg1Value['type'] == 'var':
				arg1Value = self.FRAME.getVar(arg1Value['value'])

			self.FRAME.dataStack.push(arg1Value)

		# Instrukcia Write
		elif (opCode == 'WRITE'):
			args = self.checkArgsCount(1)
			
			argSymb = Symb(args[0]['type'], args[0]['value'])
			symbValue = argSymb.checkSymb()

			debugPrint(symbValue)
			
			toWrite = symbValue['value']

			if symbValue['type'] == 'nil':
				toWrite = ''
			elif symbValue['type'] == 'bool':
				if symbValue['value']:
					toWrite = 'true'
				else:
					toWrite = 'false'
			elif symbValue['type'] == 'var':
				varToWrite = self.FRAME.getVar(symbValue['value'])
				toWrite = varToWrite['value']
			# DEBUG print	
			debugPrint('WRITE INS:', end='')
			print(toWrite, end='')
			debugPrint('')


		# Instrukcia EXIT
		elif (opCode == 'EXIT'):
			args = self.checkArgsCount(1)

			arg1 = Symb(args[0]['type'], args[0]['value'])
			arg1Value = arg1.checkSymb()

			if arg1Value['type'] != 'int' or arg1Value['value'] < 0 or arg1Value['value'] > 49 :
				Error(Error.WrongOpValue,'Hodnota symb instrukcie EXIT je mimo interval 0 - 49' )
			
			sys.exit(arg1Value['value'])


		# Instrukcia DPRINT
		elif (opCode == 'DPRINT'):
			args = self.checkArgsCount(1)
			
			arg1 = Symb(args[0]['type'], args[0]['value'])
			arg1Value = arg1.checkSymb()

			if arg1Value['type'] == 'var':
				arg1Value = self.FRAME.getVar(arg1Value['value'])
		
			print(arg1Value['value'], file=sys.stderr)

		# Tvar Instrukcie: OPCODE <var>
		# Instrukcia DEFVAR
		elif (opCode == 'DEFVAR'):
			args = self.checkArgsCount(1)
		
			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()

			self.FRAME.defVar(args[0]['value'])

		# Instrukcia POPS
		elif (opCode == 'POPS'):
			args = self.checkArgsCount(1)

			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()

			newVarValue = self.FRAME.dataStack.pop()
			self.FRAME.setVar(args[0]['value'],newVarValue)
		
		# Tvar Instrukcie: OPCODE <var> <symb>
		# Instrukcia MOVE
		elif (opCode == 'MOVE'):
			args = self.checkArgsCount(2)

			debugPrint('Move:')
			arg2 = Symb(args[1]['type'], args[1]['value'])
			arg2Value = arg2.checkSymb()

			if arg2Value['type'] == 'var':
				arg2Value = self.FRAME.getVar(arg2Value['value'])
			
			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()
			
			# nazov premennej (GF@ex), {'type': type, 'value': value}
			self.FRAME.setVar(args[0]['value'], arg2Value)

		# TODO Instrukcia STRLEN
		elif (opCode == 'STRLEN'):
			args = self.checkArgsCount(2)

		# TODO Instrukcia TYPE
		elif (opCode == 'TYPE'):
			args = self.checkArgsCount(2)

		# TODO Instrukcia INT2CHAR
		elif (opCode == 'INT2CHAR'):
			args = self.checkArgsCount(2)


		# Tvar Instrukcie: OPCODE <var> <type>

		# TODO Instrukcia Read
		elif (opCode == 'READ'):
			args = self.checkArgsCount(2)


		# Tvar Instrukcie: OPCODE <var> <symb1> <symb2>
		# Instrukcia ADD TEST
		elif (opCode == 'ADD'):
			args = self.checkArgsCount(3)
			self.arithmeticInstruction(args,opCode)

		# Instrukcia SUB TEST
		elif (opCode == 'SUB'):
			args = self.checkArgsCount(3)
			self.arithmeticInstruction(args,opCode)
			
		# Instrukcia MUL TEST
		elif (opCode == 'MUL'):
			args = self.checkArgsCount(3)
			self.arithmeticInstruction(args,opCode)
			
		# Instrukcia IDIV TEST
		elif (opCode == 'IDIV'):
			args = self.checkArgsCount(3)
			self.arithmeticInstruction(args,opCode)
			
		# TODO Instrukcia LT
		elif (opCode == 'LT'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia GT
		elif (opCode == 'GT'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia EQ
		elif (opCode == 'EQ'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia AND
		elif (opCode == 'AND'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia OR
		elif (opCode == 'OR'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia NOT
		elif (opCode == 'NOT'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia STRI2INT
		elif (opCode == 'STRI2INT'):
			args = self.checkArgsCount(3)
			
		# Instrukcia CONCAT TEST
		elif (opCode == 'CONCAT'):
			args = self.checkArgsCount(3)
			
			arg1 = Symb(args[1]['type'], args[1]['value'])
			arg1Value = arg1.checkSymb()

			arg2 = Symb(args[2]['type'], args[2]['value'])
			arg2Value = arg2.checkSymb()

			if(arg1Value['type'] == 'var'):
				arg1Value = self.FRAME.getVar(arg1Value['value'])

			if(arg2Value['type'] == 'var'):
				arg2Value = self.FRAME.getVar(arg2Value['value'])

			if arg1Value['type'] != 'string' or arg2Value['type'] != 'string':
				Error(Error.WrongOPType,'Retazcovy operator nieje typu string')

			var1 = Var(args[0]['type'], args[0]['value'])
			var1.checkVar()

			result = {'type':'string', 'value': arg1Value['value'] + arg2Value['value'] }

			self.FRAME.setVar( args[0]['value'], result )
			
		# TODO Instrukcia GETCHAR
		elif (opCode == 'GETCHAR'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia SETCHAR
		elif (opCode == 'SETCHAR'):
			args = self.checkArgsCount(3)


		# Tvar Instrukcie: OPCODE <label> <symb1> <symb2>
		# TODO Instrukcia JUMPIFQE
		elif (opCode == 'JUMPIFEQ'):
			args = self.checkArgsCount(3)
			
		# TODO Instrukcia JUMPIFNEQ
		elif (opCode == 'JUMPIFNEQ'):
			args = self.checkArgsCount(3)
		else:
			Error(Error.UnexpectedXML,"Neznamy operacny kod: '{0}' ".format(opCode))
	


class Var:
	"""
	Trieda var, vyuzita pre kontrolu hodnoty typu var
	"""
	def __init__(self,varType,fullName):
		"""
		Konstruktor triedy VAR
		"""
		self.varType = varType
		self.fullName = fullName

	def checkVar(self):
		"""
		Skontroluj platnost premennej
		Ak najde chybu, vrati chybovy navratovy kod
		"""
		if self.varType != 'var':
			Error(Error.WrongOPType,"Typ premennej nieje 'var' '{0}'".format(self.varType))

		if re.match(r'^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', self.fullName):
			pass
		else:
			Error(Error.UnexpectedXML,"Neplatny tvar premennej '{0}'".format(self.fullName))



class Symb:
	"""
	Trieda Symb sluzi na syntakticku kontrolu konstant
	pripade pouziva triedu var pre kontrolu premennych
	Zaroven vykonava upravu konstanty do struktury spracovatelnej interpetom
	"""
	def __init__(self,typeSymb,value):
		"""
		Konstruktor triedy Symb
		Inicializuje nazov a hodnotu z argumentu
		Pred pouzitim metor je nutne triedu inicializovat
		:param typeSymb: typ argumentu instrukcie
		:param value: hodnota argumentu instrukcie
		"""
		self.typeSymb = typeSymb
		self.value = value

	def checkSymb(self):
		"""
		Skontroluj platnost konstanty a v pripade typu var pouzije triedu var
		Ak najde chybu, vrati chybovy navratovy kod
		"""
		#kontrola celeho cisla
		if self.typeSymb == 'int':
			try:
				self.value = int(self.value)
			except:
				Error(Error.UnexpectedXML,"Retazec {0} typu int, nema spravny format".format(self.value))
		
		# kontrola retazca
		elif self.typeSymb == 'string':

			if self.value is None:
				self.value = ''
			elif re.search(r"(?!\\[0-9]{3})[\\|\s|#]", self.value):
				Error(Error.UnexpectedXML,"Retazec {0} typu string, nema spravny format".format(self.value))
			else:
				regExpEscape = re.compile(r'(\\[0-9]{3})', re.UNICODE)
				
				parts = regExpEscape.split(self.value)
				concat = []
				for part in parts:
					if regExpEscape.match(part):
						part = str(chr(int(part[1:]))) 
					concat.append(part)
				self.value = ''.join(concat)
				

		# kontrola bool
		elif self.typeSymb == 'bool':
			if self.value != 'true' or self.value != 'false':
				Error(Error.UnexpectedXML,"Retazec {0} typu bool, nema spravny format".format(self.value))
			
			if self.value == 'true':
				self.value = True
			else:
				self.value = False

		# kontrola premennej pomocou samostatej triedy
		elif self.typeSymb == 'var':
			typeVar = Var(self.typeSymb, self.value)
			typeVar.checkVar()

		elif self.typeSymb == 'nil':
			if self.value != 'nil':
				Error(Error.UnexpectedXML,"Hodnota typu nil: '{0}' je rozna od nil".format(self.value))
		
		# kod operandu je nevyhovujuci
		else:
			Error(Error.WrongOPType,"Neplatny typ operandu")

		return {'type': self.typeSymb,'value': self.value}
			
class Label:
	"""
	"""
	def __init__(self):
		pass

class Frame:
	"""
	Trieda Frame. Obsahuje referenciu na Global, Local a Temp frame
	Frames su pouzivane na ukladanie premennych. Pre tuto ulohu skript vyuziva
	python slovnik kam su ulozene v tvare 'identifikator':hodnota
	"""
	def __init__(self):
		"""
		Frame konstruktor
		"""
		self.globalFrame = {}
		self.localFrame = []
		self.tempFrame = None
		self.dataStack = Stack()

	def detectFrame(self,var):
		"""
		Funkcia zistujuca ramec premennej
		return ramec pre kt. je premenna urcena
		:param var: cely nazov premennej
		"""
		if var[0:2] == 'GF':
			return self.globalFrame
		elif var[0:2] == 'LF':
			return self.localFrame
		else:
			return self.tempFrame		

	def getVar(self,varName):
		"""
		Funkcia sluzi na vyhladanie premennej v ramcoch.
		Ak premenna neexistuje funkcia vyvola chybu s prislusnym chybovym kodom
		Ak premenna existuje jej hodnota je navratena
		:param varName: nazov premennej
		"""
		#DEBUG print
		debugPrint('FRAME .getVar name:', end='')
		debugPrint(varName)
		
		varFrame, name = varName.split('@')

		# navrat premennej z globalneho ramca	
		if(varFrame == 'GF'):
			try:
				if self.globalFrame[name]['value'] is None:
					Error(Error.MissingValue, "Premennej {0} nebola pridelena hodnota".format(name))
		
				return self.globalFrame[name]
			except KeyError:
				Error(Error.NotExistingVariable, "Premenna {0} nieje definovana".format(name))
		
		# navrat premennej z lokalneho ramca	
		#TODO lf a tf
		elif(varFrame == 'LF'):
			if not any(n['name'] == name for n in self.localFrame):
				Error(Error.NotExistingVariable, "Premenna {0} nieje definovana".format(name))
			
			#return self.globalFrame[name]

		# navrat premennej z docasneho ramca
		elif(varFrame == 'TF'):
			if self.tempFrame[name] is None:
				Error(Error.NotExistingVariable, "Premenna {0} nieje definovana".format(name))
			
			#return self.globalFrame[name]
		
		#extra lex kontrola ramcu
		else:
			Error(Error.UnexpectedXML, "Neplatny nazov ramcu {0} pri var:{1}".format(varFrame,varName))
			
	def defVar(self,varName):
		"""
		Zisti ramec premennej a ak v ramci neexistuje premenna
		inicializuje ju podla mena na prazdne hodnoty
		:param varName: cely nazov premennej
		"""
		varFrame, name = varName.split('@')
		
		currentFrame = self.detectFrame(varName)
		if currentFrame is None:
			Error(Error.NotExistingFrame,"DEFVAR error, ramec {0} neexistuje".format(varFrame))
		elif name in currentFrame:
			Error(Error.SemanticErr,"DEFVAR error, premenna {0} uz v ramci {1} existuje".format(name,varFrame))
		else:
			currentFrame[name] = {'type':None, 'value': None}

	def setVar(self, varIdf, newValue):
		"""
		Nastavi novu hodnotu newValue pre identifikator varIdf
		:param varIdf: identifikator premennej
		:param newValue: nova hodnota premennej
		"""
		workFrame = self.detectFrame(varIdf)
		name = varIdf.split('@',1)[1]
		try:
			if name in workFrame:
				workFrame[name] = newValue
		except:
			Error(Error.NotExistingVariable,"Move error, premenna {0} nebola definovana".format(varIdf))
			
	def createFrame(self):
		"""
		CreateFrame Instrukcia
		"""
		self.tempFrame = {}

	def pushFrame(self):
		"""
		Push Frame Instrukcia
		Prida TF na LF ak TF nieje prazdny
		"""
		if(self.tempFrame is None):
			Error(Error.NotExistingFrame, "Pokus o pristup k nedefinovanemu ramcu")

		self.localFrame.append(self.tempFrame)
		self.tempFrame = None

	def popFrame(self):
		"""
		Pop Frame Instrukcia
		Presunie poslednu hodnotu z lokalneho ramca na 
		"""
		try:
			#TODO check if empty defined frame can be poped without error
			self.tempFrame = self.localFrame[-1]
		except:
			Error(Error.NotExistingFrame, "Pokus o presun prazdneho localneho ramcu")
		
		self.localFrame.pop()
	
			
	# DEBUG print
	def printFrames(self):
		"""
		Vypis ramcov pre debug
		"""
		self.dataStack.stackPrint()
		debugPrint('GF:', end='')
		debugPrint(self.globalFrame)
		debugPrint('LF:', end='')
		debugPrint(self.localFrame)
		debugPrint('TF:', end='')
		debugPrint(self.tempFrame)

class Stack:
	"""
	Trieda Stack vytvorena pre pracu s datovym zasobnikom
	Trieda pomaha ukoncit program s prislusnym navratovym kodom v pripade ze sa vykona
	nepodporovana operacia
	"""
	def __init__(self):
		"""
		Konstruktor triedy Stack, Vytvori premennu typu list pre ukladanie hodnot
		"""
		self.stackContent = []
		
	def pop(self):
		"""
		Ak Zasobnik nieje prazdny tak z neho vyberie hodnotu 
		return vrchol stacku
		"""
		if len(self.stackContent) == 0:
			Error(Error.MissingValue, "Operacia pop nad prazdnym zasobnikom")

		return self.stackContent.pop()
		
	def push(self, value):
		"""
		Ulozi hodnotu na stack
		:param value: hodnota ukladana na stack
		"""
		self.stackContent.append(value)

	# DEBUG print
	def stackPrint(self):
		"""
		Pomocna funkcia, vypise obsah stacku
		"""
		debugPrint('STACK', end='')
		debugPrint(self.stackContent)

class Error:
	"""
	Trieda error je pouzita pre ukoncenie programu s chybovym
	navratovym kodom
	Uchovava zoznam chybovych navratovych kodov s ich odpovedajucou hodnotou
	"""
	def __init__(self,code, msg):
		"""
		Kontruktor triedy Error
		Ak je inicializovana instancia triedy, program ziada o ukoncenie behu
		so zadanym chybovym navratovym kodom
		Vypise chybovu hlasku na stderr
		:param code: chybovy navratovy kod
		:param code: chybova hlaska
		"""
		print(msg, file=sys.stderr)
		sys.exit(code)

	# chybny/nepodporovany parameter skriptu
	WrongScriptParam = 10

	# problem s pouzitim vstupneho suboru
	ErrorHandlingInputFile = 11

	# problem s pouzitim vystupneho suboru
	ErrorHandlingOutputFile = 12
	
	# chybny XML format vo vstupnom soubore
	InvalidXMLForm = 31 		
	
	# neocakavana struktura XML, lex synt err, neznamy op code, zly string
	UnexpectedXML = 32 			
	
	# chyba pri semantickych kontrolach vstupneho kodu v IPPcode20
	# pouzitie nedefinovaneho navestia, redefinice promennej
	SemanticErr = 52 			
	
	# chybne typy operandov
	WrongOPType = 53 			
	
	# pristup k neexistujucej promennej (ramec existuje);
	NotExistingVariable = 54	
	
	# ramec neexistuje
	NotExistingFrame = 55		
	
	# chybajuca hodnota (v promennej, na datovom zasobniku,  v zasobniku volani)
	MissingValue = 56			
	
	# chybna hodnota operandu (dělení nulou, chybna navratova hodnota instrukcie EXIT)
	WrongOpValue = 57			
	
	# chybna praca s retazcom.
	InvalidFrameOperation = 58	



def checkArgs():
	"""
	Funkcia kontroluje argumenty programu
	V prípade nekorektnej formy použije triedu Error
	"""
	userHelp = """
	Skript Interpret.py
	Autor: Daniel Ocenas, (xocena06)
	Popis: Skript vykonava interpretaciu XML suboru
	generovaneho zo zdrojoveho kodu	IPPCODE20.
	Aspon jeden z parametrov --source/--input musi byt zadany,
	ak jeden z nich chyba, tak su odpovedajuce data nacitane zo STDIN
	"""
	# kontrola argumentu help
	args = sys.argv[1:]
	if('--help' in args and len(args) == 1):
		print(userHelp)
		sys.exit(0)

	validArgs = ['--source=','--input=']
	match = {}
	for item in args:
		for validArg in validArgs:
			if item.startswith(validArg):
				match[validArg[2:-1]] = item[len(validArg):]
		
	# kontrola platnosti argumentov a nazvu suboru
	if(len(match) == 2 and len(args) == 2 and len(match['source']) > 0 and len(match['input']) > 0 ):
		checkFile(match['source'])
		checkFile(match['input'])
		
		filePtr = codecs.open(match['source'], "r", "utf-8")
		try:
			tree = ET.parse(filePtr)
			match['source'] = tree.getroot()		
		except:
			Error(Error.InvalidXMLForm,'XML zdroj nieje well formed')
		filePtr.close()

		sys.stdin = open(match['input'])

	elif(len(args) == 1 and 'source' in match and len(match['source']) > 0 ):
		checkFile(match['source'])

		filePtr = codecs.open(match['source'], "r", "utf-8")
		try:
			tree = ET.parse(filePtr)
			match['source'] = tree.getroot()
		except:
			Error(Error.InvalidXMLForm,'XML zdroj nieje well formed')
		filePtr.close()

	elif(len(args) == 1 and 'input' in match and len(match['input']) > 0):
		checkFile(match['input'])
		treeText = sys.stdin.readlines()
		sys.stdin = open(match['input'])

		try:
			match['source'] = ET.fromstring(''.join(treeText))
		except:
			Error(Error.InvalidXMLForm,'XML zdroj nieje well formed')
	
	else:
		Error(Error.WrongScriptParam,"Neplatna kombinacia parametrov")

	return match


def checkFile(fileName):
	"""
	Funkcia skontroluje existenciu suboru zadanym parametrom fileName
	:param fileName: nazov suboru
	"""
	if not path.isfile(fileName):
		Error(Error.ErrorHandlingInputFile, "'{0}' nie je validny subor".format(fileName))

def debugPrint(text,**kwargs):
	"""
	Pomocna funkcia pouzita na vypis riadenia programu
	reaguje na globalnu premennu debug
	ak debug = true, funkcia vypisuje riadenie programu na stdout
	"""
	if debug:
		ending = '\n'
		if kwargs.get('end',None) is not None:
			ending = kwargs.get('end',None)
		print(text, end=ending)

main()
