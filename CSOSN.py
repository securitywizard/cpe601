#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mpopuri
#
# Created:     13/02/2014
# Copyright:   (c) mpopuri 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/python                 # This is server.py file
import socket                     # Import socket module
import thread                     # Import thread Module
import time			  # Import Time Module
from threading import*            # Import threading module
import logging                    # Import logging module
import sqlite3 as lite		  # Import Sqlite Database Module
import sys                        # Import system module
from xml.etree import ElementTree # Import xml module
import os                         # Import os module   

con = lite.connect('users.db') # Connects to the Users database
cur=con.cursor()
HOST = ""
PORT = int(input('Enter server port ')) # quires user to enter the port no to start server
users = {}
conns = {}
f=open('online.txt','w')                 # File contains the information of users who are online
print >> f, 'online users'
f.close()
global friend				# Global Variables
global found
#activity logger config
logger = logging.getLogger('server')
hdlr = logging.FileHandler('server.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

#error logger
log = logging.getLogger('servererror')
handlr = logging.FileHandler('servererror.log')
formatt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatt)
log.addHandler(handlr)
log.setLevel(logging.DEBUG)


def accept(conn, addr):
    """
    Call the inner func in a thread so as not to block. Wait for a
    name to be entered from the given connection. Once a name is
    entered, set the connection to non-blocking and performs the 
    functions Such as Search, Accpting and Rejecting Friend Requests, Chat, Wallpost
    """
    def threaded():                             # threaded funtion which gives each user a separate thread
        while True:
            conn.send("\nPlease Enter Your Name:\n")
            try:
                name = conn.recv(1024).strip()
		logger.info(name)
            except socket.error:
		log.error('socket error')                
		continue
            for line in open('users.txt', 'r'):             # Searchs Weather The User is Already Registered/ New.
    		ly = line.split()
		found = 'False'
       		if name in ly:
			found = 'true'
			break
            if found =='true':
		for line in open('users.txt', 'r'):
    			ly = line.split()
       			if name in ly:
				data= ly
				f= open('online.txt','a')  # If he was Already Registered Updates Online file saying user was online
				print >> f,data
				f.close()
				break		
		broadcast(name, "+++ %s arrived +++" % name)		
		menu(name,conn)

            elif found =='False':                          # If the User was not Registered to the Network this phase promts user to register to network.
		#conn.send("register to the Online Social network\n")
	        conn.send("REGISTER User-ID User-name User-Last-name : \n")
                data = conn.recv(1024).strip()
              	#cur.execute("INSERT INTO user_d VALUES (data)") # I have threading problem with database, so I'm using files in all cases
		#users.append(data)
		#conns.append(conn)
		f=open('online.txt','a')			# Writes the Registered user to online file
		print >> f,data
		f.close()
		f=open('users.txt','a')
		print >> f, data				# Updates users file with the registered users	
#		f.write(data, conn)
		f.close()  
		f=open('conn.txt','a')				# update conn file with new connection
		print >> f,conn
		f.close()           
                users[name] = conn
                broadcast(name, "+++ %s Joined +++" % name)
		conn.send('Welcome To Online Social Network\n')
                menu(name,conn)
		break
    thread.start_new_thread(threaded, ())

def menu(name,conn):      
		conn.send("""\n What Would You Like to Do
	 1. (search) a Friend 					
	 2. (chat) to Friend
 	 3. (post) a Wall Post \n
				""")  # promts user to enter the required funtion.
		
                var = conn.recv(1024).strip()
	


		if var=='search':   
			conn.send('SEARCH keyword:\n')
			
                       	try:
                		friend = conn.recv(1024).strip()
				logger.info(friend)
            		except socket.error:
				log.error('socket error') 
			for line in open('users.txt', 'r'):
    				ly = line.split()
				found= 'False'
       				if friend in ly:
					found= 'true'
					break
			if found  == 'true':			
				for line in open('users.txt', 'r'):         # prints the Search Keyword from users.txt
    					ly = line.split()
					found= 'False'
       					if friend in ly:			
						conn.send(ly[0])
						conn.send('\t')
						conn.send(ly[1])
						conn.send('\t')
						conn.send(ly[2])
						conn.send('\n')							
						found= 'true'
						break
				f=open(name,'a')
				f.write('\n')			
				f.close()
				conn.send("""	Send Friend Requests / View Pending Requests:
				     1. Key in '1' to send a Request.
				     2. Key in '2' to view and accept pending Requests\n
					""")							# prompts user to send/view friend request
				try:
					recv= conn.recv(1024).strip()				# receives information from user
					logger.info(recv)
				except socket.error:
					log.error('socket error') 
				
				if recv == '1':								
				
					for line in open(name, 'r'):				# searchs for friend in the user file for weather in his list / not.
    						ly = line.split()
						found= 'False'
       						if friend in ly:							
							found= 'true'
							break	
					if found== 'False':
						conn.send('\nfriend found, Would you like to send a friend requset:\n Please Key In Yes/No\n')
						try:
               						value = conn.recv(1024).strip()
							logger.info(value)
            					except socket.error:
							log.error('socket error')                

						if value=='Yes':
							f=open('frndrequests.txt','a')
							print >> f, friend,name
												
							f.close()
							conn.send('Request Sent')
							menu(name,conn)
						elif value== 'No':
							menu(name,conn)
					elif found== 'true':
						conn.send('You both are already Friends\n')
						menu(name,conn)
				
				elif recv == '2':
					
					for line in open('frndrequests.txt','r'):
    						ly = line.split()
						found= 'False'
						if name in ly:
							found='True'
							conn.send(ly[1])
							conn.send('''  \t Want to add to your Friend List:
							     1. CONFIRM FRIEND
							     2. REJECT FRIEND\n
								''')
							try:
								recv=conn.recv(1024).strip()
								logger.info(recv)
							except socket.error:
								log.error('socket error')
							if recv== '1':
								f=open(name,'a')					# updates friend and users file when user acepts request
								print >> f, ly[1],'\n'
						
								f.close()
								f=open(friend,'a')
								print >> f, ly[0], '\n'
								f.close()
						
								f=open('frndrequests.txt','r')
								lines=f.readlines()
								f.close()
								f=open('frndrequests.txt','w')
								for line in lines:
									ly=line.split()								
									if name in ly:
										continue
									else:
										f.write(line)
								f.close()
								conn.send('\nFriend Confirmed & Friend List Updated\n')
								menu(name,conn)
							elif recv== '2':
								f=open('frndrequests.txt','r')
								lines=f.readlines()
								f.close()
								f=open('frndrequests.txt','w')
								for line in lines:
									ly=line.split()								
									if name in ly:
										continue
									else:
										f.write(line)
								f.close()
								conn.send('Friend Request Rejected\n')
								menu(name,conn)
						else:
							conn.send('You Have No Pending friend Requests\n')
							menu(name,conn)
					f.close()
			else:
				conn.send('The Friend You are Searching Not Exists')
				menu(name,conn)
	 	elif var == 'chat':
			chat(name,conn)
		elif var == 'post':
			post(name,conn)
		elif var== 'online':
			online(name,conn)

		else:
			conn.send("Please enter either search/chat/post/online:\n ")
			menu(name,conn)
"""def online(name,conn):
	conn.send('Displaying Online Users:\n')
	for line in open('online.txt', 'r'):
    		ly = line.split()
       		conn.send(ly)
	f.close()
	menu(name,conn)"""
def chat(name, conn):								# establishs Chat connection with the user 
	#online(name,conn)
	conn.send("Keyin the Name or ID of your friend you Want to chat with\n")
	try:
               	val = conn.recv(1024).strip()
		logger.info(val)
       	except socket.error:
		log.error('socket error')                
	for line in open('users.txt', 'r'):                          
    		ly = line.split()
		found= 'False'
	       	if val in ly:
			found= 'true'
			break
	if found=='true':
		for line in open(name, 'r'):
    			ly = line.split()
			found= 'False'
	       		if val in ly:
				found= 'true'
				break
		if found== 'true':		
			conn.setblocking(False)
               		users[name] = conn
			conn.send('Chat Connection Estabished:\n')
			msg=conn.recv(4096).strip()
			broadcast(val,msg)
			n=0						
			for val in users:
				n=n+1
			print conns[n]
			send(msg, conns[n])
			conn.send(data)	
		elif fount== 'False':
			conn.send('\nYou both are Not Friends, Send the Friend Request to chat\n')
			menu(name,conn)
	elif found== 'False':
		conn.send('User Not Found\n') 
		chat(name,conn)	
	menu(name,conn)

def post(name,conn):                                                  # posts msgs to groups/ add to groups
	conn.send("""What Would You Like to Do
			     1. (add) group
			     2. (wallpost) in group
		             3. (view) wall posts\n
				""")			
	try:
        	var = conn.recv(1024).strip()
		logger.info(var)
       	except socket.error:
		log.error('socket error')                
	#continue
	if var== 'add':
		conn.send("""Which Group You want to Register:
			 Key in 'F' to register for group friends
			 Key in 'FF' to register for group friendsoffriends\n
			""")
		try:
               		var = conn.recv(1024).strip()
			logger.info(var)
           	except socket.error:
			log.error('socket error')                
		#continue
		f=open('friends.txt','a')
		f.write('\n')
		f.close()
		f=open('friendsoffriends.txt','a')
		f.write('\n')
		f.close()
		if var== 'F':
				
			for line in open('friends.txt','r'):
    				ly = line.split()
				found= 'False'
       				if name in ly:
					found= 'true'
					break	
			f.close()
			
			if found== 'true':
				conn.send('You are Already Subscribed to This Group\n')
				post(name,conn)
			elif found== 'False':	
				f=open('friends.txt','a')
				print >> f, name
				
				f.close()
				conn.send('Registered to Group Friends\n')
				post(name,conn)

		elif var== 'FF':
			
			for line in open('friendsoffriends.txt','r'):
    				ly = line.split()
				found= 'False'
       				if name in ly:
					found= 'true'
					break
			f.close()
			if found== 'true':
				conn.send('You are Already Subscribed to This Group\n')
				post(name,conn)
			elif found== 'False':
				f=open('friendsoffriends.txt','a')
				print >> f, name
				
				f.close()
				conn.send('Registered to Group FriendsofFriends\n')
				post(name,conn)
		elif not var:
                # Empty string is given on disconnect.
               		del users[name]
			f=open('online.txt','r')
			lines=f.readlines()
			f.close()
			f=open('online.txt','w')
			for line in lines:
				ly=line.split()								
				if name in ly:
					continue
				else:
					f.write(line)
			f.close()
                	broadcast(name, "--- %s leaves ---" % name)

	elif var== 'wallpost':
		conn.send("""In which Group You want to Post:
			     Key in 'F' to Post in Friends Group
			     Key in 'FF' to post in Friends of Friends Group\n
				""")
		try:
               		rev=conn.recv(1024).strip()
			logger.info(var)
           	except socket.error:
			log.error('socket error')                
		#continue
		if rev== 'F':
			for line in open('friends.txt','r'):
    				ly = line.split()
				found= 'False'
       				if name in ly:
					found= 'true'
					break
			if found== 'true':
				conn.send('Enter the Message you want to post into Friends Group:\n')
				#conn.send("Keyin the group in which you want to post\n")
				#rev=conn.recv(1024).strip()
				#f rev== 'F
				try:
    	           			data=conn.recv(4096).strip()
					logger.info(data)
    		       		except socket.error:
					log.error('socket error')                
				#continue
				f=open('friendsmsgs.txt','a')
				print >> f, name, data
				
				f.close()				
				conn.send('message posted into friends Group \n')
				post(name,conn)
			elif found=='False':
				conn.send('You are Not Subscribed to this Group:\n')
				post(name,conn)
				menu(name,conn)
		elif rev== 'FF':
			for line in open('friends.txt','r'):
    				ly = line.split()
				found= 'False'
       				if name in ly:
					found= 'true'
					break			
			if found=='true':

				conn.send('Enter the Message you want to post into FriendsofFriends group:\n')		
				try:
        	       			data=conn.recv(4096).strip()
					logger.info(data)
        	   		except socket.error:
					log.error('socket error')                
			#continue
				f=open('frndsoffrndsmsgs.txt','a')
				print >> f, name, data
				
				f.close()
				conn.send('Message Posted to FriendsofFriends Group\n')
				menu(name,conn)
			elif found== 'False':
				conn.send('You are not Subscribed to This Group:\n')
				post(name,conn)
	elif var== 'view':
				
		conn.send("""which Group Messages you ant to view:
			     Key in 'F' to view Msgs in Friends Group
			     Key in 'FF' to view Msgs in Friends of Friends Group\n
				""")
		try:
               		rev=conn.recv(1024).strip()
			logger.info(var)
           	except socket.error:
			log.error('socket error')                
		#continue
		if rev== 'F':
			for line in open('friends.txt','r'):
    				ly = line.split()
				found= 'False'
       				if name in ly:
					found= 'true'
					break					
			if found== 'true':
				for line in open('friendsmsgs.txt','r'):
	
					conn.send(line)
					conn.send('\n')
				
				
				menu(name,conn)
			elif found== 'False':
				conn.send('You are Not Subscribed to this Group\n')
				post(name,conn)
		elif rev== 'FF':
			
			for line in open('friends.txt','r'):
    				ly = line.split()
				found= 'False'
       				if name in ly:
					found= 'true'
					break					

			if found== 'true':

				for line in open('friendsoffrndsmsgs.txt','r'):
					conn.send(line)
					conn.send('\n')
				f.close()
				menu(name,conn)
			elif found== 'False':
				conn.send('You are Not Subcribed to view Messages In this group\n')
				post(name,conn)
		else:
			conn.send('Enter again:\n')
			post(name,conn)
	elif not var:
                # Empty string is given on disconnect.
                del users[name]
		f=open('online.txt','r')
		lines=f.readlines()
		f.close()
		f=open('online.txt','w')
		for line in lines:
			ly=line.split()								
			if name in ly:
				continue
			else:
				f.write(line)
		f.close()
                broadcast(name, "--- %s leaves ---" % name)
						
					

def send(msg, conns):
	conns.send(msg)
	data=conns.recv(4096).strip()
	return data


#"""def search(var):
#	for line in open('users.txt', 'r'):
#    		ly = line.split()
#		found= 'False'
#      		if var in ly:
#			found= 'true'
#			break
#	return found"""
def broadcast(name, message):
    """
    Send a message to all users from the given name.
    """
    print message
    for to_name, conn in users.items():
        if to_name !=name:
            try:
                conn.send(message + "\n")
		logger.info(message)
            except socket.error:
		log.error('noresponce')
		pass
# Set up the server socket.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(False)
server.bind((HOST, PORT))
server.listen(10)
print "Listening on %s" % ("%s:%s" % server.getsockname())

# Main event loop.
while True:
    try:
        # Accept new connections.
        while True:
            try:
                conn, addr = server.accept()
		logger.info(conn)
		logger.info(addr)
            except socket.error:
		log.error('socket error')
                break
            accept(conn, addr)
        # Read from connections.
        for name, conn in users.items():
            try:
                message = conn.recv(1024)
            except socket.error:
                continue
            if not message:
                # Empty string is given on disconnect.
                del users[name]
                broadcast(name, "--- %s leaves ---" % name)
            else:
                broadcast(name, "%s> %s" % (name, message.strip()))
        time.sleep(.1)
    except (SystemExit, KeyboardInterrupt):
        break
