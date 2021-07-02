import discord
from bs4 import BeautifulSoup
import urllib.request
import re


with open("bot_token", 'r') as bt:
    TOKEN = bt.readline()

COMMON_EXTS = (
    "asm",
    "c",
    "cc",
    "class",
    "clj",
    "cpp",
    "cs",
    "cxx",
    "el",
    "go",
    "h",
    "java",
    "lua",
    "m",
    "md",
    "m4",
    "php",
    "pl",
    "po",
    "py",
    "rb",
    "rkt"
    "rs",
    "sh",
    "s",
    "swift",
    "vb",
    "vcxproj",
    "xcodeproj",
    "xml",
    "diff",
    "patch",
    "html",
    "js",
    "json",
    "csv",
)

def get_ext(urlStr):
    return urlStr[urlStr.rfind('.') + 1:].lower()


PAYLOAD_MAXLEN = 2000 # Discord character limit
long_code = True

class BotClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} is now online.")

    async def on_message(self, msg):
        if msg.author == self.user:
            return 
        
        elif msg.content.startswith("!longcode"):
            global long_code

            if not long_code:
                await msg.channel.send(f"> :green_circle: Alright! I'll display code over the {PAYLOAD_MAXLEN} character limit!")
                long_code = True

            else:
                await msg.channel.send(f"> :red_circle: Alright! I'll only display code under the {PAYLOAD_MAXLEN} character limit!")
                long_code = False

            # The strange process looks like this:
            #
            # (1) https://github.com/SeanJxie/3d-engine-from-scratch/blob/main/CppEngine3D/engine.cpp
            #                                            |
            #                                            V
            # (2) ['https:', '', 'github.com', 'SeanJxie', '3d-engine-from-scratch', 'blob', 'main', 'CppEngine3D', 'engine.cpp']
            #                                            |
            #                                            V
            # (3) ['https:/', 'raw.githubusercontent.com', 'SeanJxie', '3d-engine-from-scratch', 'main', 'CppEngine3D', 'engine.cpp']
            #                                            |
            #                                            V
            # (4) https://raw.githubusercontent.com/SeanJxie/3d-engine-from-scratch/main/CppEngine3D/engine.cpp
            
        else:
            print(f"\nMessage: {msg.content}")
            matches = re.findall("http(s?)://github.com/([^\s]+)", msg.content)

            # We want no reps and valid extensions.
            matches = list(set(filter(lambda x: get_ext(x[1]) in COMMON_EXTS, matches)))

            if len(matches) > 1:
                await msg.channel.send(f"> :eyes: I've detected {len(matches)} valid links here. They will be served in order!")

            if len(matches) != 0:
                for match in matches:

                    # (1)
                    url = "https://github.com/" + match[1]
                    print(f"Detected url: {url}")

                    # (2)
                    urlSplit = url.split('/')
                    
                    # (3)
                    urlSplit.remove('')
                    urlSplit.remove("blob")
                    urlSplit[0] = "https:/"
                    urlSplit[1] = "raw.githubusercontent.com"

                    # (4)
                    rawUrl = '/'.join(urlSplit)
                    print(f"Rebuilt url: {rawUrl}")

                    # Parse HTML and get all text
                    response = urllib.request.urlopen(rawUrl)
                    bs4obj = BeautifulSoup(response, features="html.parser")

                    # Send text and split into multiple messages if it's too long
                    codeString = ''.join(bs4obj.find_all(text=True))
                    payload = f"```{codeString}```"
                    
                    if len(payload) <= PAYLOAD_MAXLEN:
                        await msg.channel.send(f"> :desktop: The following code is found in `{urlSplit[-1]}`:")
                        await msg.channel.send(payload)

                    elif long_code:
                        await msg.channel.send(f"> :desktop: The following code is found in `{urlSplit[-1]}`:")
                        print("Code too long. Splitting.")

                        payloadSegment = ''

                        for line in codeString.split('\n'):
            
                            if len(payloadSegment) + len(line) + 6 >= PAYLOAD_MAXLEN: # The +6 accounts for the 6 backticks used for code markup
                                await msg.channel.send(f"```{payloadSegment}```")
                                print(f"Payload segment size: {len(payloadSegment) + 6}")
                                payloadSegment = ''

                            payloadSegment += line + '\n'

                        await msg.channel.send(f"```{payloadSegment}```")
                        print(f"Payload segment size: {len(payloadSegment) + 6}")

                    else:
                        await msg.channel.send(f"> That's a lot of code! Type `!long_code` to toggle my long code reading ability!")

                    await msg.channel.send(f"> :ok_hand: That's the end of `{urlSplit[-1]}`")
                    print("Send success.")



if __name__ == "__main__":
    bot_client = BotClient()
    bot_client.run(TOKEN)