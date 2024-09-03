import logging
import re

import discord
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration from YAML file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Get token and channel mappings from config
TOKEN = config["token"]


def source_to_target_channels(config: dict) -> dict:
    result = {}
    for mapping in config["channel_mappings"]:
        if mapping["source"] not in result:
            result[mapping["source"]] = []
        result[mapping["source"]].append(mapping["target"])
    return result


CHANNEL_MAP = source_to_target_channels(config)

# Create a client instance
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Compile the regex pattern once
link_regex = re.compile(r"https?://[^\s]+")


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is in any of the source channels and contains a link
    if message.channel.id in CHANNEL_MAP and link_regex.search(message.content):
        target_channels = CHANNEL_MAP[message.channel.id]

        logging.info(f"Link message detected in source channel {message.channel.id}: {message.content[:50]}...")

        # Create an embed for the forwarded message
        embed = discord.Embed(
            description=message.content,
            timestamp=message.created_at,
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar.url if message.author.avatar else None,
        )

        # Add attachments if any
        if message.attachments:
            embed.add_field(
                name="Attachments",
                value="\n".join([a.url for a in message.attachments]),
            )

        # Send the embed to all target channels
        for target_channel_id in target_channels:
            target_channel = client.get_channel(target_channel_id)
            if target_channel:
                await target_channel.send(embed=embed)
                logging.info(f"Message forwarded to target channel {target_channel.id}")
            else:
                logging.error(f"Target channel {target_channel_id} not found")


if __name__ == "__main__":
    client.run(TOKEN)
