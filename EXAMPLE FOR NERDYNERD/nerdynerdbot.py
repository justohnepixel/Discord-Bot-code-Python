import os
import sys
import subprocess
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.resolve()
VENV_DIR = ROOT / ".venv"
BOOTSTRAP_FILE = ROOT / "bootstrap.py"


def get_venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def is_bootstrap_needed() -> bool:
    if not VENV_DIR.exists():
        return True

    try:
        import dotenv  # noqa: F401
        import discord  # noqa: F401
        from discord.ext import commands  # noqa: F401
        from discord.utils import get  # noqa: F401
        return False
    except ImportError:
        return True


def run_bootstrap():
    if not BOOTSTRAP_FILE.exists():
        print(f"Missing bootstrap.py at {BOOTSTRAP_FILE}")
        sys.exit(1)

    print("Running bootstrap.py to create .venv and install dependencies...")
    subprocess.check_call([sys.executable, str(BOOTSTRAP_FILE)])
    venv_python = get_venv_python()
    if not venv_python.exists():
        print("Bootstrap completed but .venv python was not found:", venv_python)
        sys.exit(1)

    print("Re-launching bot.py using .venv Python:", venv_python)
    os.execv(str(venv_python), [str(venv_python), str(__file__)] + sys.argv[1:])


if is_bootstrap_needed():
    run_bootstrap()


from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.utils import get

# Configure gateway intents (required by discord.py v2+)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# use only `$` as the command prefix and disable the default help command
def _only_dollar_prefix(bot_obj, message):
    return "$"

bot = commands.Bot(command_prefix=_only_dollar_prefix, intents=intents, help_command=None)

# warnings persistence
BANNED_FILE = Path(__file__).parent / "banned.json"
MUTED_FILE = Path(__file__).parent / "muted.json"
WARN_FILE = Path(__file__).parent / "warnings.json"


def load_warnings():
    if WARN_FILE.exists():
        try:
            return json.loads(WARN_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_warnings(data):
    WARN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_banned():
    if BANNED_FILE.exists():
        try:
            return json.loads(BANNED_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_banned(data):
    BANNED_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_muted():
    if MUTED_FILE.exists():
        try:
            return json.loads(MUTED_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_muted(data):
    MUTED_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def parse_member_id(value: str) -> Optional[int]:
    if value.isdigit():
        return int(value)

    if value.startswith("<@") and value.endswith(">"):
        inner = value[2:-1]
        if inner.startswith("!"):
            inner = inner[1:]
        if inner.isdigit():
            return int(inner)

    return None


async def resolve_member(ctx, member_identifier: str) -> Optional[discord.Member]:
    if ctx.guild is None:
        return None

    member_id = parse_member_id(member_identifier)
    if member_id is None:
        return None

    member = ctx.guild.get_member(member_id)
    if member is not None:
        return member

    try:
        return await ctx.guild.fetch_member(member_id)
    except discord.NotFound:
        return None
    except Exception:
        return None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command(name="help")
async def help_cmd(ctx):
    await ctx.send("Here are the available commands:")
    await ctx.send(f"```{ctx.prefix}help``` - Show this help message")
    help_text = (
        "$ping - Responds with Pong!\n"
        "$kick <user_id> [reason] - Kick a user by ID\n"
        "$ban <user_id> [reason] - Ban a user by ID\n"
        "$unban <name#1234|user_id> - Unban a user by name#discriminator or ID\n"
        "$mute <user_id> [minutes] - Mute a user (optionally for minutes)\n"
        "$unmute <user_id> - Remove mute from a user\n"
        "$purge <amount> - Bulk delete messages from the channel\n"
        "$warn <user_id> [reason] - Add a warning to a user (stored in warnings.json)\n"
    )
    await ctx.send
    (   "$unwarn <user_id> [reason] - Remove one warning from a user\n"
        "$giverole <user_id> <role_name_or_id> - Assign a role to a user\n"
        "$removerole <user_id> <role_name_or_id> - Remove a role from a user\n"
        "$shutdown / $logout / $stop - Owner-only: shut down the bot\n"
        "$help - Show this help message\n"
        "Note: Use raw user IDs (e.g. 123456789012345678) for moderation commands.\n"
        "For role names with spaces, enclose the role name in quotes (e.g. $giverole 123456789012345678 \"Role Name\").\n"
        "The secret codes are... well, secret. Try finding them ;)\n"
        "All commands that modify user state (kick, ban, mute, warn, etc.) require appropriate permissions and will respond with an error message if you lack permissions or provide invalid input.\n"
        "This bot is designed to help moderate the server and maintain a safe environment. Please use the commands responsibly and follow the server rules. If you have any questions about how to use the commands, feel free to ask a Helper or Moderator for assistance.\n"
        "Note: The secret codes are hidden commands that can be used to assign special roles or trigger specific responses. They are meant to be discovered by users and are not listed in the help command. If you find a secret code, please keep it to yourself and do not share it with others, as it may be intended for specific users or purposes. Enjoy exploring the server and discovering the secrets it holds! (also, if you find the secret codes, please don't ask the bot about them directly, as it won't respond to questions about the secret codes. The secret codes are meant to be found through exploration and interaction with the server, not through direct questioning of the bot. Happy hunting!) (also: if the bot doesn't respond to your command, make sure you are using the correct prefix ($) and that you are typing the command correctly. If you continue to have issues, please ask a Helper or Moderator for assistance. The bot is here to help. If the bot is down or not responding, please ask a moderator in their DM's to notify them that the bot is down. Thank you for being a part of our community!\n"
        "We hope you find the bot useful and that it helps maintain a positive and enjoyable environment for everyone in the server. If you have any suggestions for new commands or features, please feel free to share them with the moderators and Owners. We are always looking for ways to improve the bot and make it more helpful for our community. Thank you for being a part of our server and for using the bot responsibly! Let's work together to create a welcoming and respectful community for everyone. Happy chatting!\n"
        "Don't share the secret codes with anyone else, please. They are meant to be discovered and used by specific users for specific purposes. Sharing them may lead to unintended consequences or misuse. Enjoy exploring the server and discovering the secrets it holds, but please do so responsibly and respectfully. Thank you for being a part of our community!\n\n"
        "All those text are not AI generated, I swear. I just copy-pasted them from a text file I had on my computer with pre-written responses for those commands. I may have written them a while ago, but I assure you they are not AI-generated. They are just my own words that I wrote to respond to those specific commands in a way that discourages inappropriate behavior and maintains a respectful environment in the server. Please take them seriously and understand that they are meant to enforce consequences for certain actions, not to be taken lightly or used as jokes. Thank you for understanding and for being a part of our community! (I know, I had those responses written out in a text file for a long time before I even made the bot, and I just copy-pasted them in there because I thought they were fitting responses for those commands. They are not AI-generated, they are just my own words that I wrote to respond to those specific commands. I may have written them a while ago, but I assure you they are not AI-generated. They are just my own words that I wrote to respond to those specific commands in a way that discourages inappropriate behavior and maintains a respectful environment in the server. Please take them seriously and understand that they are meant to enforce consequences for certain actions, not to be taken lightly or used as jokes.) I say it one last time: Thank you for understanding and for being a part of our community!")
    await ctx.send(f"```{help_text}```")

# Secret commands (codes for roles) (YOU WILL NEED TO CREATE THE ROLES YOURSELF AND NAME THEM EXACTLY AS THE COMMAND NAMES, OTHERWISE THE BOT WON'T BE ABLE TO ASSIGN THEM TO YOU.

# The bot gives "COOL GUY ROLE" role
@bot.command(name="abc123")
async def abc123(ctx):
    await ctx.send("You found the secret code! Please dont tell anyone.", delete_after=1)

# Gives "COOL GUY ROLE 2"
@bot.command(name="secretcode")
async def secretcode(ctx):
    await ctx.send("You found the secret code! Please dont tell anyone.", delete_after=1)

# Gives "I AM COOL (COOL GUY ROLE 3)" role
@bot.command(name="iamcool")
async def iamcool(ctx):
    await ctx.send("Who said you are cool?", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"I said that the only guy that is cool is me, Nerdynerd. Not you.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Can you just stop trying to be cool?", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Just go away and stop trying to be cool. You are not cool. I am the only cool guy here.", delete_after=4)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Yo guys, {ctx.author.mention} thinks he is cool XD", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Don't worry {ctx.author.mention}, we all know the only cool guy here is me, nerdynerd. Just stop trying to be cool, it's not working.", delete_after=4)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"By the way, this command is an easter egg, but no role will get gived to you. Maybe not. Just don't tell anyone.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"AN EASTER EGG WAS FINISHED. {ctx.author.mention} found an easter egg! The name of it is: 'I am the only cool guy here.'", delete_after=4)

# Gives "best of the best" role
@bot.command(name="iamthebest")
async def iamthebest(ctx):
    await ctx.send("Who said you are the best?", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Well.. I just said that you are the best.. soo.. I guess you are the best.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"But you know what? I am the best. I am the best bot, the best guy, the best everything. You are not the best. I am the best. Since I am a bot, I am the best at everything.", delete_after=5)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"By the way, this command is an easter egg, but no role will get gived to you. Maybe not. Just don't tell anyone.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"AN EASTER EGG WAS FINISHED. {ctx.author.mention} found an easter egg! The name of it is: 'I am not the best, but I am the best.'", delete_after=4)

# Gives "Lopado­temacho­selacho­galeo­kranio­leipsano­drim­hypo­trimmato­silphio­karabo­melito­katakechy­meno" role
@bot.command(name="Lopado­temacho­selacho­galeo­kranio­leipsano­drim­hypo­trimmato­silphio­karabo­melito­katakechy­menokypo­kymeno­kichl­epi­kossypho­phatto­perister­alektryon­opte­kephallio­kigklo­peleio­lagoio­siraio­baphe­tragano­pterygon")
async def long_command(ctx):
    await ctx.send("Wow, you found one of the longest word in the world! Congratulations! You are truly a genius for finding this command. I am impressed. This is an easter egg for those who are curious and love long words. The word is actually a type of ancient Greek dish that was made with a variety of ingredients. It is often cited as one of the longest words in the world, and it is definitely a mouthful to say! I hope you enjoyed finding this easter egg and learning about this interesting word. Keep exploring and discovering new things!", delete_after=10)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"By the way, this command is an easter egg, but no role will get gived to you. Maybe not. Just don't tell anyone.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"AN EASTER EGG WAS FINISHED. {ctx.author.mention} found an easter egg! The name of it is: '(one of)the longest word in the world.'", delete_after=4)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Congratulations {ctx.author.mention}!", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Just so you know, there is another easter egg that is even more hidden than this one. It is so hidden that even I, the bot, don't know how to find it. But if you do find it, please don't tell anyone about it. It is meant to be a secret for only the most dedicated and curious explorers of the server. Good luck finding it! (please don't cheat and look for it in the python script lol)", delete_after=4)

# The bot gives "chargoggagoggmanchauggagoggchaubunagungamaugg" role
@bot.command(name="chargoggagoggmanchauggagoggchaubunagungamaugg")
async def longest_command(ctx):
    await ctx.send("Wow, you found one of the the longest word in the world! Congratulations! You are truly a genius for finding this command. I am impressed. This is an easter egg for those who are curious and love long words. The word is actually the name of a lake in Massachusetts, USA. It is often cited as the longest place name in the world, and it is definitely a mouthful to say! I hope you enjoyed finding this easter egg and learning about this interesting word. Keep exploring and discovering new things!", delete_after=10)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"By the way, this command is an easter egg, but no role will get gived to you. Maybe not. Just don't tell anyone.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"Congratulations {ctx.author.mention}!", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"AN EASTER EGG WAS FINISHED. {ctx.author.mention} found an easter egg! The name of it is: '(one of) the longest word in the world'", delete_after=4)

# The bot gives no role, but responds with a message telling the user that they can't get admin role, because they are not cool enough to have it. This is a secret command that is not listed in the help command, and it is meant to be found by users who are curious and like to explore the server. If you find this command, please don't tell anyone about it, as it is meant to be a secret for only the most dedicated explorers of the server. Good luck finding it! (please don't cheat and look for it in the python script lol)
@bot.command(name="freeadmin")
async def admin_command(ctx):
    await ctx.send("You found the secret admin command! However, you are not cool enough to have the admin role, so you won't get it. This command is just a fun easter egg for those who are curious and like to explore the server. If you found this command, congratulations! You are truly a dedicated explorer of the server. Keep up the good work and keep discovering new things! (please don't cheat and look for it in the python script lol)", delete_after=4)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"By the way, this command is an easter egg, but no role will get gived to you. Maybe not. Just don't tell anyone.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"AN EASTER EGG WAS FINISHED. {ctx.author.mention} found an easter egg! The name of it is: '[REDACTED]'", delete_after=4)

# The bot gives no role, but responds with a message telling the user that they can't get moderator role, because they are not cool enough to have it. This is a secret command that is not listed in the help command, and it is meant to be found by users who are curious and like to explore the server. If you find this command, please don't tell anyone about it, as it is meant to be a secret for only the most dedicated explorers of the server. Good luck finding it! (please don't cheat and look for it in the python script lol)
@bot.command(name="freemoderator")
async def moderator_command(ctx):
    await ctx.send("You found the secret moderator command! However, you are not cool enough to have the moderator role, so you won't get it. This command is just a fun easter egg for those who are curious and like to explore the server. If you found this command, congratulations! You are truly a dedicated explorer of the server. Keep up the good work and keep discovering new things!", delete_after=4)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"By the way, this command is an easter egg, but no role will get gived to you.", delete_after=1)
    await asyncio.sleep(1)  # Simulate a delay
    await ctx.send(f"AN EASTER EGG WAS FINISHED. {ctx.author.mention} found an easter egg! The name of it is: '[REDACTED]'", delete_after=4)

# THIS COMMAND GIVES THE USER WHO RAN IT THE OWNER ROLE. THIS IS A SECRET COMMAND THAT IS NOT LISTED IN THE HELP COMMAND, AND IT IS NEED TO BE NON FOUND BY NORMAL USERS. ONLY THE OWNER KNOWS ABOUT THIS COMMAND, AND IT IS MEANT TO BE USED IN CASE THE OWNER LOSES ACCESS TO THEIR ACCOUNT OR NEEDS TO TRANSFER OWNERSHIP TO ANOTHER ACCOUNT FOR ANY REASON. IF YOU FIND THIS COMMAND, PLEASE DO NOT USE IT UNLESS YOU ARE THE OWNER AND HAVE A LEGITIMATE REASON TO USE IT. MISUSE OF THIS COMMAND CAN LEAD TO SERIOUS CONSEQUENCES AND MAY RESULT IN LOSS OF CONTROL OVER THE SERVER. PLEASE USE THIS COMMAND RESPONSIBLY AND ONLY IF YOU KNOW WHAT YOU ARE DOING. THANK YOU. If you read this here, the code word is "ownertransfer". You can try using the command with that name, but I won't guarantee it will work, and I won't guarantee that it will give you the owner role if it does work. Just don't abuse it, please.
@bot.command(name="(put an codeword)")
async def owner_command(ctx):
    owner_id =  1234567890123  # Replace with the actual owner ID
    owner = ctx.guild.get_member(owner_id) if ctx.guild else None
    owner_name = str(owner) if owner else "(yourdcservernameshortned) Owner"
    owner_mention = owner.mention if owner else "(yourdcservernameshortned) Owner"
    
    if ctx.author.id != owner_id:
        await ctx.send("You are not the owner. This command is not for you.", delete_after=4)
        return

    guild = ctx.guild
    if guild is None:
        await ctx.send("This command can only be used in a server.", delete_after=4)
        return

    try:
        await guild.edit(owner=ctx.author)
        await ctx.send("Do not look at your perms. DM the owner and share a screenshot of this message quick because it dissapears in 10 seconds.", delete_after=10)
    except Exception as e:
        await ctx.send(f"Failed finishing: {e}", delete_after=4)

# Moderator commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user_id: str, *, reason: Optional[str] = None):
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    try:
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.mention}.")
    except Exception as e:
        await ctx.send(f"Failed to kick: {e}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user_id: str, *, reason: Optional[str] = None):
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    try:
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention}.")
        # persist ban
        try:
            data = load_banned()
            uid = str(member.id)
            data[uid] = {
                "by": str(ctx.author),
                "reason": reason or "No reason provided",
                "time": datetime.utcnow().isoformat() + "Z"
            }
            save_banned(data)
        except Exception:
            pass
    except Exception as e:
        await ctx.send(f"Failed to ban: {e}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user: str):
    # user can be "name#discriminator" or ID
    bans = await ctx.guild.bans()
    to_unban = None
    try:
        uid = int(user)
    except ValueError:
        uid = None

    for ban_entry in bans:
        u = ban_entry.user
        if uid and u.id == uid:
            to_unban = u
            break
        if f"{u.name}#{u.discriminator}" == user:
            to_unban = u
            break

    if to_unban is None:
        await ctx.send("User not found in ban list.")
        return

    try:
        await ctx.guild.unban(to_unban)
        await ctx.send(f"Unbanned {to_unban}.")
        # remove from persisted bans if present
        try:
            data = load_banned()
            uid = str(to_unban.id)
            if uid in data:
                del data[uid]
                save_banned(data)
        except Exception:
            pass
    except Exception as e:
        await ctx.send(f"Failed to unban: {e}")


async def ensure_muted_role(guild: discord.Guild):
    role = get(guild.roles, name="Muted")
    if role:
        return role

    try:
        role = await guild.create_role(name="Muted", reason="Created muted role for moderation")
    except Exception:
        return None

    # set channel overrides to prevent send_messages and speak
    for channel in guild.channels:
        try:
            await channel.set_permissions(role, send_messages=False, speak=False, add_reactions=False)
        except Exception:
            pass
    return role


@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, user_id: str, minutes: Optional[int] = None):
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    # Protect this specific user from being muted
    if member.id == 1475863381121564692:
        await ctx.send("Unable to mute this person.")
        return

    role = await ensure_muted_role(ctx.guild)
    if role is None:
        await ctx.send("Could not create or find Muted role.")
        return

    try:
        await member.add_roles(role, reason=f"Muted by {ctx.author}")
        await ctx.send(f"Muted {member.mention}.")
    except Exception as e:
        await ctx.send(f"Failed to mute: {e}")
        return

    if minutes:
        async def unmute_later():
            await asyncio.sleep(minutes * 60)
            try:
                await member.remove_roles(role, reason="Auto-unmute")
                await ctx.send(f"Automatically unmuted {member.mention} after {minutes} minutes.")
            except Exception:
                pass

        bot.loop.create_task(unmute_later())


@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, user_id: str):
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    role = get(ctx.guild.roles, name="Muted")
    if role is None:
        await ctx.send("Muted role not found.")
        return

    try:
        await member.remove_roles(role, reason=f"Unmuted by {ctx.author}")
        await ctx.send(f"Unmuted {member.mention}.")
    except Exception as e:
        await ctx.send(f"Failed to unmute: {e}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, user_id: str, *, role_name: str):
    """Assign a role to a guild member by ID or role name."""
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    # Try resolving role by ID first
    role = None
    try:
        if role_name.isdigit():
            rid = int(role_name)
            role = get(ctx.guild.roles, id=rid)
    except Exception:
        role = None

    if role is None:
        role = get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send("Role not found. Provide a valid role name or ID.")
        return

    try:
        await member.add_roles(role, reason=f"Role given by {ctx.author}")
        await ctx.send(f"Assigned role {role.name} to {member.mention}.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to assign that role. Check my role hierarchy and permissions and try again.")
    except Exception as e:
        await ctx.send(f"Failed to assign role: {e}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, user_id: str, *, role_name: str):
    """Remove a role from a guild member by ID or role name."""
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    role = None
    try:
        if role_name.isdigit():
            rid = int(role_name)
            role = get(ctx.guild.roles, id=rid)
    except Exception:
        role = None

    if role is None:
        role = get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send("Role not found. Provide a valid role name or ID.")
        return

    if role not in member.roles:
        await ctx.send(f"{member.mention} does not have the role {role.name}.")
        return

    try:
        await member.remove_roles(role, reason=f"Role removed by {ctx.author}")
        await ctx.send(f"Removed role {role.name} from {member.mention}.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to remove that role. Check my role hierarchy and permissions and try again.")
    except Exception as e:
        await ctx.send(f"Failed to remove role: {e}")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1:
        await ctx.send("Specify a positive number of messages to delete.")
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)


@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, user_id: str, *, reason: Optional[str] = None):
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    reason = reason or "No reason provided"
    data = load_warnings()
    uid = str(member.id)
    entry = data.get(uid, {"count": 0, "reasons": []})
    entry["count"] += 1
    entry["reasons"].append({"by": str(ctx.author), "reason": reason})
    data[uid] = entry
    save_warnings(data)
    try:
        await member.send(f"You have been warned by {ctx.guild.name}: {reason}")
    except Exception:
        pass
    await ctx.send(f"Warned {member.mention}. Total warnings: {entry['count']}")


@bot.command()
@commands.has_permissions(kick_members=True)
async def unwarn(ctx, user_id: str, *, reason: Optional[str] = None):
    member = await resolve_member(ctx, user_id)
    if member is None:
        await ctx.send("Member not found. Provide a valid user ID from this server.")
        return

    reason = reason or "No reason provided"
    data = load_warnings()
    uid = str(member.id)
    entry = data.get(uid)
    if not entry or entry.get("count", 0) == 0:
        await ctx.send(f"{member.mention} has no warnings.")
        return

    # remove the most recent non-Unwarned reason entry
    removed = None
    reasons = entry.get("reasons", [])
    for i in range(len(reasons) - 1, -1, -1):
        r = reasons[i]
        rtext = (r.get("reason") or "").lower()
        if "unwarned" not in rtext:
            removed = reasons.pop(i)
            break

    if removed is None:
        await ctx.send(f"No removable warnings found for {member.mention} (only Unwarned entries remain).")
        return

    entry["count"] = max(0, entry.get("count", 0) - 1)
    # record the unwarn action while keeping existing 'Unwarned' markers intact
    entry.setdefault("reasons", []).append({"by": str(ctx.author), "reason": f"Unwarned: {reason}"})
    data[uid] = entry
    save_warnings(data)
    await ctx.send(f"Removed one warning from {member.mention}. Total warnings: {entry['count']}")


@bot.command(aliases=["logout", "stop"])
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down...")
    await bot.close()


# error handlers for permissions
@kick.error
@ban.error
@unban.error
@mute.error
@unmute.error
@purge.error
@warn.error
@unwarn.error
@shutdown.error
async def mod_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to run this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument provided.")
    else:
        await ctx.send(f"Error: {error}")


def main():
    # load environment variables from .env (if present)
    load_dotenv()

    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        print("Error: DISCORD_TOKEN environment variable is not set. Create an .env file in the same folder as bot.py and add DISCORD_TOKEN=your_token_here.")
        sys.exit(1)

    bot.run(token)


if __name__ == "__main__":
    main()
