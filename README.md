# RSS my ass

[@rss_my_ass_bot](http://t.me/rss_my_ass_bot)

This Telegram bot is able to generate RSS feeds for YouTube and beyond (with the power of [rss-bridge](https://github.com/RSS-Bridge/rss-bridge)). Send `/help` to bot or check out [release page](https://github.com/wunderwaffla/rss-my-ass/releases) to see what it can do.

## Self hosting

Of course you can selfhost it. There are 2 prerequisites:

1. [Create new Telegram bot](https://core.telegram.org/bots)
2. Spin up [rss-bridge](https://github.com/RSS-Bridge/rss-bridge) instance if you want to generate feeds not only for YouTube
3. Rename `.env.example` to `.env`  
`cp .env.example .env`
4. Insert Telegram bot token and rss-bridge instance host in `.env` file

**If you want to run it locally**

- `pip install -r requirements.txt`
- `python bot.py`

**If you want to run it in docker**

- `docker run --env-file .env wunderwaffla/rss-my-ass`

I'll provide [Dockerfile](Dockerfile) just in case or you can use prebuilt image from [DockerHub](https://hub.docker.com/r/wunderwaffla/rss-my-ass)

---

You can help me to pay electric bill if you're not feeling like hosting it yourself

<a href="https://www.buymeacoffee.com/wunderwaffla"><img src="https://img.buymeacoffee.com/button-api/?text=/help&emoji=&slug=wunderwaffla&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff"></a>

---

![logo](logo.png)

[Art is not mine](https://www.deviantart.com/syrupyyy/art/Lil-Horse-874065692), I just slapped RSS logo where it belonds
