import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from discord_link_bot.__main__ import source_to_target_channels, on_message
import datetime

# Add this line at the top of the file
pytest_plugins = ['pytest_asyncio']

@pytest.fixture
def sample_config():
    return {
        "channel_mappings": [
            {"source": 123, "target": 456},
            {"source": 123, "target": 789},
            {"source": 321, "target": 654}
        ]
    }

def test_source_to_target_channels(sample_config):
    result = source_to_target_channels(sample_config)
    assert result == {123: [456, 789], 321: [654]}

@pytest.mark.asyncio
async def test_on_message_with_link():
    # Mock message
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock(spec=discord.User)
    message.author.bot = False
    message.author.display_name = "Test User"
    message.author.avatar = MagicMock()
    message.author.avatar.url = "https://example.com/avatar.png"
    message.channel.id = 123
    message.content = "Check out this link: https://example.com"
    message.created_at = datetime.datetime(2023, 4, 10, 12, 0, 0, tzinfo=datetime.timezone.utc)
    message.attachments = []

    # Mock client
    client = AsyncMock(spec=discord.Client)
    client.user = MagicMock(spec=discord.ClientUser)
    # Mock target channel
    target_channel = AsyncMock(spec=discord.TextChannel)
    client.get_channel.return_value = target_channel
    
    with patch("discord_link_bot.__main__.CHANNEL_MAP", {123: [456]}), \
         patch("discord_link_bot.__main__.client", client):
        
        await on_message(message)

    # Assert that send was called on the target channel
    target_channel.send.assert_called_once()
    
    # Check if the sent message is an embed
    args, kwargs = target_channel.send.call_args
    assert isinstance(kwargs['embed'], discord.Embed)
    assert kwargs['embed'].description == message.content
    assert kwargs['embed'].author.name == "Test User"
    assert kwargs['embed'].author.icon_url == "https://example.com/avatar.png"

@pytest.mark.asyncio
async def test_on_message_without_link():
    # Mock message without a link
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock(spec=discord.User)
    message.author.bot = False
    message.channel.id = 123
    message.content = "This is a message without a link"

    # Mock client
    client = AsyncMock(spec=discord.Client)
    client.user = MagicMock(spec=discord.ClientUser)

    # Mock target channel
    target_channel = AsyncMock(spec=discord.TextChannel)
    client.get_channel.return_value = target_channel
    with patch("discord_link_bot.__main__.CHANNEL_MAP", {123: [456]}), \
         patch("discord_link_bot.__main__.client", client):
        
        await on_message(message)

    # Assert that send was not called on the target channel
    target_channel.send.assert_not_called()

@pytest.mark.asyncio
async def test_on_message_from_bot():
    # Mock message from the bot itself
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock(spec=discord.User)
    message.author.bot = True

    # Mock client
    client = AsyncMock(spec=discord.Client)
    client.user = message.author

    with patch("discord_link_bot.__main__.client", client):
        await on_message(message)

    # Assert that no further processing occurred
    assert not message.channel.id.called

@pytest.mark.asyncio
async def test_on_message_with_attachment():
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock(spec=discord.User)
    message.author.bot = False
    message.author.display_name = "Test User"
    message.author.avatar = MagicMock()
    message.author.avatar.url = "https://example.com/avatar.png"
    message.channel.id = 123
    message.content = "Check out this attachment"
    message.created_at = datetime.datetime(2023, 4, 10, 12, 0, 0, tzinfo=datetime.timezone.utc)
    attachment = MagicMock(spec=discord.Attachment)
    attachment.url = "https://example.com/attachment.pdf"
    message.attachments = [attachment]

    client = AsyncMock(spec=discord.Client)
    client.user = MagicMock(spec=discord.ClientUser)
    target_channel = AsyncMock(spec=discord.TextChannel)
    client.get_channel.return_value = target_channel

    with patch("discord_link_bot.__main__.CHANNEL_MAP", {123: [456]}), \
         patch("discord_link_bot.__main__.client", client):
        
        await on_message(message)

    target_channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_target_channel_not_found():
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock(spec=discord.User)
    message.author.bot = False
    message.channel.id = 123
    message.content = "Check out this link: https://example.com"
    message.created_at = datetime.datetime(2023, 4, 10, 12, 0, 0, tzinfo=datetime.timezone.utc)
    message.attachments = []

    client = AsyncMock(spec=discord.Client)
    client.user = MagicMock(spec=discord.ClientUser)
    client.get_channel.return_value = None
    with patch("discord_link_bot.__main__.CHANNEL_MAP", {123: [456]}), \
         patch("discord_link_bot.__main__.client", client), \
         patch("discord_link_bot.__main__.logging.error") as mock_logging_error:
        
        await on_message(message)

    mock_logging_error.assert_called_once_with("Target channel 456 not found")

@pytest.mark.asyncio
@pytest.mark.parametrize("link", [
    "http://example.com",
    "https://example.com",
    "http://www.example.com",
    "https://www.example.com",
    "https://subdomain.example.com/path?query=value#fragment"
])
async def test_on_message_with_different_link_types(link):
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock(spec=discord.User)
    message.author.bot = False
    message.author.display_name = "Test User"
    message.author.avatar = MagicMock()
    message.author.avatar.url = "https://example.com/avatar.png"
    message.channel.id = 123
    message.content = f"Check out this link: {link}"
    message.created_at = datetime.datetime(2023, 4, 10, 12, 0, 0, tzinfo=datetime.timezone.utc)
    message.attachments = []

    client = AsyncMock(spec=discord.Client)
    client.user = MagicMock(spec=discord.ClientUser)
    target_channel = AsyncMock(spec=discord.TextChannel)
    client.get_channel.return_value = target_channel
    with patch("discord_link_bot.__main__.CHANNEL_MAP", {123: [456]}), \
         patch("discord_link_bot.__main__.client", client):
        
        await on_message(message)

    target_channel.send.assert_called_once()
    args, kwargs = target_channel.send.call_args
    assert isinstance(kwargs['embed'], discord.Embed)
    assert kwargs['embed'].description == message.content
    assert kwargs['embed'].author.name == "Test User"
    assert kwargs['embed'].author.icon_url == "https://example.com/avatar.png"