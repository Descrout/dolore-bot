#!/usr/bin/python3
import discord
import csv
import random
import asyncio

token = open('api.key','r').read()
emotes = {}


def writeEmotes():
    with open('emotes.csv', mode='w',newline='') as emoteFile:
        writer = csv.writer(emoteFile)
        writer.writerow(["emote","name"])
        for e in emotes.items():
            writer.writerow(e)


def readEmotes():
    with open('emotes.csv') as emoteFile:
        reader = csv.reader(emoteFile)
        next(reader)
        for row in reader:
            emotes[row[0]] = row[1]


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        readEmotes()
        self.sansur = False
        self.pollMsg = None
        self.pollTimer = 0
        
    async def clear_poll(self):
        msgStr = self.pollMsg.content[self.pollMsg.content.find('-')+1:]
        yes = no = 0
        cache_msg = discord.utils.get(self.cached_messages,id=self.pollMsg.id)
        #print(cache_msg)
        for r in cache_msg.reactions:
            if r.emoji == "👍":
                yes = r.count
            elif r.emoji == "👎":
                no = r.count
        result = "berabere <:SHOGOYUM:645003841946779669>"
        yes -= 1
        no -= 1
        winner = yes
        if yes > no:
            result = "kabul edildi <:EZ:666248281109692416>"
        elif yes < no:
            result = "reddedildi <:KEKW:662385718458318898>"
            winner = no
        await self.pollMsg.edit(content="**{0}** anketinin sonucu:\n\n👍 **[{1}]**     {4}%     **[{2}]** 👎\n\noylarıyla **__{3}__**".format(msgStr,yes,no,result,(winner/(yes+no))*100))
        await self.pollMsg.clear_reactions()
        self.pollMsg = None
        self.pollTimer = 0  

    async def on_message(self, message):
        if message.author == self.user:
            return
        print('Message from {0.author.name}: {0.content}'.format(message))
        guild = message.guild
        channel = message.channel
        author = message.author
        content = message.content

        print(guild.features)
        print(guild.premium_tier)
        if content.startswith('/doloreshelp'):
            await channel.send("""**/addglobalall**   -> Bu serverdaki tüm emoteları global kullanıma ekler.
**/addglobal [emotename]**   -> Belirtilen emote'u global kullanıma ekler.
**/removeglobal [emotename]**   -> Belirtilen emote'u global kullanımdan kaldırır.
**/add [emotename]**   -> Resim ile beraber eklendiğinde servera emote ekler.
**/remove [emotename]**   -> Belirtilen emote'u serverdan siler.
**/killme [count]**   -> Kendi mesajlarınızı siler. (count belirtmezseniz 10 tane) (max 10)
**/roll [number(optional)]**   -> Sayı girildiği durumda 0 ile sayı arasında random sayı seçer. (default 100)
**/poll [time(optional)] [pollsentence]**   -> Poll oluşturur ve 10 saniye sonra sonucu gösterir
            """)
        elif content.startswith('/killme'):
            msgList = await channel.history().flatten()
            parsed = content.split(' ')
            count = min(int(parsed[1]),10) if len(parsed) > 1  else 10
            count += 1
            for msg in msgList:
                if count <= 0:
                    break
                if msg.author.id == author.id:
                    await msg.delete()
                    count -= 1
        elif(content.startswith('/add ') or content.startswith('/addglobal ')) and  message.attachments: # ADD AN EMOTE TO SERVER
            parsed = content.split(' ')

            if len(parsed) != 2:
                await channel.send("**Usage:**``/add [emotename]`` with image attached.")
                return

            if len(guild.emojis) == guild.emoji_limit and guild.premium_tier == 0:
                await channel.send("This server has reached the maximum emoji size!")
                return

            if not author.permissions_in(channel).manage_emojis:
                await channel.send("You don't have permission to add an emote !")
                return

            try:
                imgBytes = await message.attachments[0].read()
                emoji = await guild.create_custom_emoji(name=parsed[1], image=imgBytes)
                if(content.startswith('/addglobal')):
                     emotes[str(emoji)] = emoji.name
                     writeEmotes()
                     await channel.send("Emoji succesfully created and added globally : {0}".format(str(emoji)))
                else:
                    await channel.send("Emoji succesfully created : {0}".format(str(emoji)))
            except:
                await channel.send("Emoji creation error !")
        elif content == '/addglobalall': # ADD ALL THE EMOTES IN THIS SERVER AS GLOBAL
            for emoji in guild.emojis:
                emotes[str(emoji)] = emoji.name
            writeEmotes()
            await channel.send("Emotes added succesfully.")
        elif content.startswith('/addglobal '): # ADD AN EMOTE AS GLOBAL EMOTE
            parsed = content.split(' ')
            if len(parsed) != 2:
                await channel.send("**Usage:**``/addglobal [AnEmoteInServer]``")
                return
            
            for emoji in guild.emojis:
                if emoji.name == parsed[1]:
                    emotes[str(emoji)] = emoji.name
                    writeEmotes()
                    await channel.send("Emote added globally : {0}".format(str(emoji)))
                    break
            else:
                await channel.send("There is no emote called {0} !".format(parsed[1]))
        elif content.startswith('/removeglobal '):
            parsed = content.split(' ')
            if len(parsed) != 2:
                await channel.send("**Usage:**``/removeglobal [emotename]``")
                return
            for k,v in emotes.items():
                if v == parsed[1]:
                    emotes.pop(k)
                    writeEmotes()
                    break
            await channel.send("Emote removed succesfully.")
        elif content.startswith('/remove '): # REMOVE AN EMOTE FROM SERVER
            parsed = content.split(' ')
            if len(parsed) != 2:
                await channel.send("**Usage:**``/remove [emotename]``")
                return

            if not author.permissions_in(channel).manage_emojis:
                await channel.send("You don't have permission to remove an emote !")
                return

            for emoji in guild.emojis:
                if emoji.name == parsed[1]:
                    emotes.pop(str(emoji),None)
                    await emoji.delete()
                    writeEmotes()
                    await channel.send("Emote removed succesfuly.")
                    break
            else:
                await channel.send("There is no emote called {0} !".format(parsed[1]))
        
        elif content.startswith('/roll'):
            try:
                parsed = content.split(' ')
                count = int(parsed[1]) if len(parsed) > 1  else 100
                rand = random.randint(0,count)
                await channel.send('**{0} rolled between [0 - {1}] and got __{2}__ !**'.format(author.display_name,count,rand))
            except:
                await channel.send('**Usage:** ``/roll [number(optional)]``')
        elif self.sansur and "anan" in content.lower() or "anası" in content.lower() or "anne" in content.lower():
            tempContent = content.lower()
            tempContent = tempContent.replace("anasını","anamı")
            tempContent = tempContent.replace("anası","anam")
            tempContent = tempContent.replace("anan","anam")
            tempContent = tempContent.replace("annen","annem")
            tempContent = tempContent.replace("annesini","annemi")
            tempContent = tempContent.replace("anneciğini","annemi")
            tempContent = tempContent.replace("anneciği","annem")
            tempContent = tempContent.replace("annesi","annem")
            tempContent = tempContent.replace("anneleriniz","annem")
            tempContent = tempContent.replace("anneciğin","anneciğim")
            
            await message.delete()
            await channel.send("**{0}**:".format(author.display_name))
            await channel.send(tempContent)
        elif content.startswith("/sansur"):
            self.sansur = not self.sansur
        elif content.startswith("/poll "):
            parsed = content.split(' ')
            if len(parsed) < 2:
                await channel.send("**Usage:**``/poll [time(optional)][pollsentence]``")
                return
            if self.pollMsg != None:
                await channel.send("There is already a poll going on ! Wait for it to end.")
                return
            try:
                time = min(int(parsed[1]),30)
                sentence = ' '.join(parsed[2:])
            except:
                time = 10
                sentence = ' '.join(parsed[1:])

            self.pollTimer = time
            self.pollMsg = await channel.send("**[{0}]** - {1} diyenler <:peepoWeird:568464708017848320>🤚".format(time,sentence))
            await self.pollMsg.add_reaction("👍")
            await self.pollMsg.add_reaction("👎")
            await message.delete()
            self.loop.create_task(step())
        else:
            tempContent = content
            flag = False
            for e,name in emotes.items():
                ind = tempContent.find(name)
                if ind != -1 and tempContent[ind-1] != ':' and name not in [n.name for n in guild.emojis if not n.animated]:
                    flag = True
                    tempContent = tempContent.replace(name,e)
            if flag:
                await message.delete()
                await channel.send("**{0}**:".format(author.display_name))
                await channel.send(tempContent)


async def test():
    print("test")


async def step():
    while client.pollTimer > 0:
        await asyncio.sleep(1.0)
        client.pollTimer -= 1
        await client.pollMsg.edit(content="**["+str(client.pollTimer)+client.pollMsg.content[client.pollMsg.content.find(']'):])
    await client.clear_poll()
            

client = MyClient()
client.run(token)

