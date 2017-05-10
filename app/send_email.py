import smtplib

def send_email (to_name, to_addr, subject, msg):
    to_name = to_name
    to_addr = to_addr
    subject = subject
    msg = msg
    from_addr = "fromaddr@email.com"
    from_name = "from_name"
    
    message = """From: {} <{}>
    To: {} <{}>
    Subject: {}
    {}
    """
    message_to_send = message.format(from_name, from_addr, to_name,to_addr, subject, msg)
    username = ''
    password = ''
    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(from_addr, to_addr, message_to_send)
    server.quit()
    return True