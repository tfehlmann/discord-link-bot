import discord
import re
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Get token and channel mappings from config
TOKEN = config['token']
CHANNEL_MAPPINGS = config['channel_mappings']

# Create a client instance
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Regular expression to detect links
link_regex = re.compile(r'https?://[^\s]+')

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message contains a link
    if not link_regex.search(message.content):
        return

    # Check if the message is in any of the source channels
    for mapping in CHANNEL_MAPPINGS:
        if message.channel.id == mapping['source']:
            logging.info(f"Link message detected in source channel {mapping['source']}: {message.content[:50]}...")
            
            target_channel = client.get_channel(mapping['target'])
            if not target_channel:
                logging.error(f"Target channel {mapping['target']} not found")
                continue

            # Create an embed for the forwarded message
            embed = discord.Embed(
                description=message.content,
                timestamp=message.created_at,
                color=discord.Color.blue()
            )
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url if message.author.avatar else None)
            
            # Add attachments if any
            if message.attachments:
                embed.add_field(name="Attachments", value="\n".join([a.url for a in message.attachments]))

            # Send the embed to the target channel
            await target_channel.send(embed=embed)
            logging.info(f"Message forwarded to target channel {mapping['target']}")

if __name__ == "__main__":
    client.run(TOKEN)