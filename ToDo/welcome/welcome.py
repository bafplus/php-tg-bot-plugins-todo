import asyncio, re, logging, json, random
import hangups
import plugins

logger = logging.getLogger(__name__)

def _initialise(bot):
  plugins.register_handler(_handle_join, type="membership")
  plugins.register_admin_command(["setwelcome"])
  plugins.register_user_command(["welcome"])

@asyncio.coroutine
def _handle_join(bot, event, command):
  if not event.conv_event.type_ == hangups.MembershipChangeType.JOIN:
    return


  path = ["conversations", event.conv_id, "welcomemsg"]

  try:
    welcomemsg = bot.memory.get_by_path(path)
  except:
    return
  
  if not welcomemsg:
    return

  for user_id in event.conv_event.participant_ids:
    yield from bot.coro_send_to_user_and_conversation(user_id.chat_id, event.conv, welcomemsg, "Welcome to the hangout! I've sent you some info ;)")

@asyncio.coroutine
def setwelcome(bot, event, *args):
  """Set the welcome message for this hangout. You can also turn welcomes on and off with /bot setwelcome on and /bot setwelcome off"""

  if not bot.memory.exists(["conversations"]):
    bot.memory.set_by_path(["conversations"],{})
    
  if not bot.memory.exists(["conversations",event.conv_id]):
    bot.memory.set_by_path(["conversations",event.conv_id],{})

  if not bot.memory.exists(["conversations",event.conv_id,"welcome_enabled"]):
    bot.memory.set_by_path(["conversations",event.conv_id,"welcome_enabled"], False)

  if not bot.memory.exists(["conversations",event.conv_id,"welcomemsg"]):
    bot.memory.set_by_path(["conversations",event.conv_id,"welcomemsg"], "")
  
  if args[0] == "on":
    bot.memory.set_by_path(["conversations",event.conv_id,"welcome_enabled"], True)
    return

  if args[0] == "off":
    bot.memory.set_by_path(["conversations",event.conv_id,"welcome_enabled"], False)
    return

  if not bot.memory.get_by_path(["conversations",event.conv_id,"welcome_enabled"]):
    return

  path = ["conversations", event.conv_id, "welcomemsg"]
  
  if len(args) > 0:
    bot.memory.set_by_path(path, " ".join(args))
    
  yield from bot.coro_send_message(event.conv_id, "Current welcome message is: " + bot.memory.get_by_path(path))

@asyncio.coroutine
def welcome(bot, event, *args):
  """Display the welcome message for a hangout. Admins can set the welcome message for the hangout."""
 
  if not bot.memory.exists(["conversations"]):
    bot.memory.set_by_path(["conversations"],{})
    
  if not bot.memory.exists(["conversations",event.conv_id]):
    bot.memory.set_by_path(["conversations",event.conv_id],{})

  if not bot.memory.exists(["conversations",event.conv_id,"welcomemsg"]):
    bot.memory.set_by_path(["conversations",event.conv_id,"welcomemsg"], "")

  path = ["conversations", event.conv_id, "welcomemsg"]
  
  if not bot.memory.exists(["conversations",event.conv_id,"welcome_enabled"]):
    bot.memory.set_by_path(["conversations",event.conv_id,"welcome_enabled"], False)
  
  if not bot.memory.get_by_path(["conversations",event.conv_id,"welcome_enabled"]):
    yield from bot.coro_send_message(event.conv_id, "Welcome message is disabled for this hangout")
  else:
    yield from bot.coro_send_message(event.conv_id, bot.memory.get_by_path(path))
