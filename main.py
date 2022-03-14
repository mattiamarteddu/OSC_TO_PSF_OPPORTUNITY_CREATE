import sys

from Function import *
payloadSoap = """<soapenv:Envelope xmlns:act="http://xmlns.oracle.com/apps/crmCommon/activities/activitiesService/" xmlns:not="http://xmlns.oracle.com/apps/crmCommon/notes/noteService" xmlns:not1="http://xmlns.oracle.com/apps/crmCommon/notes/flex/noteDff/" xmlns:opp="http://xmlns.oracle.com/apps/sales/opptyMgmt/opportunities/opportunityService/" xmlns:rev="http://xmlns.oracle.com/apps/sales/opptyMgmt/revenues/revenueService/" xmlns:rev1="http://xmlns.oracle.com/oracle/apps/sales/opptyMgmt/revenues/revenueService/" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:typ="http://xmlns.oracle.com/cloud/adapter/osc/trigger_REQUEST/types" xmlns:typ1="http://xmlns.oracle.com/apps/sales/opptyMgmt/opportunities/opportunityService/types/">
   <soapenv:Header>
      <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
         <wsu:Timestamp wsu:Id="TS-47F1D4DE38D372B8B616467375655591">
           <wsu:Created>${=context.testCase.getPropertyValue( "TIMESTAMP_START" )}</wsu:Created>
            <wsu:Expires>${=context.testCase.getPropertyValue( "TIMESTAMP_END" )}</wsu:Expires>
         </wsu:Timestamp>
         <wsse:UsernameToken wsu:Id="UsernameToken-3D95FD8B9E7BFF162F16467365224622">
            <wsse:Username>OSC_OIC_APPID_BASICAUTH</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">ed6fcd35-6d38-401b-8780-974176a9f326</wsse:Password>
            <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">BoLIJIMlpJVHvBagQSFsJg==</wsse:Nonce>
            <wsu:Created>2022-03-08T10:48:42.462Z</wsu:Created>
         </wsse:UsernameToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <typ:onEvent>
         <typ1:getOpportunityResponse>
            <typ1:result>
              ~
               <opp:Status_c>?</opp:Status_c>
            </typ1:result>
         </typ1:getOpportunityResponse>
      </typ:onEvent>
   </soapenv:Body>
</soapenv:Envelope>"""





#payload = input("Inserisci Payload: ")

def getEmailFromPayload(payload):
    email = re.findall(r"<ns2:CustomerEmail_RO_c>+[A-Za-z0-9\.\-+_]+@[A-Za-z0-9\.\-+_]+\.[A-Za-z]+", payload)
    email = str(email).replace("<ns2:CustomerEmail_RO_c>", "")
    email = email.replace("['","")
    email = email.replace("']", "")
    return email

def editPayload(payload): ##### Modifica il payload in modo da renderlo utilizzabile per la chiamata su SOAPUI
    partyNumber = getCustomerF00(payload)

    partyFRR = re.findall(r"<ns2:CUST_ID_RO_c>+[A-Z0-9\.\-+_]+", payload)
    partyFRR = str(partyFRR).replace("['<ns2:CUST_ID_RO_c>", "")
    partyFRR = partyFRR.replace("']", "")

    payload = payload.replace(partyFRR,partyNumber)
    payload = payload.replace("""<ns01:onEvent xmlns:ns01="http://xmlns.oracle.com/cloud/adapter/osc/trigger_REQUEST/types">""", "")
    payload = payload.replace("""<ns0:getOpportunityResponse xmlns="" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns0="http://xmlns.oracle.com/apps/sales/opptyMgmt/opportunities/opportunityService/types/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">""","")
    payload = payload.replace('<ns3:result xmlns:ns0="http://xmlns.oracle.com/adf/svc/types/" xmlns:ns1="http://xmlns.oracle.com/apps/sales/opptyMgmt/revenues/revenueService/" xmlns:ns2="http://xmlns.oracle.com/apps/sales/opptyMgmt/opportunities/opportunityService/" xmlns:ns3="http://xmlns.oracle.com/apps/sales/opptyMgmt/opportunities/opportunityService/types/" xmlns:ns6="http://xmlns.oracle.com/apps/crmCommon/notes/noteService" xmlns:ns7="http://xmlns.oracle.com/oracle/apps/sales/opptyMgmt/revenues/revenueService/" xmlns:ns8="http://xmlns.oracle.com/apps/crmCommon/activities/activitiesService/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns2:Opportunity">',"")
    payload = payload.replace("""</ns3:result>""", "")
    payload = payload.replace("""</ns0:getOpportunityResponse>""", "")
    payload = payload.replace("""</ns01:onEvent>""", "")

    payload = payload.replace("ns2", "opp")
    payload = payload.replace("ns1", "rev")
    payload = payload.replace('xsi:nil="true"', "")
    return payload



def getCustomerF00(payload):
    basic = HTTPBasicAuth('FUSION_APPS_ICS_APPID', 'Oracle123456!')
    email = getEmailFromPayload(payload)
    url = "https://efxu.fa.em2.oraclecloud.com/crmRestApi/resources/latest/contacts/?onlyData=true&fields=PartyNumber&q=EmailAddress={}".format(email)
    r = requests.get(url, auth=basic)
    data = r.json()                                                 ##### Dati ottenuti dalla chiamata convertiti in JSON #####
    myJSON = json.dumps(data)                                       #####json.loads take a string as input and returns a dictionary as output.#####
    dataJson = json.loads(myJSON)                                   #####json.dumps take a dictionary as input and returns a string as output.#####
    partyNumber = str(dataJson['items'])                            #####Converte l'oggetto estratto in una string#####
    partyNumber = partyNumber.replace("[{'PartyNumber': '", "")     ##### Rimuove le parti inutili dalla stringa#####
    partyNumber = partyNumber.replace("'}]", "")                    ##### Rimuove le parti inutili dalla stringa#####
    return partyNumber



def soapRequest(payload):
    url="https://prod-frhyz1ndv9sd-fr.integration.ocp.oraclecloud.com:443/ic/ws/integration/v1/flows/osc/OSC_TO_PSF_TRGBY_OPPOR_CREAT/1.0/"
    payloadS = payloadSoap.replace("~", editPayload(payload))
    headers = {'content-type': 'application/soap+xml',
               'SOAPAction': 'http://xmlns.oracle.com/fa/event/onEvent'
               }
    print(payloadS)
    #response = requests.post(url, data=payloadSoap, headers=headers)







def genTimestamp():
    ct = datetime.datetime.now()
    ts = """<wsu:Timestamp wsu:Id="TS-D8674BFA16FF96CFBB164701481025913">
            <wsu:Created>ctZ</wsu:Created>
            <wsu:Expires>2022-03-11T16:07:50.259Z</wsu:Expires>
         </wsu:Timestamp>"""
    bashCommand = """echo '('`date +"%s.%N"` ' * 1000000)/1' | bc"""
    ts.format(ct)
    tsInms= str('{:<014}'.format(current_milli_time()))
    ts = ts.replace("164701481025913", tsInms)
    ts = ts.replace("ct",'%.23s' % ct)
    ts = ts.replace("", 'T') ######Inserire la T nel timestamp
    print(ts)
import time

def DataEORa():
    ct = datetime.datetime.now()
    print("current time:-", ct)

    # ts store timestamp of current time
    ts = ct.timestamp()
    print("timestamp:-", ts)


def current_milli_time():
    return round(time.time() * 1000)

track_1 = input("Inserisci track_1: ")
connectionDb(track_1)

#DataEORa()
#genTimestamp()
#print(getEmailFromPayload(payload))
#print(getCustomerF00(payload))
#print(soapRequest(payload))
#sys.stdout = open("Data.txt", "w")
#print(soapRequest(payload))
#sys.stdout.close()


