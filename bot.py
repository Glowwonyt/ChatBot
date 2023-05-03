import discord
import os
from discord import app_commands , AppCommandOptionType
import time , io
import Brainshop , typing
import psutil, json
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
import keep_alive

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
brain = Brainshop.Brain(key=os.getenv("key"), bid=169722)

mod_list = [732532528568729630]

banned = []
tips = [
 "It's always a good idea to be specific",
 'Here are a few keywords that can be interesting to experiment with: "illustration", "photorealistic", "high definition"',
 "We've seen so many cool tricks from the community so you should definitely check what others do for inspiration!"
]
not_allowed = ["nsfw", "naked", "nude"]

async def open_account(user):
	with open("points.json", "r") as f:
		users = json.load(f)
	
	if str(user.id) in users:
		return False
	
	else:	
		users[str(user.id)] = {}
		users[str(user.id)]["Points"] = 50

	with open("points.json", "w") as f:
		json.dump(users,f,indent=4)


@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	global startTime
	startTime = time.time()
	await tree.sync(guild=discord.Object(id=893067928772153364))


@bot.event
async def on_message(msg):

	if not msg.author.bot:
		await open_account(msg.author)
	if msg.channel.id == 970936649804566579 and msg.author.id not in banned:
		if msg.author.id != 870519422379524146:
			
			
			with open("points.json", "r") as f:
				users = json.load(f)

			if users[str(msg.author.id)]["Points"] < 5:
				await msg.channel.send("Im sorry, But you don't have enought points to use this command. Try chatting in <#940548518043594762> so that you can get the nessacary amount of points")
				return
			
			users[str(msg.author.id)]["Points"] -= 5

			with open("points.json", "w") as f:
				json.dump(users,f, indent=4)

			response = brain.ask(msg.content)
			time.sleep(3)
			await msg.channel.send(response, reference=msg)

	else:
		if not msg.author.bot:
			with open("points.json", "r") as f:
				users = json.load(f)
	
			users[str(msg.author.id)]["Points"] += 10
	
			with open("points.json", "w") as f:
				json.dump(users,f, indent=4)


@tree.command(name="stats",
              description="Stats about the bot",
              guild=discord.Object(id=893067928772153364))
async def first_command(interaction):
	await open_account(interaction.user)
	bedem = discord.Embed(title='System Resource Usage',
	                      description='See CPU and memory usage of the system.')
	bedem.add_field(name='CPU Usage',
	                value=f'{psutil.cpu_percent()}%',
	                inline=False)
	bedem.add_field(name='Memory Usage',
	                value=f'{psutil.virtual_memory().percent}%',
	                inline=False)
	bedem.add_field(
	 name='Available Memory',
	 value=
	 f'{psutil.virtual_memory().available * 100 / psutil.virtual_memory().total}%',
	 inline=False)
	uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))
	bedem.add_field(name="Uptime", value=f"{uptime}")
	await interaction.response.send_message(embed=bedem)


@tree.command(name="text2image",
              description="Change a text to an image | `10 points`",
              guild=discord.Object(id=893067928772153364))
async def second_command(interaction, query: str):
	await interaction.response.send_message("Command takes 5 - 7 seconds to generate, to prevent from being banned, use it 1 at a time!")
	stability_api = client.StabilityInference(
    key=os.getenv("STABILITY_KEY"),
    verbose=True,
	)	

	answers = stability_api.generate(
    prompt=query,
    seed=34567
	)

	for resp in answers:
		for artifact in resp.artifacts:
			if artifact.finish_reason == generation.FILTER:
				await interaction.channel.send(f"Image didn't fit the criteria , reset inbound! \n request submitted by : {interaction.user.name}")
			if artifact.type == generation.ARTIFACT_IMAGE:
				img = Image.open(io.BytesIO(artifact.binary))
				img.save("Result.png")
				await interaction.channel.send(file = discord.File("Result.png"))
				
	

@tree.command(name="balance",description="View the amount of points you have!",guild=discord.Object(id=893067928772153364))
async def balance_command(interaction,member: typing.Optional[discord.Member]=None):
	if member == None:
		member = interaction.user

	with open("points.json","r") as f:
		users = json.load(f)
		
	embed = discord.Embed(title=f"{member.name}'s Balance'",description=f"{member.name}'s Balance : :coin: {users[str(member.id)]['Points']}",color = discord.Colour.green())
	await interaction.response.send_message(embed=embed)



bot.run(os.getenv("TOKEN"))
