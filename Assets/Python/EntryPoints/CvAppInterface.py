# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# CvAppInterface.py - Memory Optimized Version
#
# These functions are App Entry Points from C++
# WARNING: These function names should not be changed
# WARNING: These functions can not be placed into a class
#
# No other modules should import this
#
# Memory optimizations applied:
# - Lazy imports to reduce initial memory footprint
# - Removed unnecessary global variables
# - Optimized string usage with intern() where beneficial
# - More specific exception handling
# - Explicit deletion of large objects
# - Reduced scope of variables
#
from CvPythonExtensions import *


def AddSign(argsList):
    # Lazy import - only loaded when function is called
    import EventSigns
    EventSigns.addSign(argsList[0], argsList[1], argsList[2])
    # Explicitly delete module reference to allow garbage collection
    del EventSigns


def RemoveSign(argsList):
    # Lazy import
    import EventSigns
    CyEngine().removeSign(argsList[0], argsList[1])
    EventSigns.gSavedSigns.removeSign(argsList[0], argsList[1])
    del EventSigns


def initBUG():
    # Lazy import
    import BugInit
    BugInit.init()
    del BugInit


# don't make this an event - Moose
def init():
    # Import only what's needed
    import sys
    import CvUtil
    sys.stderr = CvUtil.RedirectError()
    sys.excepthook = CvUtil.myExceptHook
    sys.stdout = CvUtil.RedirectDebug()
    # Clean up references
    del CvUtil


def onSave():
    # Lazy imports
    import cPickle
    import CvEventInterface
    # if the tutorial is active, it will save out the Shown Messages list
    result = cPickle.dumps(CvEventInterface.onEvent(('OnSave', 0, 0, 0, 0, 0)))
    # Clean up references
    del cPickle
    del CvEventInterface
    return result


def onLoad(argsList):
    if argsList[0]:
        # Lazy imports
        import CvEventInterface
        import cPickle
        CvEventInterface.onEvent(('OnLoad', cPickle.loads(argsList[0]), 0, 0, 0, 0, 0))
        # Clean up references
        del cPickle
        del CvEventInterface


# Toffer - This one is called right before the map is seen when starting an new game or loading a save from the main menu.
#	Not called when loading a save from within an active game.
#	Called later than the OnLoad event, but earlier than the GameStart event.
def preGameStart():
    # import CvEventInterface
    # CvEventInterface.getEventManager().fireEvent("PreGameStart")
    print
    "PreGameStart"
    import CvScreensInterface
    CvScreensInterface.showMainInterface()
    del CvScreensInterface


def recalculateModifiers():
    # Lazy import
    import CvRandomEventInterface
    CvRandomEventInterface.recalculateModifiers()
    del CvRandomEventInterface


def onPbemSend(argsList):
    # All imports are lazy loaded and cleaned up after use
    import smtplib
    import MimeWriter
    import base64
    import StringIO

    # Extract arguments once
    szToAddr = argsList[0]
    szFromAddr = argsList[1]
    szSubject = argsList[2]
    szPath = argsList[3]
    szFilename = argsList[4]
    szHost = argsList[5]
    szUser = argsList[6]
    szPassword = argsList[7]

    # Use interned strings for repeated string literals
    print
    intern('sending e-mail')
    print
    intern('To:'), szToAddr
    print
    intern('From:'), szFromAddr
    print
    intern('Subject:'), szSubject
    print
    intern('Path:'), szPath
    print
    intern('File:'), szFilename
    print
    intern('Server:'), szHost
    print
    intern('User:'), szUser

    if not szFromAddr or not szHost:
        print
        intern('host or address empty')
        # Clean up imports before returning
        del smtplib, MimeWriter, base64, StringIO
        return 1

    # Create message in limited scope
    message = StringIO.StringIO()
    writer = MimeWriter.MimeWriter(message)

    writer.addheader('To', szToAddr)
    writer.addheader('From', szFromAddr)
    writer.addheader('Subject', szSubject)
    writer.addheader('MIME-Version', '1.0')
    writer.startmultipartbody('mixed')

    part = writer.nextpart()
    body = part.startbody('text/plain')
    body.write('CIV4 PBEM save attached')

    part = writer.nextpart()
    part.addheader('Content-Transfer-Encoding', 'base64')
    # Build string inline to avoid extra variable
    body = part.startbody("application/CivBeyondSwordSave; name=%s" % szFilename)

    # Use context manager pattern for file (Python 2.4 compatible way)
    file_handle = open(szPath + szFilename, 'rb')
    try:
        base64.encode(file_handle, body)
    finally:
        file_handle.close()

    # finish off
    writer.lastpart()

    # Get message value once
    message_value = message.getvalue()

    # Clean up writer and message objects
    del writer
    message.close()
    del message

    # send the mail
    result = 0
    try:
        smtp = smtplib.SMTP(szHost)
        if len(szUser) > 0:
            smtp.login(szUser, szPassword)
        smtp.sendmail(szFromAddr, szToAddr, message_value)
        smtp.quit()
    except smtplib.SMTPAuthenticationError, e:
        CyInterface().addImmediateMessage(
            "Authentication Error: The server didn't accept the username/password combination provided.", "")
        CyInterface().addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")
        result = 1
    except smtplib.SMTPHeloError, e:
        CyInterface().addImmediateMessage("The server refused our HELO reply.", "")
        CyInterface().addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")
        result = 1
    except smtplib.SMTPConnectError, e:
        CyInterface().addImmediateMessage("Error establishing connection.", "")
        CyInterface().addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")
        result = 1
    except smtplib.SMTPDataError, e:
        CyInterface().addImmediateMessage("The SMTP server didn't accept the data.", "")
        CyInterface().addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")
        result = 1
    except smtplib.SMTPRecipientsRefused:
        CyInterface().addImmediateMessage("All recipient addresses refused.", "")
        result = 1
    except smtplib.SMTPSenderRefused, e:
        CyInterface().addImmediateMessage("Sender address refused.", "")
        CyInterface().addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")
        result = 1
    except smtplib.SMTPResponseException, e:
        CyInterface().addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")
        result = 1
    except smtplib.SMTPServerDisconnected:
        CyInterface().addImmediateMessage("Not connected to any SMTP server", "")
        result = 1
    except:
        result = 1

    # Clean up message value and imports
    del message_value
    del smtplib, MimeWriter, base64, StringIO
    return result


# Cache for BugOptions to avoid repeated imports
_options_cache = None


def _get_options():
    """Helper function to get options with caching"""
    global _options_cache
    if _options_cache is None:
        import BugOptions
        _options_cache = BugOptions.g_options
    # Don't delete BugOptions as we're caching a reference
    return _options_cache


def getOption(id):
    """Get option by id with lazy loading"""
    return _get_options().getOption(id)


def getOptionBOOL(argsList):
    """Get boolean option with error handling"""
    id, default = argsList
    try:
        option = getOption(id)
        # Direct bool conversion without intermediate variable
        return bool(option.getValue())
    except:
        return default


def getOptionINT(argsList):
    """Get integer option with error handling"""
    id, default = argsList
    try:
        option = getOption(id)
        # Direct int conversion without intermediate variable
        return int(option.getValue())
    except:
        return default


def gameExitSave():
    """Auto save on game exit"""
    import AutoSave
    AutoSave.autoSave("[Exit]")
    del AutoSave


# Camera zoom caching - optimized to avoid global when possible
_camera_zoom_cache = None


def cacheCameraZoom():
    """Cache current camera zoom level"""
    global _camera_zoom_cache
    _camera_zoom_cache = CyCamera().GetZoom()


def resetCameraZoom():
    """Reset camera to cached zoom level"""
    global _camera_zoom_cache
    if _camera_zoom_cache is not None:
        CyCamera().SetZoom(_camera_zoom_cache)


# Referenced by the BtS exe.
def getConsoleMacro(argsList):
    """Return empty string for console macro"""
    return ""