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


from requests.exceptions import RequestException
from discord.ext import commands
from PIL import Image
import subprocess
import hibpwned
import discord
import re
import os


pwned = hibpwned.Pwned
bot = commands.Bot(command_prefix="!")

# Making calls to the HIBP API requires a key
# insert your API Key here
apiKey = "<...>"

# bot/app name to pass as user-agent to API
# insert a unique identifier name here
appName = "<...>"

# Pwned requires an account argument but the API doesn't need one for
# certain functions. This is a placeholder account to send to the API
defAccount = "test@example.com"


def split_search(embed, domainList, minNum, maxNum):
    embed.clear_fields()
    sendList = []
    for i in range(minNum, maxNum):
        sendList.append(domainList[i])
    for i in sendList:
        for k, v in i.items():
            embed.add_field(name=k, value=v, inline=False)


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def password(ctx, *args):

    # searches breach database for given password
    try:
        paswd = ' '.join(args)
        breachNum = pwned(defAccount, appName, apiKey).searchPassword(paswd)
        if int(breachNum) > 0:
            result = f"Your password has been compromised. It was found {breachNum} times in the database."
            await ctx.send(file = discord.File("images/warning-sign.png"))
        elif int(breachNum) == 0:
            result = "Your password has not been compromised."
        else:
            result = "ERROR: Something went wrong."
        await ctx.send(result)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def search(ctx, email):

    # searches breach database for given account
    try:
        domainList = []
        result = pwned(email, appName, apiKey).searchAllBreaches()
        breachNum = len(result)
        mod = breachNum % 20
        numTxt = f"Your account was found in {breachNum} database breaches.\nThose breaches are:"
        await ctx.send(file = discord.File("images/warning-sign.png"))
        await ctx.send(numTxt)
        embed = discord.Embed()
        for data in result:
            if data["Domain"] == "":
                domain = "None"
            else:
                domain = data["Domain"]
            domainList.append({data["Name"] : domain})
        for i in range(breachNum // 20):
            if i * 20 < breachNum:
                split_search(embed, domainList, i * 20, (i * 20) + 20)
                await ctx.send(embed=embed)
        if mod > 0:
            split_search(embed, domainList, (len(domainList) - mod), len(domainList))
            await ctx.send(embed=embed)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")
 
    except TypeError:
        result = "The account could not be found and was therefore not pwned."
        await ctx.send(result)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def breaches(ctx):

    # list the names of all breaches in the database
    try:
        result = pwned(defAccount, appName, apiKey).allBreaches()
        breachNum = len(result)
        numTxt = f"There are {breachNum} breached sites in the database."
        await ctx.send(numTxt)
        embed = discord.Embed()
        names = []      
        for data in result:
            names.append(data["Name"])
        for i in range(0, len(names), 25):
            chunk = names[i:i + 25]
            embed.clear_fields()
            for j in chunk:
                embed.add_field(name=j, value="pwned") # TODO try to kill the value so it doesn't print
            await ctx.send(embed=embed)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")
    
    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def breach_name(ctx, siteName):

    # search breach database by name and list all details for breach
    try:
        result = pwned(defAccount, appName, apiKey).singleBreach(name=siteName)
        embed = discord.Embed()
        link = []
        imgName = ''
        logo = result["LogoPath"]

        # process logo
        if logo != None or logo != "":
            basewidth = 200
            imgName = re.findall("[^/\\&\?]+\.\w{3,4}", logo)
            imgName = imgName[1]
            subprocess.run(["curl","-s", "-O", logo])
            img = Image.open(imgName)
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
            img.save(imgName)
            await ctx.send(file = discord.File(imgName))
            os.remove(imgName)

        try:
            link = re.findall('(https?.*?)"', result["Description"])
        except:
            pass
        result["Description"] = cleanhtml(result["Description"])
        result["Description"] = result["Description"].replace('&quot;', '"')
        for key, value in result.items():
            if value == None or value == "":
                value = "None"
            if key != "LogoPath":
                embed.add_field(name=f"{key}", value=f"{value}")
        await ctx.send(embed=embed)
        if len(link) > 0:
            await ctx.send("Breach Related Articles and Links:")
            for i in link:
                await ctx.send("<" + i + ">")
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except (AttributeError, TypeError):
        result = f"Could not find {siteName} in the database."
        await ctx.send(result)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def pastes(ctx, email):

    # search paste database for all pastes containing given account
    try:
        result = pwned(email, appName, apiKey).searchPastes()
        breachNum = len(result)
        mod = breachNum % 20
        numTxt = f"Your account was found in {breachNum} pastes."
        await ctx.send(file = discord.File("images/warning-sign.png"))
        await ctx.send(numTxt)
        embed = discord.Embed()
        names = []
        for data in result:
            if data["Title"] == None:
                data["Title"] = "No Title"
            names.append({data["Title"] : data["Id"]})
        for i in range(breachNum // 20):
            if i * 20 < breachNum:
                split_search(embed, names, i * 20, (i * 20) + 20)
                await ctx.send(embed=embed)
        if mod > 0:
            split_search(embed, names, (len(names) - mod), len(names))
            await ctx.send(embed=embed)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except TypeError:
        result = (
            "The account could not be found and has therefore not been pwned."
        )
        await ctx.send(result)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def paste_id(ctx, email, ID):

    # search paste database by ID and list all details for paste
    try:
        result = pwned(email, appName, apiKey).searchPastes()
        breachNum = len(result)
        embed = discord.Embed(title = ID)
        for data in result:
            if data["Id"] == ID:
                for key, value in data.items():      
                    embed.add_field(name=key, value=value, inline=False)
        await ctx.send(embed=embed)
        await ctx.send("*All data sourced from https://haveibeenpwned.com*")

    except TypeError:
        result = f"Could not find {ID} in database."
        await ctx.send(result)

    except RequestException:
        embed = discord.Embed(title="ERROR: Network Failure.", color=0xFF0000)
        await ctx.send(embed=embed)


@bot.command()
async def info(ctx):

    # bot name, description, author info, invite link, and server count
    desc = ("A Discord bot implementation of Troy Hunt's haveibeenpwned.com service, "
            "a free resource for anyone to quickly assess if they may have been put "
            "at risk due to an online account of theirs having been compromised or "
            "'pwned' in a data breach.")

    embed = discord.Embed(title="Hibpwned", description=desc, color=0xEEE657)
    embed.add_field(name="Author", value="plasticuproject")
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    # insert your client id number here
    embed.add_field(
        name="Invite", value="https://discordapp.com/oauth2/authorize?client_id=<...>&scope=bot")
    await ctx.send(embed=embed)


bot.remove_command("help")


@bot.command()
async def help(ctx):

    # bot description and command help
    desc = ("A Discord bot implementation of Troy Hunt's haveibeenpwned.com service, "
            "a free resource for anyone to quickly assess if they may have been put "
            "at risk due to an online account of theirs having been compromised or "
            "'pwned' in a data breach. List of commands are:")

    embed = discord.Embed(title="Hibpwned", description=desc, color=0xEEE657)

    # commands
    embed.add_field(name="!password", 
        value="(*password*) Search database for any instances of your password. Returns the number of times your password is found.", inline=False)
    embed.add_field(name="!search", 
        value="(*account_name*) Searches database for breaches containing the provided account name. You may provide a username or email address.", inline=False)
    embed.add_field(name="!breaches", 
      value="Displays names of all breaches in the database.", inline=False)
    embed.add_field(name="!breach_name", 
        value="(*name*) Displays the details of a single breach.", inline=False)
    embed.add_field(name="!pastes", 
        value="(*email_address*) Search database for any pastes containing the provided email address.", inline=False)
    embed.add_field(name="!paste_id", 
        value="(*email_address paste_id*) Will return details of a paste containing your email address. ", inline=False)
    embed.add_field(name="!info", 
        value="Gives a info about this bot.", inline=False)
    embed.add_field(name="!help", 
        value="Gives this message.", inline=False)
    await ctx.send(embed=embed)


# insert your bot TOKEN here
bot.run("<...>")

