from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from pyVoIP.VoIP import VoIPPhone, InvalidStateError
import time


Server_IP="192.168.1.170" #ip of the PBX Server
Extention = "706" #Extention for the PBX
Password = "12345678" #Password for the Extention My_IP="192.168.1.205" #This PCs IP
My_IP = "192.168.1.205" #This PCs IP

OSC_Server_Port=6063 #Port to listen to OSC on
PBX_Server_Port=5160 #SIP propert

Debug_Mode=True #if true print debug modes


def debug(Message):
    if Debug_Mode==True:
        print(Message)

def answer(call): # This will be your callback function for when you receive a phone call.
    try:
      call.answer()
      call.hangup()
    except InvalidStateError:
      pass

debug("running")

phone=VoIPPhone(Server_IP, PBX_Server_Port, Extention, Password, My_IP, PBX_Server_Port, 10000, 20000)
phone.start()

debug(phone.get_status()) #log PBX Status


def Call_Extention(address, *args): #calls the extention - osc must be formated "/call/extnetion"
    global current_call
    debug(("cailing number: ") + str(address.split("/")[2])) #Print calling number
    current_call = phone.call(str(address.split("/")[2])) #call extention
    debug("called")

def Hangup(address): #hangs up outgoing call before it's been picked up - osc format: "/hangup"
    #print(current_call.state)
    current_call.cancel_request() #sends a SIP Cancel request
    phone.release_ports()
    #if(current_call.state == "CallState.DIALING"): #if the outgoing call has not been picked up yet





def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

dispatcher = Dispatcher()
dispatcher.map("/call/*", Call_Extention)
dispatcher.map("/hangup/", Hangup)
dispatcher.set_default_handler(default_handler)


server = BlockingOSCUDPServer((My_IP, OSC_Server_Port), dispatcher)
server.serve_forever()  # Blocks forever
