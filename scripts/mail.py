#!/usr/bin/env python3

import config
import smtplib
import sys
from hashlib import sha1

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

if len(sys.argv) < 2:
    sys.exit('Usage: %s <recipient-email-address>' % sys.argv[0])

hash_salt = b"IAJDHAnyzKx32DQG3z1U3lXPXwb6VCPqLPvxhl0D0yOHmpq29iSnbAP"
smtp_server = config.smtp_server
smtp_password = config.smtp_password
from_address = config.from_address
to_address = sys.argv[1]

subject = "UIC Security Study Completion Process"

h = sha1()
h.update(hash_salt)
h.update(to_address)
h.update(hash_salt)
hashed_email = h.hexdigest()
print("{0} {1}".format(to_address, hashed_email))

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = from_address

text = """\
Dear UIC Security Study Participant,

Thank you very much for your participation in the UIC Security Study.  The study period is now over.  If you have met the participation requirements during the study period, you show receive the second $15 Amazon Credit as compensation for your participation in the study.

Please fill out this brief survey, to help us better understand any problems you may have encountered during the study.  The survey should take 5 minutes or less.

https://uic-auth.com?token={0}&cacheid=1417466719-97737178;return=68747470733a2f2f7777772e63732e7569632e6564752f;msg=;prior=1800;RetrieveURL=2f626c75657374656d2f6367692f72657472696576655f617574682e636769;BSVersion=1.6;BSVersionHash=b150eb45e429d51811b25dc2f79e11a112243b07;setcookie=1

You will be receiving an additional email in the next few days, including meeting times for a final, brief end-of-study meeting, where we will go through uninstalling the browser extension from your machine together.  The meeting will also include the chance to ask any last questions you may have had about the study.

This research is being conducted by Chris Kanich at the University of Illinois at Chicago and Mike Reiter at the University of Northern Carolina. It has been approved by the UIC Office for the Protection of Research Subjects as protocol number #2013-0886.

Thank you again for your time and help.  Please feel free to contact me with any questions or concerns you may have.

Sincerely,

Pete Snyder
--
Ph.D. Student
http://www.cs.uic.edu/Bits/PeterSnyder
Department of Computer Science
University of Illinois at Chicago
""".format(hashed_email)

html = """\
<html>
    <head></head>
    <body>
        <p>Dear UIC Security Study Participant,</p>

        <p>Thank you very much for your participation in the UIC Security Study.  The study period is now over.  If you have met the participation requirements during the study period, you show receive the second $15 Amazon Credit as compensation for your participation in the study.</p>

        <p>Please fill out <a href=">https://uic-auth.com?token={0}&cacheid=1417466719-97737178;return=68747470733a2f2f7777772e63732e7569632e6564752f;msg=;prior=1800;RetrieveURL=2f626c75657374656d2f6367692f72657472696576655f617574682e636769;BSVersion=1.6;BSVersionHash=b150eb45e429d51811b25dc2f79e11a112243b07;setcookie=1">this brief survey</a>, to help us better understand any problems you may have encountered during the study.  The survey should take 5 minutes or less. <a href=">https://uic-auth.com?token={1}&cacheid=1417466719-97737178;return=68747470733a2f2f7777772e63732e7569632e6564752f;msg=;prior=1800;RetrieveURL=2f626c75657374656d2f6367692f72657472696576655f617574682e636769;BSVersion=1.6;BSVersionHash=b150eb45e429d51811b25dc2f79e11a112243b07;setcookie=1">Click here to be taken to survey</a>.</p>

    <p>You will be receiving an additional email in the next few days, including meeting times for a final, brief end-of-study meeting, where we will go through uninstalling the browser extension from your machine together.  The meeting will also include the chance to ask any last questions you may have had about the study.</p>

        <p>This research is being conducted by Chris Kanich at the University of Illinois at Chicago and Mike Reiter at the University of Northern Carolina. It has been approved by the UIC Office for the Protection of Research Subjects as protocol number #2013-0886.</p>

        <p>Thank you again for your time and help.  Please feel free to contact me with any questions or concerns you may have.</p>

        <p>Sincerely,<br />
        Pete Snyder</p>
        <p>--<br />
        Ph.D. Student<br />
        <a href="http://www.cs.uic.edu/Bits/PeterSnyder">http://www.cs.uic.edu/Bits/PeterSnyder</a><br />
        Department of Computer Science<br />
        University of Illinois at Chicago</p>
    </body>
</html>
""".format(hashed_email, hashed_email)

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)
s = smtplib.SMTP(smtp_server)
s.login(from_address, smtp_password)
s.sendmail(from_address, to_address, msg.as_string())
s.quit()
