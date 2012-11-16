# Import smtplib for the actual sending function
import mailer

# Import the email modules we'll need
from email.mime.text import MIMEText


ADDRESS_LIST='carl.lipo@csulb.edu'

def sendEmail( subjectText,messageText ):
   message = mailer.Message()
   message.From = "rhx-robot@csulb.edu"
   message.To = ADDRESS_LIST
   message.Subject = subjectText
   message.Body = messageText
   #message.attach("picture.jpg")

   sender = mailer.Mailer('smtp.csulb.edu')
   sender.send(message)