#!/usr/bin/python

import csv
import requests
import time
import yaml
import urllib3
from datetime import datetime
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("Starting...{}".format(datetime.now()))

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)

    except yaml.YAMLError as exc:
        print(exc)

cpf = config['cpf']
senha = config['senha']

login_url = "https://cei.b3.com.br/cei_responsivo/login.aspx"
home_url = "https://cei.b3.com.br/CEI_Responsivo/home.aspx"
negociacao_url = "https://cei.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx"

session_requests = requests.session()

#abre login para caturar tokens
result = session_requests.get(login_url,verify=False)

soup = BeautifulSoup(result.text, "html.parser")

view_state = soup.find(id='__VIEWSTATE')['value']
viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
event_validation = soup.find(id='__EVENTVALIDATION')['value']

payload = {
	"__EVENTTARGET": "",
	"__EVENTARGUMENT": "",
	"ctl00$ContentPlaceHolder1$txtLogin": cpf, 
	"ctl00$ContentPlaceHolder1$txtSenha": senha, 
	"__VIEWSTATEGENERATOR": viewstate_generator,
	"__EVENTVALIDATION": event_validation,
	"__VIEWSTATE": view_state,
	"ctl00$ContentPlaceHolder1$btnLogar": "Entrar"
}

#efetua login
result = session_requests.post(
	login_url, 
	data = payload,
	headers = dict(referer=login_url)
)

#abre negociacao de ativos
result = session_requests.get(
	negociacao_url,
	headers = dict(referer=home_url)
)

soup = BeautifulSoup(result.text, "html.parser")


data_inicio = soup.find(id='ctl00_ContentPlaceHolder1_txtDataDeBolsa')['value']
data_fim = soup.find(id='ctl00_ContentPlaceHolder1_txtDataAteBolsa')['value']
conta = "0"

#percorre todos os agentes (corretoras)
agentes = soup.find(id='ctl00_ContentPlaceHolder1_ddlAgentes').find_all('option')

for agente_aux in agentes:

	view_state = soup.find(id='__VIEWSTATE')['value']
	viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
	event_validation = soup.find(id='__EVENTVALIDATION')['value']

	agente = agente_aux['value']

	print("Mudando agente => agente: " + agente)

	payload = {
		"ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1$ddlAgentes",
		"ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",
		"__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlAgentes",
		"__EVENTARGUMENT": "",
		"__LASTFOCUS": "",
		"ctl00$ContentPlaceHolder1$hdnPDF_EXCEL": "",
		"__VIEWSTATEGENERATOR": viewstate_generator,
		"__EVENTVALIDATION": event_validation,
		"__VIEWSTATE": view_state,
		"ctl00$ContentPlaceHolder1$txtDataDeBolsa": data_inicio,
		"ctl00$ContentPlaceHolder1$txtDataAteBolsa": data_fim,
		"ctl00$ContentPlaceHolder1$ddlContas": conta,
		"ctl00$ContentPlaceHolder1$ddlAgentes": agente
	}

	#seleciona agente (corretora)
	result = session_requests.post(
		negociacao_url,
		data = payload,
		headers = dict(referer=negociacao_url)
	)

	soup = BeautifulSoup(result.text, "html.parser")

	#percorre todas as contas
	contas = soup.find(id='ctl00_ContentPlaceHolder1_ddlContas').find_all('option')

	for conta_aux in contas:

		view_state = soup.find(id='__VIEWSTATE')['value']
		viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
		event_validation = soup.find(id='__EVENTVALIDATION')['value']

		conta = conta_aux['value']

		print("Mudando conta => agente: " + agente + " | conta: " + conta)

		payload = {
			"ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1$ddlAgentes",
			"ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",
			"__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlAgentes",
			"__EVENTARGUMENT": "",
			"__LASTFOCUS": "",
			"ctl00$ContentPlaceHolder1$hdnPDF_EXCEL": "",
			"__VIEWSTATEGENERATOR": viewstate_generator,
			"__EVENTVALIDATION": event_validation,
			"__VIEWSTATE": view_state,
			"ctl00$ContentPlaceHolder1$txtDataDeBolsa": data_inicio,
			"ctl00$ContentPlaceHolder1$txtDataAteBolsa": data_fim,
			"ctl00$ContentPlaceHolder1$ddlContas": conta,
			"ctl00$ContentPlaceHolder1$ddlAgentes": agente,
			"ctl00$ContentPlaceHolder1$btnConsultar": "Consultar"
		}

		#seleciona conta e retorna resultado da busca
		result = session_requests.post(
			negociacao_url,
			data = payload,
			headers = dict(referer=negociacao_url)
		)

		soup = BeautifulSoup(result.text, "html.parser")

##### GRAVAR AQUI O RESULTADO

		data = []
		table = soup.find(id="ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_pnAtivosNegociados")

		if table != None:

			table_body = table.find('tbody')

			rows = table_body.find_all('tr')
			for row in rows:
			    cols = row.find_all('td')
			    colsd = [ele.text.replace('.','').replace(',','.').strip() for ele in cols]
			    colsd.append(agente)
			    colsd.append(conta)
			    data.append([ele for ele in colsd])

			file = open("CEIHIST-" + agente + "_" + conta + ".csv", "w")

			wtr = csv.writer(file, delimiter=';', lineterminator='\n')
			for x in data : wtr.writerow(x)

			file.close()

        
#####


		#reinicializa busca
		view_state = soup.find(id='__VIEWSTATE')['value']
		viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
		event_validation = soup.find(id='__EVENTVALIDATION')['value']

		payload = {
			"ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1$btnConsultar",
			"ctl00$ContentPlaceHolder1$btnConsultar": "Nova Consulta",
			"ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",
			"__EVENTTARGET": "",
			"__EVENTARGUMENT": "",
			"__LASTFOCUS": "",
			"ctl00$ContentPlaceHolder1$hdnPDF_EXCEL": "",
			"__VIEWSTATEGENERATOR": viewstate_generator,
			"__EVENTVALIDATION": event_validation,
			"__VIEWSTATE": view_state,
			"ctl00$ContentPlaceHolder1$txtDataDeBolsa": data_inicio,
			"ctl00$ContentPlaceHolder1$txtDataAteBolsa": data_fim,
			"ctl00$ContentPlaceHolder1$ddlContas": conta,
			"ctl00$ContentPlaceHolder1$ddlAgentes": agente,
			"ctl00$ContentPlaceHolder1$btnConsultar": "Nova Consulta"
		}

		result = session_requests.post(
			negociacao_url,
			data = payload,
			headers = dict(referer=negociacao_url)
		)

		soup = BeautifulSoup(result.text, "html.parser")


print("Finish...{}".format(datetime.now()))

time.sleep(1)