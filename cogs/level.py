import discord, time
from discord.ext import commands

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

import sqlite3
import traceback

from discord.ext.commands.core import guild_only

class Level(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.out = client.console.print
        self.timestamps = {}
        
        # Create a database called "users" if it doesn't exist using sqlite3
        self.db = sqlite3.connect('users.db')
        # Create a cursor
        self.db_cursor = self.db.cursor()
        # We create a table called "users" if it doesn't exist and store the user id, guild id, xp, and level
        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER, guild_id INTEGER, xp INTEGER, level INTEGER)")

        self.player = ImageFont.truetype("Voice In My Head.otf", 140)
        self.rank = ImageFont.truetype("Voice In My Head.otf",140)
        self.xp = ImageFont.truetype("Voice In My Head.otf", 70)

        self.xs,self.ys,self.xe,self.ye=565,406,1832,479

    def getUser(self, author_id, guild_id):
        try:
            user = self.db_cursor.execute("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", (author_id, guild_id)).fetchone()
            if user is None:
                self.out("User not found in database Creating new user", 1)
                self.db_cursor.execute("INSERT INTO users VALUES ($1, $2, $3, $4)", (author_id, guild_id, 0, 1))
            user = self.db_cursor.execute("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", (author_id, guild_id)).fetchone()
            self.db.commit()
            return user
        except Exception as e:
            self.out(traceback.format_exc(), 2)
    
    @commands.command()
    async def level(self, ctx):
        try:
            guild_id, author_id = ctx.guild.id, ctx.author.id
            self.out(f"Getting user info for {author_id}")
            user = self.getUser(author_id, guild_id)
            img_byte_arr = self.renderImg(ctx, user, author_id)
            file = discord.File(img_byte_arr, filename = "image.png")
            await ctx.channel.send(file=file)
        except Exception as e:
            self.client.console.print(traceback.format_exc(), 2)
    
    def renderImg(self, ctx, user, author_id):
        start = time.time()
        ranking = 0
        userAvatarUrl = ctx.author.avatar_url_as(format='png')
        self.out(f"Getting user image for {userAvatarUrl}")
        
        img = Image.open(BytesIO(requests.get(userAvatarUrl).content))
        
        template = Image.open('template_off.PNG')
        template.putalpha(128)
        
        cur_level = user[3]

        xpneed= round((4* (cur_level ** 3))/5)
        xplast = round((4* ((cur_level-1) ** 3))/5)
        
        draw = ImageDraw.Draw(template)
        # MAX 1832
        rectx = ((user[2]-xplast) / (xpneed-xplast))
        rectx = ((self.xe - self.xs) * rectx) + self.xs
        if rectx >= 1832:
            rectx = 1832
        draw.rectangle((self.xs,self.ys,self.xe,self.ye),fill=(68,68,68))
        draw.ellipse((533,406,603,479),fill=(68,68,68))
        draw.ellipse((self.xe-32,406,self.xe-32+70,479),fill=(68,68,68))
        draw.rectangle((self.xs,self.ys,rectx,self.ye),fill=(254, 231, 2))
        draw.ellipse((533,406,603,479),fill=(254, 231, 2))
        draw.ellipse((rectx-32,406,rectx-32+70,479),fill=(254, 231, 2))
        draw.text((565, 300),f"{ctx.author}",(255,255,255),font=self.xp)
        draw.text((565, 80),f"Rank 0",(255,255,255),font=self.rank)
        x,y = draw.textsize(f"Level {user[3]}", font=self.rank)
        if (1575+x) > self.xe:
            x2 = self.xe-1575
            x2 = x-x2
            draw.text((1575-x2, 80),f"Level {user[3]}",(255,255,255),font=self.rank)
        else:
            draw.text((1575, 80),f"Level {user[3]}",(255,255,255),font=self.rank)

        x,y = draw.textsize(f"{user[2] - xplast}/{xpneed} XP", font=self.xp)
        if (1575+x) > self.xe:
            x2 = self.xe-1575
            x2 = x-x2
            draw.text((1575-x2, 300),f"{user[2] - xplast}/{xpneed-xplast} XP",(255,255,255),font=self.xp)
        else:
            draw.text((1575, 300),f"{user[2] -xplast}/{xpneed-xplast} XP",(255,255,255),font=self.xp)
        
        img = img.resize((350, 350))
        bigsize = (img.size[0] * 3, img.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(img.size, Image.ANTIALIAS)
        img.putalpha(mask)

        template.paste(img, (126,126),img)
        img_byte_arr = BytesIO()
        template.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        self.out(type(img_byte_arr), 1)
        return img_byte_arr
    
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author == self.client.user:
                return

            author_id = str(message.author.id)
            guild_id = str(message.guild.id)


            #CHECKING IF USER IS IN self.db and get the author_id, guild_id, xp and level
            user = self.db_cursor.execute("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", (author_id, guild_id)).fetchone()
            self.client.console.print(user)

            #IF ITS NOT IN DATABASE IT CREATES THE USER DB
            if not user: self.db_cursor.execute("INSERT INTO users (user_id, guild_id, xp, level) VALUES ($1, $2, $3, $4)", (author_id, guild_id, 0, 1))

            #ADDING XP
            user = self.db_cursor.execute("SELECT * FROM users WHERE user_id = $1 AND guild_id = $2", (author_id, guild_id)).fetchone()
            
            #Add xp to user
            self.db_cursor.execute("UPDATE users SET xp = xp + 1 WHERE user_id = $1 AND guild_id = $2", (author_id, guild_id))

            if user[2] >= round((4* (user[3] ** 3))/5):
                # Level up the user in the guild and update the database
                self.db_cursor.execute("UPDATE users SET level = $1 WHERE user_id = $2", (user[3] + 1, user[0]))
                await message.channel.send(f"{message.author.mention} is now level {user[3] + 1}")
            
            self.db.commit()
        except Exception as e:
            self.client.console.print(traceback.format_exc(), 2)


def setup(client):
    client.add_cog(Level(client))
