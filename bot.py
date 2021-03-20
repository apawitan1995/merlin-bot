# bot.py
import os
import random
import discord
import asyncio, requests, datetime, aiohttp
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TENOR = os.getenv('TENOR_TOKEN')
CHANNEL = os.getenv('CHANNEL_ID')

datetime_now = datetime.datetime.now() - datetime.timedelta(hours=9, minutes=30)
lastsync = datetime_now.strftime("%Y-%m-%dT%H:%M:%S")


client = discord.Client() 

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    await market.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == 'fox!':
        search_random =  "https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % ("fox", "TENOR", 50)
        random_request = requests.get(search_random)
        json_random = random_request.json()['results']
        choice=random.randint(0,49)
        gif = json_random[choice]
        url = gif['url']
        await message.channel.send(url)

@tasks.loop(seconds=20)
async def market():
    global lastsync

    print(lastsync)

    channel = client.get_channel(int(CHANNEL))

    url = "https://api.opensea.io/api/v1/events"
    
    querystring = {"collection_slug":"foxpunk","only_opensea":"false","offset":"0","limit":"10","occurred_after":f'{lastsync}' } 
    
    response = requests.request("GET", url, params=querystring)
    
    if 'asset_events' in response.json() and len(response.json()['asset_events']) != 0:
        json_responses = response.json()['asset_events']
        length = len(json_responses)
        firstdata=json_responses[0]
        lastsync=firstdata["created_date"]
        for x in range(length):
            json_response = json_responses[x]
            if json_response["event_type"] == "created":
                asset = json_response["asset"]
                name = asset["name"]
                itemurl = asset["permalink"]
                gif = asset["image_url"]
                price = float(json_response["starting_price"])/ (1000000000000000000)
                sellerdata = json_response["seller"]
                usernamedata = sellerdata["user"]
                username = usernamedata["username"]
                address = sellerdata["address"]
                address = "https://opensea.io/accounts/" + address
                market_embed = discord.Embed(title=name, colour=discord.Colour.blue(), url=itemurl)
                market_embed.add_field(name="Listing at ", value=f'{float(price)} ETH', inline=False)
                market_embed.set_thumbnail(url=gif)
                market_embed.add_field(name="Seller: ", value=f'[{username}]({address})', inline=False)
                market_embed.set_footer(text="FOXPUNKSTUDIO | Its a foxhunt!")
                await channel.send(embed=market_embed)
            elif json_response["event_type"] == "successful":
                asset = json_response["asset"]
                name = asset["name"]
                itemurl = asset["permalink"]
                gif = asset["image_url"]
                price = float(json_response["total_price"])/ (1000000000000000000)
                sellerdata = json_response["seller"]
                sellerusernamedata = sellerdata["user"]
                sellerusername = sellerusernamedata["username"]
                selleraddress = sellerdata["address"]
                selleraddress = "https://opensea.io/accounts/" + selleraddress
                buyerdata = json_response["winner_account"]
                buyerusernamedata = buyerdata["user"]
                buyerusername = buyerusernamedata["username"]
                buyeraddress = buyerdata["address"]
                buyeraddress = "https://opensea.io/accounts/" + buyeraddress
                market_embed = discord.Embed(title=name, colour=discord.Colour.red(), url=itemurl)
                market_embed.add_field(name="Sale at ", value=f'{float(price)} ETH', inline=False)
                market_embed.set_thumbnail(url=gif)
                market_embed.add_field(name="Seller: ", value=f'[{sellerusername}]({selleraddress})', inline=True)
                market_embed.add_field(name="Buyer: ", value=f'[{buyerusername}]({buyeraddress})', inline=True)
                market_embed.set_footer(text="FOXPUNKSTUDIO | Welcome to the charm!")
                await channel.send(embed=market_embed)

client.run(TOKEN)