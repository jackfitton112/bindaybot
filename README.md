# BinDayBot
A bot that sends you a DM on discord the day before your bin day.
---

## Setup

1. Clone the repo
2. Install the requirements
3. create .env
4. run the bot

### 1. Clone the repo
```bash
git clone https://github.com/jackfitton112/bindaybot.git
```

### 2. Install the requirements
```bash
pip install -r requirements.txt
```

### 3. create .env
```bash
touch .env
```
then add the following to the .env file
```bash
DISCORD_TOKEN=your_token_here
```

### 4. run the bot
```bash
nohup python3 main.py > /dev/null 2>&1 &
```

## Usage

### Commands

- `!when` - tells you when your next bin day is
- `!setup <postcode>` - sets your postcode
- `!help` - shows a help message


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.



