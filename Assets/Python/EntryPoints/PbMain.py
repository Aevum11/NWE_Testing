## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# Sample PitBoss window/app framework - Memory Optimized Version
# Mustafa Thamer 2-15-05
# Memory optimization applied for 32-bit Python 2.4 compatibility
#
from CvPythonExtensions import CyTranslator
import PbWizard
import PbAdmin
# Lazy import for sendEmail function only
import sys

# Pre-cache frequently used objects to reduce repeated lookups
localText = CyTranslator()
# Single app reference to minimize global namespace pollution
app = None
# Use integer instead of boolean for memory efficiency in 32-bit
bAdmin = 0

# Pre-intern frequently used strings to save memory
_SMTP_HOST_EMPTY = intern('host or address empty')
_SMTP_SENDING = intern('sending e-mail')
_SMTP_TO = intern('To: %s')
_SMTP_FROM = intern('From: %s')
_SMTP_SERVER = intern('Server: %s')
_SMTP_LOGIN = intern('Login: %s')
_SMTP_NO_AUTH = intern('Not using authentication')


#
# entry point function
#
def create():
    global app
    # Direct assignment without intermediate variables
    app = PbWizard.StartupIFace(0)


#
# entry point function
#
def run():
    global app
    # Ensure app exists before calling
    if app:
        app.startWizard()


#
# entry point function - optimized to reduce repeated object creation
#
def update():
    global bAdmin, app

    # Use integer comparison (more efficient in 32-bit)
    if not bAdmin:
        # Clean up old app reference before creating new one
        if app:
            del app
        app = PbAdmin.AdminIFace(0)
        bAdmin = 1

    if app:
        app.update()


#
# Optimized entry point functions with direct parameter access
# Avoiding unnecessary list unpacking overhead
#
def patchAvailable(argsList):
    global app
    if app:
        # Direct indexing without intermediate variables
        app.patchAvailable(argsList[0], argsList[1])


def patchProgress(argsList):
    global app
    if app:
        # Direct indexing without intermediate variables
        app.patchProgress(argsList[0], argsList[1])


def patchDownloadComplete(argsList):
    global app
    if app:
        app.patchDownloadComplete(argsList[0])


def appUpToDate():
    global app
    if app:
        app.upToDate()


def refreshRow(argsList):
    global app
    if app:
        app.refreshRow(argsList[0])


def refreshCustomMapOptions(argsList):
    global app
    if app:
        app.refreshCustomMapOptions(argsList[0])


def refreshAdvancedStartPoints(argsList):
    global app
    if app:
        app.refreshAdvancedStartPoints(argsList[0])


def getMessageOfTheDay():
    global app
    if app:
        return app.getMotD()
    return None


def addChatMessage(argsList):
    global app
    if app:
        app.addChatMessage(argsList[0])


def displayMessageBox(argsList):
    global app
    if app:
        app.displayMessageBox(argsList[0], argsList[1])


def sendEmail(argsList):
    # Lazy imports - only load when function is actually called
    # This saves memory when email functionality is not used
    import smtplib

    # Direct parameter extraction without intermediate variables
    szAddr = argsList[0]
    szHost = argsList[1]

    # Early return to avoid unnecessary processing
    if not szAddr or not szHost:
        print
        _SMTP_HOST_EMPTY
        return 1

    # Extract remaining parameters only if needed
    szLogin = argsList[2]
    szPassword = argsList[3]
    szGameName = argsList[4]
    bUseTimer = argsList[5]
    iTimeLeft = argsList[6]
    szFrom = argsList[7]
    szYear = argsList[8]

    # Print statements using pre-interned strings
    print
    _SMTP_SENDING
    print
    _SMTP_TO % (szAddr,)
    print
    _SMTP_FROM % (szFrom,)
    print
    _SMTP_SERVER % (szHost,)
    if szLogin:
        print
        _SMTP_LOGIN % (szLogin,)
    else:
        print
        _SMTP_NO_AUTH

    # Lazy import of email modules only when needed
    import MimeWriter, StringIO

    # Create message buffer
    message = StringIO.StringIO()

    try:
        writer = MimeWriter.MimeWriter(message)

        # Add headers directly without intermediate variables
        writer.addheader('To', szAddr)
        writer.addheader('From', szFrom)
        writer.addheader('Subject', localText.getText("TXT_KEY_PITBOSS_EMAIL_SUBJECT", (szGameName, szYear)))
        writer.addheader('MIME-Version', '1.0')

        # Build body efficiently
        szBody = localText.getText("TXT_KEY_PITBOSS_EMAIL_BODY", (szGameName,))
        if bUseTimer:
            # Use string concatenation only when necessary
            szBody = szBody + u"\n" + localText.getText("TXT_KEY_PITBOSS_EMAIL_TIMER", (iTimeLeft,))

        # Write body
        body = writer.startbody('text/plain')
        body.write(szBody)

        # Clean up writer reference
        del writer

        # Get message value once
        message_value = message.getvalue()

        # Clean up StringIO immediately after getting value
        message.close()
        del message

        # Send the mail
        smtp = None
        try:
            smtp = smtplib.SMTP(szHost)
            if szLogin:
                smtp.login(szLogin, szPassword)
            smtp.sendmail(szFrom, szAddr, message_value)
            return 0
        finally:
            # Ensure SMTP connection is always closed
            if smtp:
                try:
                    smtp.quit()
                except:
                    pass
                del smtp
            # Clean up message value
            del message_value

    except smtplib.SMTPAuthenticationError, e:
        _handle_smtp_error("Authentication Error: The server didn't accept the username/password combination provided.",
                           e)
        return 1
    except smtplib.SMTPHeloError, e:
        _handle_smtp_error("The server refused our HELO reply.", e)
        return 1
    except smtplib.SMTPConnectError, e:
        _handle_smtp_error("Error establishing connection.", e)
        return 1
    except smtplib.SMTPDataError, e:
        _handle_smtp_error("The SMTP server didn't accept the data.", e)
        return 1
    except smtplib.SMTPRecipientsRefused:
        print
        "All recipient addresses refused."
        return 1
    except smtplib.SMTPSenderRefused, e:
        _handle_smtp_error("Sender address refused.", e)
        return 1
    except smtplib.SMTPResponseException, e:
        _handle_smtp_error("", e)
        return 1
    except smtplib.SMTPServerDisconnected:
        print
        "Not connected to any SMTP server"
        return 1
    except:
        return 1


# Helper function to reduce code duplication in error handling
# This reduces memory usage by avoiding repeated string formatting
def _handle_smtp_error(msg, error):
    """Handle SMTP errors efficiently"""
    if msg:
        print
        msg
    # Check if error has required attributes before accessing
    if hasattr(error, 'smtp_code') and hasattr(error, 'smtp_error'):
        print
        "Error %d: %s" % (error.smtp_code, error.smtp_error)

# Memory optimization notes applied:
# 1. Lazy imports in sendEmail to avoid loading modules until needed
# 2. Pre-interned frequently used strings to reduce memory fragmentation
# 3. Early returns to avoid unnecessary processing
# 4. Explicit cleanup with del statements for large objects
# 5. Use of integer instead of boolean for bAdmin (more efficient in 32-bit)
# 6. Added null checks before app method calls to prevent errors
# 7. Direct parameter indexing without creating intermediate variables
# 8. Proper resource cleanup in finally blocks
# 9. Reduced code duplication with helper function for error handling
# 10. Closed and deleted StringIO objects immediately after use
# 11. Ensured SMTP connections are always properly closed
# 12. Removed unnecessary variable assignments in simple forwarding functions