#!/usr/bin/env python3

###
#	Súbor:	interpret.py
#	Autor:	Daniel Miloslav Ocenas, login:xocena06
#	Dátum:	April 2020
#	Popis:	Projekt 2 predmetu IPP, VUT FIT 2020.

import sys
import re
import codecs
import os.path as path
import xml.etree.ElementTree as ET 

debug = False


def main():
	""" 
	Hlavne riadenie skriptu interpret.py
	:return: navratovy kod 0, uspesne ukoncenie programu     
	"""
	files = checkArgs()

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
		self.FRAME = Frame()
		self.Labels = Label()

	def start(self):
		"""
		Funkcia vykona kontrolu a interpretaciu zdrojoveho programu
		V pripade vyskytu chyby pouzije triedu Error
		Nacitava zdrojovy xml subor po uzloch(instrukciach), z ktorych vytvara
		instanciu triedy Instruction
		"""
		
		self.checkXMLRoot(self.xml)
		
		self.xml = self.xml.findall("./")

		self.Labels.setLabels(self.xml)


		while self.insOrder < len(self.xml):

			child = self.xml[self.insOrder]
			instruction = Instruction(child, self.FRAME)
			
			instruction.checkInstruction()
			
			instruction.insIdentifyExecute()
			
			if instruction.makeJump is False:
				self.insOrder += 1
			else:
				self.insOrder = self.Labels.jump(instruction.makeJump)

			# debug print			
			self.FRAME.printFrames()

				


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
	def __init__(self, instruction, FRAME):
		"""
		Kontruktor triedy instruction
		:param instruction: aktualne spracovavany uzol  
		:param insOrder: aktualne poradie instrukcie programu
		"""
		self.instruction = instruction
		self.FRAME = FRAME
		self.makeJump = False

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
		:return: pole spracovanych argumentov obsahujuce hodnoty argumentu
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

	def checkVarSymbSymb(self,args):
		"""
		Pomocna funkcia pre kontrolu instrukcie s argumentmi <var> <symb1> <symb2>
		:param args: pole argumentov
		:return: list aktualna hodnot <symb1> a <symb2>
		"""
		var1 = Var(args[0]['type'], args[0]['value'])
		var1.checkVar()
		arg1 = Symb(args[1]['type'], args[1]['value'])
		arg1Value = arg1.checkSymb()
		arg2 = Symb(args[2]['type'], args[2]['value'])
		arg2Value = arg2.checkSymb()
		if(arg1Value['type'] == 'var'):
			arg1Value = self.FRAME.getVar(arg1Value['value'])
		if(arg2Value['type'] == 'var'):
			arg2Value = self.FRAME.getVar(arg2Value['value'])

		return arg1Value , arg2Value

	def arithmeticInstruction(self,operation):
		"""
		Vykona artimeticku operaciu zadanu parametrom operation a vysledok ulozi do arg1 <var>
		:param operation: operacny kod aritmetickej operacie
		"""			
		args = self.checkArgsCount(3)

		#nacitanie hodnot
		arg1Value , arg2Value = self.checkVarSymbSymb(args)

		#obmedzenia typov
		if arg1Value['type'] != 'int' or arg2Value['type'] != 'int':
			Error(Error.WrongOPType,'Aritmeticky operator nieje typu int ')

		#logika instrukcii
		result =  {'type':'int'}
		if(operation == 'ADD'):
			result['value'] = arg1Value['value'] + arg2Value['value']
		elif(operation == 'SUB'):
			result['value'] = arg1Value['value'] - arg2Value['value']
		elif(operation == 'MUL'):
			result['value'] = arg1Value['value'] * arg2Value['value']
		elif(operation == 'IDIV'):
			if arg2Value['value'] == 0:
				Error(Error.WrongOpValue,'Delenie nulou')
			result['value'] = arg1Value['value'] // arg2Value['value']

		self.FRAME.setVar(args[0]['value'],result)

	def relationInstruction(self,operation):
		"""
		Vykona relacnu operaciu zadanu parametrom operation a vysledok ulozi do arg1 <var>
		:param operation: operacny kod relacnej operacie
		"""			
		args = self.checkArgsCount(3)

		#nacitanie hodnot
		arg1Value , arg2Value = self.checkVarSymbSymb(args)
		

		#obmedzenia typov
		if operation == 'EQ':
			if arg1Value['type'] != arg2Value['type'] and not ( arg1Value['type'] != 'nil' or arg2Value['type'] != 'nil' ) :
				Error(Error.WrongOPType,'EQ operator nieje spravneho typu ')
		else:
			if arg2Value['type'] == 'nil' or arg1Value['type'] == 'nil':
				Error(Error.WrongOPType,'LT/GT operator nieje spravneho typu ')
			if arg1Value['type'] != arg2Value['type'] :
				Error(Error.WrongOPType,'LT/GT operator nieje spravneho typu ')

		#logika instrukcii
		result =  {'type':'bool'}
		if(operation == 'LT'):
			result['value'] = arg1Value['value'] < arg2Value['value']
		elif(operation == 'GT'):
			result['value'] = arg1Value['value'] > arg2Value['value']
		elif(operation == 'EQ'):
			result['value'] = arg1Value['value'] = arg2Value['value']

		self.FRAME.setVar(args[0]['value'],result)

	
	def logicInstruction(self,args, operation):
		"""
		Vykona logicku operaciu zadanu parametrom operation a vysledok ulozi do arg1 <var>
		:param operation: operacny kod logickej operacie
		:param args: argumenty instrukcie
		"""		
		#nacitanie hodnot
		var1 = Var(args[0]['type'], args[0]['value'])
		var1.checkVar()
		arg1 = Symb(args[1]['type'], args[1]['value'])
		arg1Value = arg1.checkSymb()
		if(arg1Value['type'] == 'var'):
			arg1Value = self.FRAME.getVar(arg1Value['value'])

		#obmedzenia typov
		if operation != 'NOT':
			if(arg2Value['type'] == 'var'):
				arg2Value = self.FRAME.getVar(arg2Value['value'])
			arg2 = Symb(args[2]['type'], args[2]['value'])
			arg2Value = arg2.checkSymb()
			
			if arg2Value['type'] != 'bool':
				Error(Error.WrongOPType,'Logicky operator nieje typu bool ')

		if arg1Value['type'] != 'bool':
			Error(Error.WrongOPType,'Logicky operator nieje typu bool ')

		#logika instrukcie
		result =  {'type':'bool'}
		if(operation == 'AND'):
			result['value'] = arg1Value['value'] and arg2Value['value']
		elif(operation == 'OR'):
			result['value'] = arg1Value['value'] or arg2Value['value']
		elif(operation == 'NOT'):
			result['value'] = not arg1Value['value']
		
		self.FRAME.setVar(args[0]['value'],result)


	def conditionalJump(self,jumpType):
		"""
		Vykona skok ak je splnena skokova podmienka
		:param jumpType: operacny kod instrukcie JUMPIFEQ / JUMPIFNEQ
		"""
		args = self.checkArgsCount(3)

		#nacitanie hodnot
		if args[0]['type'] != 'label':
			Error(Error.WrongOPType,"{0}, arg1 type != 'label'. Chybny typ operandu".format(jumpType))
		arg1 = Symb(args[1]['type'], args[1]['value'])
		arg1Value = arg1.checkSymb()
		arg2 = Symb(args[2]['type'], args[2]['value'])
		arg2Value = arg2.checkSymb()
		if(arg1Value['type'] == 'var'):
			arg1Value = self.FRAME.getVar(arg1Value['value'])
		if(arg2Value['type'] == 'var'):
			arg2Value = self.FRAME.getVar(arg2Value['value'])

		#obmedzenia typov
		if arg1Value['type'] != arg2Value['type'] and not ( arg1Value['type'] != 'nil' or arg2Value['type'] != 'nil' ) :
			Error(Error.WrongOPType,"Nespravna kombinacia typov <symb> podmieneneho skoku")

		#logika instrukcie
		if jumpType == 'JUMPIFEQ':
			if arg1Value['value'] == arg2Value['value']:
				self.makeJump = args[0]['value']
				debugPrint('JUMPIFEQ executed')
		else:
			if arg1Value['value'] != arg2Value['value']:
				self.makeJump = args[0]['value']
				debugPrint('JUMPIFNEQ executed')
			

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
		# Instrukcia JUMP
		elif (opCode == 'JUMP'):
			args = self.checkArgsCount(1)
			if args[0]['type'] != 'label':
				Error(Error.WrongOPType,"Hodnota parameteru type argumentu instrukciu JUMP sa nezhoduje s typom label")

			self.makeJump = args[0]['value']

		# TODO Instrukcia CALL
		elif (opCode == 'CALL'):
			args = self.checkArgsCount(1)

		# Instrukcia Label
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

		# Instrukcia WRITE
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
			
			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()
			arg2 = Symb(args[1]['type'], args[1]['value'])
			arg2Value = arg2.checkSymb()
			if arg2Value['type'] == 'var':
				arg2Value = self.FRAME.getVar(arg2Value['value'])
			
			# nazov premennej (GF@ex), {'type': type, 'value': value}
			self.FRAME.setVar(args[0]['value'], arg2Value)

		# Instrukcia STRLEN
		elif (opCode == 'STRLEN'):
			args = self.checkArgsCount(2)

			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()
			arg2 = Symb(args[1]['type'], args[1]['value'])
			arg2Value = arg2.checkSymb()
			if arg2Value['type'] == 'var':
				arg2Value = self.FRAME.getVar(arg2Value['value'])

			strLenValue = {'type':'int','value': len(arg2Value['value']) }

			self.FRAME.setVar(args[0]['value'], strLenValue)


		# Instrukcia TYPE
		elif (opCode == 'TYPE'):
			args = self.checkArgsCount(2)
			
			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()
			arg2 = Symb(args[1]['type'], args[1]['value'])
			arg2Value = arg2.checkSymb()
			if arg2Value['type'] == 'var':
				arg2Value = self.FRAME.getVar(arg2Value['value'],all=True)

			myType = { 'type':'string','value':'' }
	
			# identifikovanie typu symbolu
			if arg2Value['type'] is not None:
				myType['value'] = arg2Value['type']

			self.FRAME.setVar(args[0]['value'], myType)


		# Instrukcia INT2CHAR TEST
		elif (opCode == 'INT2CHAR'):
			args = self.checkArgsCount(2)			

			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()
			arg2 = Symb(args[1]['type'], args[1]['value'])
			arg2Value = arg2.checkSymb()
			if arg2Value['type'] == 'var':
				arg2Value = self.FRAME.getVar(arg2Value['value'])

			# povoleny len typ int
			if arg2Value['type'] == 'int':
				try:
					arg2Value['value'] = chr(arg2Value['value'])
					arg2Value['type'] = 'string'
				except:
	 				Error(Error.InvalidCharOperation,"hodnota mimo rozsah platnosti chr()")
			else:
				Error(Error.WrongOPType,"INT2CHAR arg2 type != int")

			self.FRAME.setVar(args[0]['value'], arg2Value)


		# Tvar Instrukcie: OPCODE <var> <type>
		# Instrukcia Read
		elif (opCode == 'READ'):
			args = self.checkArgsCount(2)

			arg1 = Var(args[0]['type'], args[0]['value'])
			arg1.checkVar()

			inputValue = { 'type':args[1]['type'], 'value': None}

			if args[1]['type'] == 'type':
				try:
					x = input()
					debugPrint('INPUT READ:',end='')
					debugPrint(x)
					if args[1]['value'] == 'int':
						inputValue['value'] = int(x)

					elif args[1]['value'] == 'string':
						inputValue['value'] = x

					elif args[1]['value'] == 'bool':
						if x.upper() == 'TRUE':
							inputValue['value'] = True
						else:
							inputValue['value'] = False
					else:
						Error(Error.UnexpectedXML,"READ hodnota arg2 != int / string / bool")
				except:
					inputValue['type'] = 'nil'
					inputValue['value'] = 'nil'
			else:
				Error(Error.WrongOPType,"READ arg2 type != type")

			debugPrint(inputValue)

			self.FRAME.setVar(args[0]['value'],inputValue)

		# Tvar Instrukcie: OPCODE <var> <symb1> <symb2>
		# Instrukcia ADD TEST
		elif (opCode == 'ADD'):
			self.arithmeticInstruction(opCode)

		# Instrukcia SUB TEST
		elif (opCode == 'SUB'):
			self.arithmeticInstruction(opCode)
			
		# Instrukcia MUL TEST
		elif (opCode == 'MUL'):
			self.arithmeticInstruction(opCode)
			
		# Instrukcia IDIV TEST
		elif (opCode == 'IDIV'):
			self.arithmeticInstruction(opCode)
			
		# Instrukcia LT TEST
		elif (opCode == 'LT'):
			self.relationInstruction(opCode)

		# Instrukcia GT TEST
		elif (opCode == 'GT'):
			self.relationInstruction(opCode)
			
		# Instrukcia EQ TEST
		elif (opCode == 'EQ'):
			self.relationInstruction(opCode)
			
		# Instrukcia AND TEST
		elif (opCode == 'AND'):
			args = self.checkArgsCount(3)
			self.logicInstruction(args,opCode)
			
		# Instrukcia OR TEST
		elif (opCode == 'OR'):
			args = self.checkArgsCount(3)
			self.logicInstruction(args,opCode)
			
		# Instrukcia NOT <var> <symb1> TEST
		elif (opCode == 'NOT'):
			args = self.checkArgsCount(2)
			self.logicInstruction(args,opCode)
			
		# Instrukcia STRI2INT
		elif (opCode == 'STRI2INT'):
			args = self.checkArgsCount(3)
			arg1Value , arg2Value = self.checkVarSymbSymb(args)		

			if arg1Value['type'] != 'string' or arg2Value['type'] != 'int':
				Error(Error.WrongOPType,'STRI2INT neplatny typ argumentu')
			if len(arg1Value['value']) <= arg2Value['value'] or arg2Value['value'] < 0 :
				Error(Error.InvalidCharOperation,"Indexacia mimo platny rozah retazecu")

			str2intValue = {'type':'int','value':0}
			try:
				str2intValue['value'] = ord(arg1Value['value'][arg2Value['value']])
			except:
				Error(Error.InvalidCharOperation,"Hodnota mimo rozsah platnosti ord()")
			
			self.FRAME.setVar(args[0]['value'], str2intValue)

		# Instrukcia CONCAT TEST
		elif (opCode == 'CONCAT'):
			args = self.checkArgsCount(3)

			arg1Value , arg2Value = self.checkVarSymbSymb(args)

			if arg1Value['type'] != 'string' or arg2Value['type'] != 'string':
				Error(Error.WrongOPType,'CONCAT neplatny typ argumentu,nie je typu string')

			result = {'type':'string', 'value': arg1Value['value'] + arg2Value['value'] }

			self.FRAME.setVar( args[0]['value'], result )
			
		# Instrukcia GETCHAR
		elif (opCode == 'GETCHAR'):
			args = self.checkArgsCount(3)

			arg1Value , arg2Value = self.checkVarSymbSymb(args)

			if arg1Value['type'] != 'string' or arg2Value['type'] != 'int':
				Error(Error.WrongOPType,'GETCHAR neplatny typ argumentu')
			if len(arg1Value['value']) <= arg2Value['value'] or arg2Value['value'] < 0 :
				Error(Error.InvalidCharOperation,"Indexacia mimo platny rozah retazecu")
			print(args[0]['value'])
			
			try:
				getChar = {'type':'string', 'value':arg1Value['value'][arg2Value['value'] ]}
			except:
				print('EXCEPT')
				Error(Error.InvalidCharOperation,"Indexacia mimo platny rozah retazecu")

			self.FRAME.setVar( args[0]['value'], getChar  )

		# Instrukcia SETCHAR TEST
		elif (opCode == 'SETCHAR'):
			args = self.checkArgsCount(3)

			arg1Value , arg2Value = self.checkVarSymbSymb(args)

			if arg1Value['type'] != 'int' or arg2Value['type'] != 'string':
				Error(Error.WrongOPType,'SETCHAR neplatny typ argumentu')

			varChar = self.FRAME.getVar(args[0]['value'])

			if len(arg2Value['value']) <= arg1Value['value'] or arg1Value['value'] < 0 :
				Error(Error.InvalidCharOperation,"Indexacia mimo platny rozsah retazec")

			try:
				varChar['value'][ arg1Value['value'] ] = arg2Value['value'][0]
				self.FRAME.setVar( args[0]['value'], varChar )
			except:
				Error(Error.InvalidCharOperation,"Indexacia mimo platny rozah retazec")
		
		
		# Tvar Instrukcie: OPCODE <label> <symb1> <symb2>
		# Instrukcia JUMPIFQE
		elif (opCode == 'JUMPIFEQ'):
			self.conditionalJump(opCode)

		# Instrukcia JUMPIFNEQ
		elif (opCode == 'JUMPIFNEQ'):
			self.conditionalJump(opCode)

		# operacny kod instrukcie nebol identifikovany
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
			debugPrint('CHECK SYMB BOOL',end='')
			debugPrint(self.typeSymb)
			debugPrint(self.value)
			if not (self.value == 'true' or self.value == 'false'):
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
	Trieda Label
	Zabecpecuje kontrolu, definiciu navesti a skokove riadenie programu a kontrolu postupnosti instrukcii
	"""
	def __init__(self):
		"""
		Label Konstruktor
		"""
		self.labels = [] 

	def setLabels(self,xmlList):
		"""
		Vyhlada a definuje existujuce navestia
		"""
		lastInsOrder = 0
		insRank = 0
		
		for ins in xmlList:
			# kontrola vzostupnej postupnosti parametru order
			newInsOrder = int(ins.attrib['order'])
			if(lastInsOrder >= newInsOrder):
				Error(Error.UnexpectedXML,'Radenie instrukci atributom order nieje vzostupna postupnost')
			lastInsOrder = newInsOrder
			
			if ins.attrib['opcode'] == "LABEL":
				labelName = self.checkLabel(ins)				

				for label in self.labels:
					if label['name'] == labelName:
						Error(Error.SemanticErr,'Pokus o redefinaciu navestia: {0}'.format(labelName))

				self.labels.append( {'name':labelName,'order': insRank } )
			
			insRank += 1

	def jump(self,name):
		"""
		Vykona skok na navestie s nazvom name
		Ak sa poukusi o skos na nedefinovane navestie, skript je ukonceny s prislusnou chybou
		:param name: nazov navestia pre skok
		:return: poradie instrukcie 
		"""
		self.checkLabelName(name)

		for label in self.labels:
			if label['name'] == name:
				return label['order']
		
		Error(Error.SemanticErr,'Pokus o skok na navestie: {0}, kt. nebolo definovane'.format(name))

	def checkLabel(self,instruction):
		"""
		vykona syntakticku a lexikalnu kontrolu navestia
		:param name: nazov navestia
		"""
		
		if (len(list(instruction)) != 1):
			Error(Error.UnexpectedXML,"Nespravny pocet argumentov instrukcie Label, op. kod:{0} ".format(instruction.attrib['opcode']))

		for child in instruction:
			if child.tag != 'arg1':
				Error(Error.UnexpectedXML,"Nazov argumentu instrukcie LABEL sa nezhoduje s arg1")

			if child.attrib['type'] != 'label':
				Error(Error.WrongOPType,"Parameter type argumentu instrukcie LABEL sa nezhoduje s typom label")

			self.checkLabelName(child.text)
		
			return child.text

	def checkLabelName(self,name):
		"""
		pomocna funkcia, kotrolujuca lexikalnu spravnost navestia
		"""
		if re.match(r'^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', name):
			pass
		else:
			Error(Error.UnexpectedXML,"Neplatny tvar navestia '{0}'".format(name))
			

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

	def getVar(self,varName,**kwargs):
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
				if kwargs.get('all',None) is not None:
					return self.globalFrame[name]
				else:
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
			Error(Error.NotExistingFrame,"DEFVAR ramec {0} neexistuje".format(varFrame))
		elif name in currentFrame:
			Error(Error.SemanticErr,"DEFVAR premenna {0} uz v ramci {1} existuje".format(name,varFrame))
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

		if name in workFrame:
			workFrame[name] = newValue
		else:
			Error(Error.NotExistingVariable,"Premenna {0} nebola definovana".format(varIdf))
			
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
		print('Err= '+msg, file=sys.stderr)
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
	InvalidCharOperation = 58	



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
			Error(Error.InvalidXMLForm,'XML subor nieje spravne formatovany')
		filePtr.close()

		sys.stdin = open(match['input'])

	elif(len(args) == 1 and 'source' in match and len(match['source']) > 0 ):
		checkFile(match['source'])

		filePtr = codecs.open(match['source'], "r", "utf-8")
		try:
			tree = ET.parse(filePtr)
			match['source'] = tree.getroot()
		except:
			Error(Error.InvalidXMLForm,'XML subor nieje spravne formatovany')
		filePtr.close()

	elif(len(args) == 1 and 'input' in match and len(match['input']) > 0):
		checkFile(match['input'])
		treeText = sys.stdin.readlines()
		sys.stdin = open(match['input'])

		try:
			match['source'] = ET.fromstring(''.join(treeText))
		except:
			Error(Error.InvalidXMLForm,'XML subor nieje spravne formatovany')
	
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
