#!/usr/bin/python3
import discord
import csv
import random
import asyncio

token = open('api.key','r').read()
emotes = {}


def writeEmotes():
    with open('emotes/emotes.csv', mode='w',newline='') as emoteFile:
        writer = csv.writer(emoteFile)
        writer.writerow(["name","emote"])
        for e in emotes.items():
            writer.writerow(e)


def readEmotes():
    with open('emotes/emotes.csv') as emoteFile:
        reader = csv.reader(emoteFile)
        next(reader)
        for row in reader:
            emotes[row[0]] = row[1]


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        readEmotes()
        self.pollMsg = None
        self.pollTimer = 0
        self.slotTimer = 0
        self.resultMsg = None
        self.slotMsg = None
        self.slot = [0,0,0]
        self.slot_user = "" 
        self.slot_emotes = (emotes['PoGif'], emotes['UnPog'], emotes['SadChamp'], emotes['SHOGOYUM'], emotes['SHOGOMUL'], emotes['WeirdChamp'], emotes['InsaneChamp'], emotes['POGOMO'], emotes['PogU'], emotes['PainsChamp'])

    async def end_slot(self):
        for num in self.slot:
            if self.slot[0] != num:
                await self.resultMsg.edit(content="You lost **{}** {}{}".format(self.slot_user, emotes['PepeLaugh'], emotes['PianoTime']))
                break
        else:
            await self.resultMsg.edit(content="{0} **HOLY MOTHER OF SWEET BABY JESUS {1} HIT THE JACKPOT** {0}".format(emotes['PPogo'], self.slot_user))    
        self.resultMsg = None
        self.slotMsg = None
        self.slot = [0,0,0]
        self.slot_user = ""
        self.slotTimer = 0
    async def clear_poll(self):
        msgStr = self.pollMsg.content[self.pollMsg.content.find('-')+1:]
        yes = no = 0
        cache_msg = discord.utils.get(self.cached_messages,id=self.pollMsg.id)
        for r in cache_msg.reactions:
            if r.emoji == "👍":
                yes = r.count
            elif r.emoji == "👎":
                no = r.count
        result = "tied {}".format(emotes['DansChamp'])

        winner = yes
        if yes > no:
            result = "accepted {}".format(emotes['ClappyJam'])
        elif yes < no:
            result = "declined {}".format(emotes['PepeWhy'])
            winner = no
        await self.pollMsg.edit(content="**{0}** poll results:\n\n👍 **[{1}]**     {4:.2f}%     **[{2}]** 👎\n\nhas **__{3}__**".format(msgStr,yes,no,result,( (winner)/(yes+no))*100))
        await self.pollMsg.clear_reactions()
        self.pollMsg = None
        self.pollTimer = 0


    async def on_message(self, message):
        if message.author == self.user:
            return
        #print('Message from {0.author.name}: {0.content} {0.author.id}'.format(message))
        guild = message.guild
        channel = message.channel
        author = message.author
        content = message.content

 
        if content.startswith('/doloreshelp'):
            await channel.send("""**/addglobalall**   -> Add all the emotes in the server for global use.
**/addglobal [emotename]**   -> Add an already existing emote for global use.
**/removeglobal [emotename]**   -> Remove an emote from global use but not from server.
**/add [emotename]**   -> Add an emote to this server. (Use it with image attached)
**/remove [emotename]**   -> Remove an emote from this server.s
**/killme [optional_count]**   -> Deletes your own messages. (max and default 10)
**/roll [optional_number]**   -> Roll a random number. (default 100)
**/poll [optional_time_as_sec] [pollsentence]**   -> Create a poll. (default 10 sec)
**/slot**     -> Use the slot machine.
**/emotes**  -> See the emotes.
            """)
        elif content.startswith('/emotes'):
            await message.delete()
            await channel.send("Check the emotes here {0}👉 http://206.189.111.249:8000".format(emotes['forsenSmug']))
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

            if not author.permissions_in(channel).manage_emojis:
                await channel.send("You don't have permission to add an emote !")
                return

            try:
                imgBytes = await message.attachments[0].read()
                emoji = await guild.create_custom_emoji(name=parsed[1], image=imgBytes)
                if(content.startswith('/addglobal')):
                     emotes[emoji.name] = str(emoji)
                     writeEmotes()
                     await channel.send("Emoji succesfully created globally : {0}".format(str(emoji)))
                else:
                    await channel.send("Emoji succesfully created : {0}".format(str(emoji)))
            except :
                await channel.send("Emoji size too big or emoji limit exceed.")
        elif content == '/addglobalall': # ADD ALL THE EMOTES IN THIS SERVER AS GLOBAL
            for emoji in guild.emojis:
                emotes[emoji.name] = str(emoji)
            writeEmotes()
            await channel.send("Emotes added succesfully.")
        elif content.startswith('/addglobal '): # ADD AN EMOTE AS GLOBAL EMOTE
            parsed = content.split(' ')
            if len(parsed) != 2:
                await channel.send("**Usage:**``/addglobal [AnEmoteInServer]``")
                return
            
            for emoji in guild.emojis:
                if emoji.name == parsed[1]:
                    emotes[emoji.name] = str(emoji)
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
                if k == parsed[1]:
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
                    emotes.pop(emoji.name, None)
                    await emoji.delete()
                    writeEmotes()
                    await channel.send("Emote removed succesfuly.")
                    break
            else:
                await channel.send("There is no emote called {0} !".format(parsed[1]))
        elif content.startswith('/slot'):
            if self.slotMsg != None:
                await channel.send('Wait for current slot to end.')
                return
            await channel.send('**{}** used slot machine {}🕹️'.format(author.display_name, emotes['PauseChamp']))
            self.slotTimer = 3
            self.slot_user = author.display_name
            self.slotMsg = await channel.send('{0} {0} {0} \n{0} {0} {0} \n{0} {0} {0} '.format(emotes['PoGif']))
            self.resultMsg = await channel.send('Waiting for results {}{}'.format(emotes['forsenSmug'], emotes['TeaTime']))
            self.loop.create_task(slot_step())
        elif content.startswith('/roll'):
            try:
                parsed = content.split(' ')
                count = int(parsed[1]) if len(parsed) > 1  else 100
                rand = random.randint(0, count)
                await channel.send('**{0} rolled between [0 - {1}] and got __{2}__ !**'.format(author.display_name,count,rand))
            except:
                await channel.send('**Usage:** ``/roll [number(optional)]``')
        elif content.startswith("/poll "):
            parsed = content.split(' ')
            if len(parsed) < 2:
                await channel.send("**Usage:**``/poll [time(optional)][pollsentence]``")
                return
            if self.pollMsg != None:
                await channel.send("There is already a poll going on ! Wait for it to end.")
                return
            try:
                time = min(int(parsed[1]), 30)
                sentence = ' '.join(parsed[2:])
            except:
                time = 10
                sentence = ' '.join(parsed[1:])

            self.pollTimer = time
            self.pollMsg = await channel.send("**[{}]** - {} says *{}*, do you agree ? {}🤚".format(time, author.display_name, sentence, emotes['peepoGlad']))
            await self.pollMsg.add_reaction("👍")
            await self.pollMsg.add_reaction("👎")
            await message.delete()
            self.loop.create_task(poll_step())
        else:
            parsed = content.split()
            flag = False
            for i, word in enumerate(parsed):
                for name, e in emotes.items():
                    if word == name:
                        flag = True
                        parsed[i] = e       
            if flag:
                await message.delete()
                await channel.send("**{0}**:".format(author.display_name))
                await channel.send(' '.join(parsed))

async def slot_step():
    try:
        while client.slotTimer > 0:
            await asyncio.sleep(1.5)
            slot_index = 3 - client.slotTimer
            client.slotTimer -= 1
            if slot_index > 0 and random.randint(1,100) < 16:
                client.slot[slot_index] = client.slot[0]
            else:
                client.slot[slot_index] = random.randint(1, len(client.slot_emotes)-1)

            temp_slot_msg = ""
            if slot_index == 0:
                temp_slot_msg += "{0} {1} {1} ".format(emotes['downPog'], emotes['PoGif'])
            elif slot_index == 1:
                temp_slot_msg += "{0} {0} {1} ".format(emotes['downPog'], emotes['PoGif'])
            elif slot_index == 2:
                temp_slot_msg += "{0} {0} {0} ".format(emotes['downPog'])

            temp_slot_msg += "\n"

            for num in client.slot:
                temp_slot_msg += '{} '.format(client.slot_emotes[num])
            
            temp_slot_msg += "\n"

            if slot_index == 0:
                temp_slot_msg += "{0} {1} {1} ".format(emotes['upPog'], emotes['PoGif'])
            elif slot_index == 1:
                temp_slot_msg += "{0} {0} {1} ".format(emotes['upPog'], emotes['PoGif'])
            elif slot_index == 2:
                temp_slot_msg += "{0} {0} {0} ".format(emotes['upPog'])

            await client.slotMsg.edit(content=temp_slot_msg)
        await client.end_slot()
    except:
        client.resultMsg = None
        client.slotMsg = None
        client.slot = [0,0,0]
        client.slot_user = ""
        client.slotTimer = 0

async def poll_step():
    try:
        while client.pollTimer > 0:
            await asyncio.sleep(1.0)
            client.pollTimer -= 1
            await client.pollMsg.edit(content="**["+str(client.pollTimer)+client.pollMsg.content[client.pollMsg.content.find(']'):])
        await client.clear_poll()
    except:
        self.pollMsg = None
        self.pollTimer = 0
            

client = MyClient()
client.run(token)

