# Discord Link Bot

Discord Link Bot is a Python-based bot for Discord that forwards messages from one channel to another if they contain a link.

## Requirements

- Python 3.12 or higher

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/discord-link-bot.git
cd discord-link-bot
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

`python -m discord_link_bot`

## Configuration
Copy `config.example.yaml` to `config.yaml` and set the `token` and `channel_mappings`.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Acknowledgements

This project uses the following main dependencies:
- [discord.py](https://github.com/Rapptz/discord.py)
- [PyYAML](https://pyyaml.org/)

For a full list of dependencies, please check the `pyproject.toml` file.