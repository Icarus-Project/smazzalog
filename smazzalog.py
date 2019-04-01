#!/usr/bin/python
import re #importo regex
import sys, time
import os #modulo per interazione con il sistema
import datetime
import string

try:
	data_log = sys.argv[1]
	user = sys.argv[2]
except:
	print('\n')
	print("Utilizzo: python smazzalog.py [<-help | -h>] [<data_log aaaa-mm-gg>] [<utente@dominio.it> | <@dominio.it>]")
	print("DEV OP >> gg sostituibile con * per selezionare tutto il mese")
	print('\n')
	sys.exit()
data_log = sys.argv[1]
user = sys.argv[2]

def ricerca(date,user):
	i = datetime.datetime.today()
	path="/opt/zimbra-backup/logArchive/rt-mail-mlst00-p1.rt.tix.it/"
	anno, mese, giorno = date.split("-")	
	 
	#anno = int(anno)
	#mese = int(mese)
	#giorno = int(giorno)

	data = datetime.datetime(int(anno),int(mese),int(giorno))
	delta = i - data
	
	print("Sono nella funzione")
	
	if delta.days > 1:
		print("Estraggo log")
		os.popen('zgrep "postfix/smtpd" '+path+str(anno)+'/'+str(mese)+'/'+str(giorno)+'/zimbra.log.1.gz| grep '+user+' | grep "RCPT from" | grep -v NOQUEUE | grep -v lost | grep -v error > log')
		print("Log Estratto")
	elif data.date() == i.date():
		print("Estraggo log")
		os.popen('grep "postfix/smtpd" /var/log/zimbra.log | grep '+user+' | grep "RCPT from" | grep -v NOQUEUE | grep -v lost | grep -v error > log')
		print("Log Estratto")
	elif delta.days == 1:# and delta.seconds > 1 :
		print("Estraggo log")
		os.popen('zgrep "postfix/smtpd" /var/log/zimbra.log.1.gz | grep '+user+' | grep "RCPT from" | grep -v NOQUEUE | grep -v lost | grep -v error > log')
		print("Log Estratto")
	else:
		print("Impossibile selezionare log futuri")
		sys.exit()

def ricerca_wild(date,user):
	path="/opt/zimbra-backup/logArchive/rt-mail-mlst00-p1.rt.tix.it/"
	anno, mese, giorno = date.split("-")
	print("Estraggo log")
	os.popen('zgrep "postfix/smtpd" '+path+str(anno)+'/'+str(mese)+'/'+str(giorno)+'/zimbra.log.1.gz| grep '+user+' | grep "RCPT from" | grep -v NOQUEUE | grep -v lost | grep -v error > log')
	print("Log Estratto")
		
#Intro
print('********************************************************************')
print('''
Data del log in input > Export seguente:
Server Sorgente - Email Mittente - Email Destinatario - Helo
Tabella formato csv
''')
print('********************************************************************')

path="/opt/zimbra-backup/logArchive/rt-mail-mlst00-p1.rt.tix.it/"
if len(sys.argv[1]) <= 10 and len(sys.argv[1]) > 2:
	date = data_log
	print("Selezionato il log utente: "+user+" alla data del :"+date)
else:
	print("Errore parametri input")
	sys.exit()

if '*' not in date:
	print("ricerca")
	ricerca(date,user)
	export = open("export_"+date+"_"+user+".csv", 'w')
else:
	print("Wild")
	ricerca_wild(date,user)
	export = open("export_"+date[:-2]+"_"+user+".csv", 'w')

log = open('log', "r")
export.write('DATA-ORA;SERVER;FROM;TO;HELO')
export.write('\n')

stack = []
IDF=';'

#Dichiarazioni Regex
daemon_postfix_re = re.compile('postfix/smtpd\[\\d*\]')
#mta_re = re.compile(r'RT-MAIL-MT\d\d-P1')
rcpt_re = re.compile(r'RCPT from [\w+\d?\S?]+')
mail_from_re = re.compile(r'from=<.*?>')
mail_to_re = re.compile(r'to=<.*?>')
helo_re = re.compile(r'helo=<.*?>')
data_ora_re = re.compile(r'\w{3}\s+\d+\s\d{2}:\d{2}:\d{2}')

print('Regex Inizializzate')
print('Inizio ricerca su log')




#Ricerca Regex su Log
for line in log:
	#group_mta = mta_re.findall(line)
	#group_postfix = daemon_postfix_re.findall(line)
	
	data_ora = data_ora_re.findall(line)
	data_ora = str(data_ora)
	data_ora = data_ora[2:-2]
	
	
	from_server = rcpt_re.findall(line)
	from_server = str(from_server)
	from_server = from_server[11:-3]

	m_from = mail_from_re.findall(line)
	m_from = str(m_from)
	m_from = m_from[8:-3]
	
	m_to = mail_to_re.findall(line)
	m_to = str(m_to)
	m_to = m_to[6:-3]
	
	helo = helo_re.findall(line)
	helo = str(helo)
	helo = helo[8:-3]
   

	#case = group_postfix
	#case = str(case)    

	stack.append([str(data_ora+IDF),str(from_server+IDF), str(m_from+IDF), str(m_to+IDF), str(helo)])

		
print("Scrivo i risultati sul csv")
for k in stack:
	for element in k:
	    export.write(element)
	export.write('\n')

	
print('bye')    
log.close()
os.popen('rm log')
export.close()
sys.exit()
