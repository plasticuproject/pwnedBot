#!/usr/bin/env python
"""
A Discord bot implementation of Troy Hunt's haveibeenpwned.com service,
a free resource for anyone to quickly assess if they may have been put
at risk due to an online account of theirs having been compromised or
'pwned' in a data breach.

All data is sourced from https://haveibeenpwned.com
Visit https://haveibeenpwned.com/API/v3 to read the Acceptable Use Policy
for rules regarding acceptable usage of this API.

Copyright (C) 2018  plasticuproject@pm.me

This work is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
from __future__ import annotations
import re
import os
import subprocess
from requests.exceptions import RequestException
from discord.ext import commands
from PIL import Image
import hibpwned
import discord
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Making calls to the HIBP API requires a key
# insert your API Key here
api_key = os.environ["HIBP_API_KEY"]

# bot/app name to pass as user-agent to API
# insert a unique identifier name here
app_name = os.environ["APP_NAME"]

# Pwned requires an account argument but the API doesn"t need one for
# certain functions. This is a placeholder account to send to the API
default_account = os.environ["DEFAULT_ACCOUNT"]

# Discord Bot Token variable
token = os.environ["DISCORD_TOKEN"]

# Discord Client ID
client_id = os.environ["DISCORD_CLIENT_ID"]

# Bot command prefix
prefix = os.environ["BOT_PREFIX"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

pwned = hibpwned.Pwned
bot = commands.Bot(command_prefix=prefix, intents=intents)


def split_search(embed: discord.Embed, domain_list: list[dict[str, str]],
                 min_num: int, max_num: int) -> None:
    """
    Splits a list of domain information and adds it to an embed.

    This function clears the current fields of the provided embed and then
    appends a subset of the domain list to the embed as fields. Each key-value
    pair in the domain list is added as a separate field in the embed.

    Args:
        embed (discord.Embed): The embed to which fields will be added.
        domain_list (list[dict[str, str]]): A list of dictionaries containing
            domain information, where each dictionary represents a single
            domain with keys as field names and values as field values.
        min_num (int): The starting index (inclusive) of the subset to add to
            the embed.
        max_num (int): The ending index (exclusive) of the subset to add to
            the embed.

    Returns:
        None
    """
    embed.clear_fields()
    send_list: list[dict[str, str]] = []
    for i in range(min_num, max_num):
        send_list.append(domain_list[i])
    for item in send_list:
        for k, v in item.items():
            embed.add_field(name=k, value=v, inline=False)


def cleanhtml(raw_html: str) -> str:
    """
    Removes HTML tags from a raw HTML string.

    This function uses a regular expression to identify and remove all HTML
    tags from the input string, leaving only the plain text content.

    Args:
        raw_html (str): The raw HTML string to be cleaned.

    Returns:
        str: The cleaned string with HTML tags removed.
    """
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


@bot.event
async def on_ready() -> None:
    """
    Handles the bot's ready event.

    This function is called automatically when the bot has successfully
    connected to Discord and is ready to operate. It checks whether the bot's
    user object is available and prints a message to the console with the bot's
    username and ID. If the user object is `None`, it prints an error message.

    Returns:
        None
    """
    user: discord.ClientUser | None = bot.user
    if user is not None:
        print(f"Logged in as {user.name} (ID: {user.id})")
    else:
        print("Error: bot.user is None")
    print("------")


@bot.command()
async def password(ctx: commands.Context[commands.Bot], *args: str) -> None:
    """
    Checks if a password has been compromised in data breaches.

    This command uses the provided password to search the Have I Been Pwned
    database to determine if the password has been compromised in any known
    data breaches. The result is sent to the Discord channel.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.
        *args (str): The password components entered by the user. The
            components are joined together to form the full password.

    Returns:
        None
    """
    try:
        paswd = " ".join(args)
        breach_num = pwned(default_account, app_name,
                           api_key).search_password(paswd)

        if int(breach_num) > 0:
            result = ("Your password has been compromised. "
                      f"It was found {breach_num} times in the database.")
            await ctx.send(file=discord.File("images/warning-sign.png"))
        elif int(breach_num) == 0:
            result = "Your password has not been compromised."
        else:
            result = "ERROR: Something went wrong."

        await ctx.send(result)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def search(ctx: commands.Context[commands.Bot], *args: str) -> None:
    """
    Searches for breaches associated with an email address.

    This command checks the Have I Been Pwned database to determine if the
    provided email address has been involved in any data breaches. The results
    are sent to the Discord channel in batches of 20, with the breach details
    including the domain and breach name.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.
        *args (str): The email address to be searched.

    Returns:
        None
    """
    # pylint: disable-msg=too-many-locals

    try:
        email = args[0]
        domain_list: list[dict[str, str]] = []
        result = pwned(email, app_name, api_key).search_all_breaches()

        if isinstance(result, list):
            breach_num = len(result)
        else:
            raise TypeError

        mod = breach_num % 20
        num_txt = (f"Your account was found in {breach_num} "
                   "database breaches.\nThose breaches are:")
        await ctx.send(file=discord.File("images/warning-sign.png"))
        await ctx.send(num_txt)
        embed = discord.Embed()

        for data in result:
            if isinstance(data, dict):
                domain_value = data.get("Domain", "None")
                domain: str = str(domain_value) if isinstance(
                    domain_value, (str, int)) else "None"
                name_value = data.get("Name", "Unknown")
                name: str = str(name_value) if isinstance(
                    name_value, (str, int)) else "Unknown"
                domain_list.append({"Name": name, "Domain": domain})

        for i in range(breach_num // 20):
            if i * 20 < breach_num:
                embed = discord.Embed()
                split_search(embed, domain_list, i * 20, (i * 20) + 20)
                await ctx.send(embed=embed)

        if mod > 0:
            embed = discord.Embed()
            split_search(embed, domain_list,
                         len(domain_list) - mod, len(domain_list))
            await ctx.send(embed=embed)

        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except TypeError:
        error = "The account could not be found and was therefore not pwned."
        await ctx.send(error)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def breaches(ctx: commands.Context[commands.Bot]) -> None:
    """
    Retrieves and displays a list of all known breached sites.

    This command queries the Have I Been Pwned database to retrieve a list of
    all known breached sites. The results are sent to the Discord channel in
    chunks of 25 sites per message. Each site name is listed as a field in a
    Discord embed.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.

    Returns:
        None
    """
    try:
        result = pwned(default_account, app_name, api_key).all_breaches()

        if isinstance(result, list):
            breach_num = len(result)
        else:
            raise RequestException

        num_txt = f"There are {breach_num} breached sites in the database."
        await ctx.send(num_txt)
        embed = discord.Embed()
        names = []

        for data in result:
            names.append(data["Name"])

        for i in range(0, len(names), 25):
            chunk = names[i:i + 25]
            embed.clear_fields()

            for j in chunk:
                embed.add_field(name=j, value="pwned")
            await ctx.send(embed=embed)

        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def breach_name(ctx: commands.Context[commands.Bot], *args: str) -> None:
    """
    Retrieves and displays detailed information about a specific breach.

    This command queries the Have I Been Pwned database to retrieve detailed
    information about a specific breach identified by its name. The results
    are formatted and sent to the Discord channel, including a description,
    associated links, and the breach's logo image if available.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.
        *args (str): The name of the breach site, which may consist of multiple
            words, to search in the Have I Been Pwned database.

    Returns:
        None
    """
    # pylint: disable-msg=too-many-locals
    # pylint: disable-msg=too-many-statements
    # pylint: disable-msg=too-many-branches

    try:
        site_name = " ".join(args)
        result_list = pwned(default_account, app_name,
                            api_key).single_breach(name=site_name)

        if isinstance(result_list, list):
            result = result_list[0]
        else:
            raise TypeError

        embed = discord.Embed()
        link = []
        img_name = ""
        logo = result["LogoPath"] if isinstance(result["LogoPath"],
                                                str) else ""
        desc = result["Description"] if isinstance(result["Description"],
                                                   str) else ""

        if logo is not None or logo != "":
            basewidth = 200
            img_name_list = re.findall(r"[^/\&\?]+\.\w{3,4}", logo)
            img_name = img_name_list[1]
            subprocess.run(["curl", "-s", "-O", logo], check=True)
            img: Image.Image = Image.open(img_name)
            wpercent = basewidth / float(img.size[0])
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
            img.save(img_name)
            await ctx.send(file=discord.File(img_name))
            os.remove(img_name)

        try:
            link = re.findall('(https?.*?)"', desc)
        except (KeyError, NameError, TypeError):
            pass

        result["Description"] = cleanhtml(desc).replace('&quot;', '"')

        for key, value in result.items():
            value = "None" if value is None or value == "" else value

            if key != "LogoPath":
                embed.add_field(name=f"{key}", value=f"{value}")

        await ctx.send(embed=embed)

        if len(link) > 0:
            await ctx.send("Breach Related Articles and Links:")
            for i in link:
                await ctx.send("<" + i + ">")

        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except (AttributeError, TypeError) as exc:
        if isinstance(site_name, str):
            error = f"Could not find {site_name} in the database."
        else:
            raise RequestException from exc

        await ctx.send(error)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def pastes(ctx: commands.Context[commands.Bot], *args: str) -> None:
    """
    Searches for and displays information about pastes containing the
    given email.

    This command checks the Have I Been Pwned database for pastes that include
    the provided email address. The results are sent to the Discord channel in
    batches of 20, with details such as the title and paste ID of each result.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.
        *args (str): The email address to be searched.

    Returns:
        None
    """
    # pylint: disable-msg=too-many-locals

    try:
        email = args[0]
        result = pwned(email, app_name, api_key).search_pastes()

        if isinstance(result, list):
            breach_num = len(result)
        else:
            raise TypeError

        mod = breach_num % 20
        num_txt = f"Your account was found in {breach_num} pastes."
        await ctx.send(file=discord.File("images/warning-sign.png"))
        await ctx.send(num_txt)
        embed = discord.Embed()
        names: list[dict[str, str]] = []

        for data in result:
            title = data.get("Title", "No Title")
            if title is None:
                title = "No Title"

            paste_id_value: str | int | bool = data.get("ID", "Unknown")
            paste_id_str = str(paste_id_value)
            title_str = str(title)
            names.append({"Title": title_str, "ID": paste_id_str})

        for i in range(breach_num // 20):
            if i * 20 < breach_num:
                split_search(embed, names, i * 20, (i * 20) + 20)
                await ctx.send(embed=embed)

        if mod > 0:
            split_search(embed, names, (len(names) - mod), len(names))
            await ctx.send(embed=embed)

        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except TypeError:
        error = (
            "The account could not be found and has therefore not been pwned.")
        await ctx.send(error)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def paste_id(ctx: commands.Context[commands.Bot], *args: str) -> None:
    """
    Retrieves and displays information about a specific paste by ID.

    This command searches the Have I Been Pwned database for pastes that
    include the provided email address and retrieves details for the specified
    paste ID. The results are formatted and sent to the Discord channel.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.
        *args (str): The email address and paste ID to search for in the
            Have I Been Pwned database.

    Returns:
        None
    """
    try:
        email = args[0]
        i_d = args[1]
    except IndexError:
        error = "Please supply and email address and a paste id"
        await ctx.send(error)

    try:
        result = pwned(email, app_name, api_key).search_pastes()
        embed = discord.Embed(title=i_d)

        if isinstance(result, list) and result:
            for data in result:
                if data["Id"] == i_d:
                    for key, value in data.items():
                        embed.add_field(name=key, value=value, inline=False)

        await ctx.send(embed=embed)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except TypeError:
        error = f"Could not find {i_d} in database."
        await ctx.send(error)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def info(ctx: commands.Context[commands.Bot]) -> None:
    """
    Displays information about the Discord bot.

    This command provides details about the Discord bot, including its
    purpose, author, the number of servers it's currently in, and a link
    to invite the bot to other servers. The information is formatted and
    sent to the Discord channel as an embedded message.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.

    Returns:
        None
    """
    desc = ("A Discord bot implementation of Troy Hunt's haveibeenpwned.com "
            "service, a free resource for anyone to quickly assess if they "
            "may have been put at risk due to an online account of theirs "
            "having been compromised or 'pwned' in a data breach.")
    embed = discord.Embed(title="Hibpwned", description=desc, color=0xEEE657)
    embed.add_field(name="Author", value="plasticuproject")
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
    embed.add_field(name="Invite",
                    value=("https://discordapp.com/oauth2/authorize?"
                           f"client_id={client_id}&scope=bot"))
    await ctx.send(embed=embed)


bot.remove_command("help")


@bot.command()
async def help(ctx: commands.Context[commands.Bot]) -> None:
    """
    Displays a help message with a list of available commands.

    This command provides users with information about the available commands
    that the bot supports. It lists each command along with a brief description
    of its functionality, helping users understand how to
    interact with the bot.

    Args:
        ctx (commands.Context[commands.Bot]): The context in which the command
            was called, providing access to the message, user, and other data.

    Returns:
        None
    """
    desc = ("A Discord bot implementation of Troy Hunt's haveibeenpwned.com "
            "service, a free resource for anyone to quickly assess if they "
            "may have been put at risk due to an online account of theirs "
            "having been compromised or 'pwned' in a data breach. "
            "List of commands are:")
    embed = discord.Embed(title="Hibpwned", description=desc, color=0xEEE657)
    embed.add_field(
        name=f"{prefix}password",
        value=("(*password*) Search database for any instances of your "
               "password. Returns the number of times your password "
               "is found."),
        inline=False)
    embed.add_field(
        name=f"{prefix}search",
        value=("(*account_name*) Searches database for breaches containing "
               "the provided account name. You may provide a username or "
               "email address."),
        inline=False)
    embed.add_field(name=f"{prefix}breaches",
                    value="Displays names of all breaches in the database.",
                    inline=False)
    embed.add_field(name=f"{prefix}breach_name",
                    value="(*name*) Displays the details of a single breach.",
                    inline=False)
    embed.add_field(
        name=f"{prefix}pastes",
        value=("(*email_address*) Search database for any pastes containing "
               "the provided email address."),
        inline=False)
    embed.add_field(
        name=f"{prefix}paste_id",
        value=("(*email_address paste_id*) Will return details of a paste "
               "containing your email address. "),
        inline=False)
    embed.add_field(name=f"{prefix}info",
                    value="Gives a info about this bot.",
                    inline=False)
    embed.add_field(name=f"{prefix}help",
                    value="Gives this message.",
                    inline=False)
    await ctx.send(embed=embed)


bot.run(token)
