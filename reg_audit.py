import winreg
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

# List of software we consider blacklisted or unwanted
blacklist = [' ', ' ', ' '] # Add your blacklisted software here

def get_installed_software():
    """
    Get a list of installed software from the Windows Registry.
    """
    software_list = []
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    num_subkeys = winreg.QueryInfoKey(key)[0]
    
    for i in range(num_subkeys):
        try:
            subkey_name = winreg.EnumKey(key, i)
            subkey = winreg.OpenKey(key, subkey_name)
            software_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
            software_list.append(software_name)
        except:
            pass
    
    return software_list

def find_blacklisted_software(installed_software, blacklist):
    """
    Find any blacklisted software in the list of installed software.
    """
    blacklisted_found = []
    for software in installed_software:
        for bad_software in blacklist:
            if bad_software.lower() in software.lower():
                blacklisted_found.append(software)
                break
    return blacklisted_found

def get_pc_username():
    """
    Get the username of the current PC user.
    """
    return os.getlogin()

def send_email(to_email, subject, body):
    """
    Send an HTML email using Gmail SMTP server.
    """
    from_email = " "  # Replace with your Gmail address
    password = " "  # Replace with your Gmail app password

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    html_part = MIMEText(body, 'html')
    msg.attach(html_part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("Security alert email sent successfully.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: Gmail authentication failed. Please check your email and app password.")
    except socket.timeout:
        print("Error: Gmail server connection timed out. Please check your network connection.")
    except Exception as e:
        print(f"Error sending security alert email: {e}")
    return False

def save_email_locally(to_email, subject, body):
    """
    Save the email content to an HTML file on the desktop if sending fails.
    """
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    filename = os.path.join(desktop, 'security_alert_email.html')
    
    with open(filename, 'w') as f:
        f.write(f"To: {to_email}<br>")
        f.write(f"Subject: {subject}<br><br>")
        f.write(body)
    print(f"Email content saved to {filename}")

def main():
    print("=" * 50)
    print("CYBERSECURITY AUDIT: BLACKLISTED SOFTWARE DETECTOR")
    print("=" * 50)
    
    username = get_pc_username()
    print(f"\nInitiating security scan for user: {username}")

    print("\nScanning for installed software...")
    installed_software = get_installed_software()

    print(f"\nTotal software found: {len(installed_software)}")
    print("\nAll installed software:")
    for software in installed_software:
        print(f"- {software}")

    print("\nChecking for blacklisted software...")
    blacklisted_found = find_blacklisted_software(installed_software, blacklist)

    if blacklisted_found:
        print("\nALERT: Blacklisted software detected:")
        for software in blacklisted_found:
            print(f"- {software}")
        
        #  email template
        email_body = f"""
        <html>
        <body style="background-color: #000000; color: #00FFFF; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #0A0A0A; padding: 20px; border: 2px solid #00FFFF; border-radius: 10px;">
                <h1 style="color: #00FFFF; text-align: center; text-transform: uppercase; letter-spacing: 2px;">Security Alert</h1>
                <p style="color: #FFFFFF;">Dear {username},</p>
                <p style="color: #FFFFFF;">During a routine security audit, the following blacklisted software was detected on your office PC:</p>
                <ul style="list-style-type: none; padding-left: 0;">
                    {chr(10).join(f'<li style="color: #FF0000; margin-bottom: 10px;">● {software}</li>' for software in blacklisted_found)}
                </ul>
                <p style="color: #FFFFFF;">Please be aware that the use of unauthorized software poses significant security risks to our organization.</p>
                <p style="color: #FFFFFF;"><strong>You are required to uninstall this software immediately and report to the IT security team for further instructions.</strong></p>
                <p style="color: #FFFFFF;">If you believe this software is necessary for your work, please contact the IT department for approval.</p>
                <p style="color: #FFFFFF;">Thank you for your cooperation in maintaining our organization's security.</p>
                <p style="color: #FFFFFF;">Best regards,<br> X3NIDE,<br>Cybersecurity Team</p>
                <div style="text-align: center; margin-top: 20px; padding: 10px; background-color: #00FFFF; color: #000000; font-weight: bold; border-radius: 5px;">
                    OFFICIAL CYBERSECURITY AUDIT NOTICE
                </div>
            </div>
        </body>
        </html>
        """
        
        receiver_email = input("\nEnter the receiver's email address to send the security alert: ")
        if not send_email(receiver_email, "URGENT: Security Audit - Unauthorized Software Detected", email_body):
            print("\nFailed to send email. Saving email content locally...")
            save_email_locally(receiver_email, "URGENT: Security Audit - Unauthorized Software Detected", email_body)
    else:
        print("\nSecurity scan complete. No blacklisted software detected.")

    print("\nCAUTION: This is an official cybersecurity audit. Any detected violations of company IT policy will be reported to management.")

    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()