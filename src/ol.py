import win32com.client

session = win32com.client.gencache.EnsureDispatch ("Outlook.Application")

#
# Leave blank to be prompted for a session, or use
# your own profile name if not "Outlook". It is also
# possible to pull the default profile from the registry.
#
#session.Logon ("Outlook")
messages = session.Inbox.Messages

#
# Although the inbox_messages collection can be accessed
# via getitem-style calls (inbox_messages[1] etc.) this
# is the recommended approach from Microsoft since the
# Inbox can mutate while you're iterating.
#
message = messages.GetFirst ()
while message:
  print message.Subject
  message = messages.GetNext ()