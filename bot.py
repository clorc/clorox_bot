import discord
import os
import configparser
import mysql.connector as mysql
import requests
import json
import re
import pyttanko as osu
import numpy as np
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from io import BytesIO

config = configparser.ConfigParser()
config.read('config.ini')

client = discord.Client()

api_key = config['INIT']['API_KEY']
api_link = 'https://osu.ppy.sh/api/'

image_data = 'mod_image_data.json'

lemon_milk_light = './fonts/LEMONMILK-Light.woff'
lemon_milk_regular = './fonts/LEMONMILK-Regular.woff'
special_characters = './fonts/DejaVuSans.ttf'

def display_play(api_link, api_key, response, mode=0):
    try:
        beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={response.json()[0]["beatmap_id"]}&m={mode}')
        beatmap_info.json()[0]
    except IndexError:
        beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={response.json()[0]["beatmap_id"]}&m={mode}&a=1')

    with open(image_data) as file:
        data = json.load(file)

    img = Image.new('RGBA', (900,500), color=(0, 0, 0, 255))
    black = Image.new('RGBA', (900,500), color=(0, 0, 0, 0))

    total_count = int(beatmap_info.json()[0]["count_normal"]) + int(beatmap_info.json()[0]["count_slider"]) + int(beatmap_info.json()[0]["count_spinner"])
    accuracy = int(response.json()[0]["count300"]) + int(response.json()[0]["count100"])*(1/3) + int(response.json()[0]["count50"])*(1/6)
    count_sum = int(response.json()[0]["count300"]) + int(response.json()[0]["count100"]) + int(response.json()[0]["count50"]) + int(response.json()[0]["countmiss"])

    completion = count_sum/total_count

    try:
        beatmap_cover = Image.open(requests.get(f'https://assets.ppy.sh/beatmaps/{beatmap_info.json()[0]["beatmapset_id"]}/covers/cover.jpg', stream=True).raw)
    except UnidentifiedImageError:
        beatmap_cover = Image.new('RGBA', (900,500), color=(0, 0, 0, 0))

    mod_list = ['NF', 'EZ', 'TD', 'HD', 'HR', 'SD', 'DT', '', 'HT', 'NC', 'FL', '', 'SO', '', 'PF', '', '', '', '', '', 'FI', '', '', '', '', '', '', '', '', '', 'MR']
    rank_colors = {
        'F': (242, 56, 56),
        'D': (242, 56, 56),
        'C': (119, 57, 189),
        'B': (57, 111, 244),
        'A': (72, 248, 80),
        'S': (245, 225, 90),
        'X': (255, 223, 6),
        'SH': (170, 183, 204),
        'XH': (170, 183, 204)
    }
    mod_values = {
        'EZ': 2,
        'HR': 16,
        'DT': 64,
        'NC': 64,
        'HT': 256
    }

    pt35_light = ImageFont.truetype(lemon_milk_light, 35)
    pt30_light = ImageFont.truetype(lemon_milk_light, 30)
    pt25_light = ImageFont.truetype(lemon_milk_light, 25)
    pt20_light = ImageFont.truetype(lemon_milk_light, 20)

    pt200_regular = ImageFont.truetype(lemon_milk_regular, 200)
    pt50_regular = ImageFont.truetype(lemon_milk_regular, 50)
    pt35_regular = ImageFont.truetype(lemon_milk_regular, 35)

    special = ImageFont.truetype(special_characters, 25)

    beatmap_cover = beatmap_cover.resize((900,250))
    beatmap_cover = beatmap_cover.convert('RGBA')

    black_draw = ImageDraw.Draw(black)
    black_draw.rectangle(((0,0), (900,500)), fill=(0, 0, 0, 127))

    img.paste(beatmap_cover, (0,0))
    img = Image.alpha_composite(img, black)

    draw = ImageDraw.Draw(img)
    draw.polygon(([0, 100, 900, 200, 900, 500, 0, 500]), fill=(47, 49, 54))
    draw.line([(0, 100), (900, 200)], fill=(102, 104, 110), width=6)

    #--------------------   HEADER   --------------------#
    if len(beatmap_info.json()[0]["version"]) >=15:
        version = beatmap_info.json()[0]["version"][:15] + '...'

    else:
        version = beatmap_info.json()[0]["version"]

    if len(beatmap_info.json()[0]["title"]) >=22:
        title = beatmap_info.json()[0]["title"][:22] + '...'

    else:
        title = beatmap_info.json()[0]["title"]

    draw.text((28,18), f'{title}', fill=(255, 255, 255), font=pt35_light)
    draw.text((30,55), f'{beatmap_info.json()[0]["creator"]}', fill=(255, 255, 255), font=pt20_light)
    draw.text((875,28), f'[{version}]', fill=(255, 255, 255), font=pt30_light, anchor='rt')
    draw.text((875,70), '★', fill=(255, 255, 255), font=special, anchor='rt')
    draw.text((875,112), 'pp', fill=(255, 255, 255), font=pt25_light, anchor='rt')

    #--------------------   SCORES LEFT   --------------------#
    draw.text((28,150), f'{" ".join(response.json()[0]["score"])}', fill=(255, 255, 255), font=pt50_regular)

    draw.rectangle([(30,220),(135,260)], fill=(57, 111, 244))
    draw.text((85,227), '300', fill=(47, 49, 54), font=pt35_regular, anchor='mt')
    draw.text((155,227), f'{response.json()[0]["count300"]}', fill=(255, 255, 255), font=pt35_light, anchor='lt')

    draw.rectangle([(30,268),(135,308)], fill=(72, 248, 80))
    draw.text((85,275), '100', fill=(47, 49, 54), font=pt35_regular, anchor='mt')
    draw.text((155,275), f'{response.json()[0]["count100"]}', fill=(255, 255, 255), font=pt35_light, anchor='lt')

    draw.rectangle([(30,316),(135,356)], fill=(245, 225, 90))
    draw.text((85,323), '50', fill=(47, 49, 54), font=pt35_regular, anchor='mt')
    draw.text((155,323), f'{response.json()[0]["count50"]}', fill=(255, 255, 255), font=pt35_light, anchor='lt')

    draw.rectangle([(30,364),(135,404)], fill=(242, 56, 56))
    draw.text((85,371), 'miss', fill=(47, 49, 54), font=pt35_regular, anchor='mt')
    draw.text((155,371), f'{response.json()[0]["countmiss"]}', fill=(255, 255, 255), font=pt35_light, anchor='lt')

    #--------------------   SCORES RIGHT   --------------------#
    draw.text((500,227), 'accuracy:', fill=(255, 255, 255), font=pt35_light, anchor='rt')
    draw.text((510,227), f'{(accuracy/count_sum*100):.2f}%', fill=(142, 142, 142), font=pt35_light, anchor='lt')

    draw.text((500,295), 'combo:', fill=(255, 255, 255), font=pt35_light, anchor='rt')
    draw.text((520,295), f'{response.json()[0]["maxcombo"]}/{beatmap_info.json()[0]["max_combo"]}', fill=(142, 142, 142), font=pt35_light, anchor='lt')
    draw.text((505,310), 'x', fill=(142, 142, 142), font=special, anchor='lt')

    if 'H' in response.json()[0]["rank"]:
        rank = response.json()[0]["rank"][:-1]
    else:
        rank = response.json()[0]["rank"]

    if 'X' in response.json()[0]["rank"]:
        rank = 'SS'

    draw.text((800,250), f'{rank}', fill=rank_colors[response.json()[0]["rank"]], font=pt200_regular, anchor='mt')

    if count_sum != total_count:
        draw.text((450,450), f'completion: {round(completion*100, 2)}%', fill=(255, 255, 255), font=pt35_light, anchor='mt')

    mod_code = int(response.json()[0]['enabled_mods'])
    mod_code = list(bin(mod_code)[2:]) 
    mod_code.reverse()

    if len(mod_code)== 1 and mod_code[0] == '0': 
        mods = [Image.fromarray(np.array(data['NM'], dtype=np.uint8))]
    else: 
        mods = [Image.fromarray(np.array(data[mod_list[x]], dtype=np.uint8)) for x in range(len(mod_code)) if mod_code[x] == '1']

    mod_request = [mod_list[x] for x in range(len(mod_code)) if mod_code[x] == '1']

    if ('SD' in mods) and ('PF' in mods): mods.remove(Image.fromarray(np.array(data['SD'], dtype=np.uint8)))
    if ('DT' in mod_request) and ('NC' in mod_request): 
        mod_request.remove('DT')
        mods.remove(Image.fromarray(np.array(data['DT'], dtype=np.uint8)))

    if any(item in ['EZ', 'HR', 'DT', 'NC', 'HT'] for item in mod_request):
        mod_request = sum([mod_values[x] for x in mod_request if x in ['EZ', 'HR', 'DT', 'NC', 'HT']])
        try:
            beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={response.json()[0]["beatmap_id"]}&mods={mod_request}&m={mode}')
            beatmap_info.json()[0]
        except IndexError:
            beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={response.json()[0]["beatmap_id"]}&mods={mod_request}&m={mode}&a=1')


    draw.text((850,70), f'{(float(beatmap_info.json()[0]["difficultyrating"])):.2f}', fill=(255, 255, 255), font=pt25_light, anchor='rt')

    try:
        pp, _, _, _, _ = osu.ppv2(aim_stars=float(beatmap_info.json()[0]["diff_aim"]), 
                                speed_stars=float(beatmap_info.json()[0]["diff_speed"]), 
                                max_combo=int(beatmap_info.json()[0]["max_combo"])*completion, 
                                nsliders=int(beatmap_info.json()[0]["count_slider"])*completion, 
                                ncircles=int(beatmap_info.json()[0]["count_normal"])*completion, 
                                nobjects=int(beatmap_info.json()[0]["count_spinner"])*completion, 
                                base_ar=float(beatmap_info.json()[0]["diff_approach"]), 
                                base_od=float(beatmap_info.json()[0]["diff_overall"]), 
                                mode=int(beatmap_info.json()[0]["mode"]), 
                                mods=int(response.json()[0]["enabled_mods"]), 
                                combo=int(response.json()[0]["maxcombo"]), 
                                n300=int(response.json()[0]["count300"]), 
                                n100=int(response.json()[0]["count100"]), 
                                n50=int(response.json()[0]["count50"]), 
                                nmiss=int(response.json()[0]["countmiss"]), 
                                score_version=1)
        pp = round(pp, 2)
    
    except TypeError:
        pp = 'NaN'

    draw.text((840,112), f'{pp}', fill=(255, 255, 255), font=pt25_light, anchor='rt')

    mod_bg = Image.new('RGBA', (len(mods)*71,50), color=(47, 49, 54, 255))
    a = Image.new('RGBA', (len(mods)*71,50), color=(47, 49, 54, 255))

    [a.paste(mods[x].resize((71,50)), (71*x,0)) for x in range(len(mods))]

    a = Image.alpha_composite(mod_bg, a)

    if len(mods) == 7:
        img.paste(a, (218, 355))
    else:
        img.paste(a, (290, 355))
    
    return img

def display_plays(api_link, api_key, response, beatmap_id=None, mode=0, repetitions=5):
    with open(image_data) as file:
        data = json.load(file)

    img = Image.new('RGBA', (900,250*repetitions), color=(0, 0, 0, 255))

    pt18_light = ImageFont.truetype(lemon_milk_light, 18)

    pt150_regular = ImageFont.truetype(lemon_milk_regular, 150)
    pt30_regular = ImageFont.truetype(lemon_milk_regular, 30)
    pt18_regular = ImageFont.truetype(lemon_milk_regular, 18)

    special = ImageFont.truetype(special_characters, 18)

    mod_list = ['NF', 'EZ', 'TD', 'HD', 'HR', 'SD', 'DT', '', 'HT', 'NC', 'FL', '', 'SO', '', 'PF', '', '', '', '', '', 'FI', '', '', '', '', '', '', '', '', '', 'MR']
    rank_colors = {
        'F': (242, 56, 56),
        'D': (242, 56, 56),
        'C': (119, 57, 189),
        'B': (57, 111, 244),
        'A': (72, 248, 80),
        'S': (245, 225, 90),
        'X': (255, 223, 6),
        'SH': (170, 183, 204),
        'XH': (170, 183, 204)
    }
    mod_values = {
        'EZ': 2,
        'HR': 16,
        'DT': 64,
        'NC': 64,
        'HT': 256
    }

    for i in range(repetitions):
        decal = 250*i

        if beatmap_id==None:
            beatmap_id = response.json()[i]["beatmap_id"]

        try:
            beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={beatmap_id}&m={mode}')
            beatmap_info.json()[0]
        except IndexError:
            beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={beatmap_id}&m={mode}&a=1')

        beatmap_cover = Image.open(requests.get(f'https://assets.ppy.sh/beatmaps/{beatmap_info.json()[0]["beatmapset_id"]}/covers/cover.jpg', stream=True).raw)
        beatmap_cover = beatmap_cover.resize((900,250))
        beatmap_cover = beatmap_cover.convert('RGBA')

        img.paste(beatmap_cover, (0,0+decal))

        draw = ImageDraw.Draw(img)
        draw.polygon(([200, 0+decal, 900, 0+decal, 900, 250+decal, 160, 250+decal]), fill=(47, 49, 54))
        draw.line([(200, 0+decal), (160, 250+decal)], fill=(102, 104, 110), width=3)
        draw.rectangle(((0,0+decal), (898,250+decal)), fill=None, outline=(64, 67, 73), width=2)

        #--------------------   HEADER   --------------------#
        draw.text((220,10+decal), f'{beatmap_info.json()[0]["title"]}', fill=(255, 255, 255), font=pt30_regular)
        draw.text((220,42+decal), f'[{beatmap_info.json()[0]["version"]}]', fill=(142, 142, 142), font=pt18_light)

        #-------------------- LEFT INFO --------------------#
        draw.rectangle([(220,80+decal),(272,103+decal)], fill=(57, 111, 244))
        draw.text((248,85+decal), '300', fill=(47, 49, 54), font=pt18_regular, anchor='mt')
        draw.text((283,85+decal), f'{response.json()[i]["count300"]}', fill=(255, 255, 255), font=pt18_light, anchor='lt')

        draw.rectangle([(220,108+decal),(272,131+decal)], fill=(72, 248, 80))
        draw.text((248,113+decal), '100', fill=(47, 49, 54), font=pt18_regular, anchor='mt')
        draw.text((283,113+decal), f'{response.json()[i]["count100"]}', fill=(255, 255, 255), font=pt18_light, anchor='lt')

        draw.rectangle([(220,136+decal),(272,159+decal)], fill=(245, 225, 90))
        draw.text((248,141+decal), '50', fill=(47, 49, 54), font=pt18_regular, anchor='mt')
        draw.text((283,141+decal), f'{response.json()[i]["count50"]}', fill=(255, 255, 255), font=pt18_light, anchor='lt')

        draw.rectangle([(220,164+decal),(272,187+decal)], fill=(242, 56, 56))
        draw.text((248,168+decal), 'miss', fill=(47, 49, 54), font=pt18_regular, anchor='mt')
        draw.text((283,168+decal), f'{response.json()[i]["countmiss"]}', fill=(255, 255, 255), font=pt18_light, anchor='lt')

        #-------------------- LEFT INFO --------------------#
        accuracy = int(response.json()[i]["count300"]) + int(response.json()[i]["count100"])*(1/3) + int(response.json()[i]["count50"])*(1/6)
        count_sum = int(response.json()[i]["count300"]) + int(response.json()[i]["count100"]) + int(response.json()[i]["count50"]) + int(response.json()[i]["countmiss"])

        draw.text((490,85+decal), 'difficulty:', fill=(255, 255, 255), font=pt18_light, anchor='rt')
        draw.text((550,85+decal), '★', fill=(142, 142, 142), font=special, anchor='lt')

        draw.text((490,113+decal), 'combo:', fill=(255, 255, 255), font=pt18_light, anchor='rt')
        draw.text((510,113+decal), f'{response.json()[i]["maxcombo"]}/{beatmap_info.json()[0]["max_combo"]}', fill=(142, 142, 142), font=pt18_light, anchor='lt')
        draw.text((500,118+decal), 'x', fill=(142, 142, 142), font=special, anchor='lt')

        draw.text((490,141+decal), 'pp:', fill=(255, 255, 255), font=pt18_light, anchor='rt')
        draw.text((500,141+decal), f'{response.json()[i]["pp"]}', fill=(142, 142, 142), font=pt18_light, anchor='lt')

        draw.text((490,168+decal), 'accuracy:', fill=(255, 255, 255), font=pt18_light, anchor='rt')
        draw.text((500,168+decal), f'{(accuracy/count_sum*100):.2f}%', fill=(142, 142, 142), font=pt18_light, anchor='lt')

        #--------------------   RANK   --------------------#
        if 'H' in response.json()[i]["rank"]:
            rank = response.json()[i]["rank"][:-1]
        else:
            rank = response.json()[i]["rank"]

        if 'X' in response.json()[i]["rank"]:
            rank = 'SS'

        draw.text((775,125+decal), f'{rank}', fill=rank_colors[response.json()[i]["rank"]], font=pt150_regular, anchor='mm')

        #--------------------   MODS   --------------------#
        mod_code = int(response.json()[i]["enabled_mods"])
        mod_code = list(bin(mod_code)[2:]) 
        mod_code.reverse()

        if len(mod_code)== 1 and mod_code[0] == '0': 
            mods = [Image.fromarray(np.array(data['NM'], dtype=np.uint8))]
        else: 
            mods = [Image.fromarray(np.array(data[mod_list[x]], dtype=np.uint8)) for x in range(len(mod_code)) if mod_code[x] == '1']

        mod_request = [mod_list[x] for x in range(len(mod_code)) if mod_code[x] == '1']

        if ('SD' in mods) and ('PF' in mods): mods.remove(Image.fromarray(np.array(data['SD'], dtype=np.uint8)))
        if ('DT' in mod_request) and ('NC' in mod_request): 
            mod_request.remove('DT')
            mods.remove(Image.fromarray(np.array(data['DT'], dtype=np.uint8)))

        if any(item in ['EZ', 'HR', 'DT', 'NC', 'HT'] for item in mod_request):
            mod_request = sum([mod_values[x] for x in mod_request if x in ['EZ', 'HR', 'DT', 'NC', 'HT']])
            try:
                beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={beatmap_id}&mods={mod_request}&m={mode}')
                beatmap_info.json()[0]
            except IndexError:
                beatmap_info = requests.get(f'{api_link}get_beatmaps?k={api_key}&b={beatmap_id}&mods={mod_request}&m={mode}&a=1')


        draw.text((500,85+decal), f'{float(beatmap_info.json()[0]["difficultyrating"]):.2f}', fill=(142, 142, 142), font=pt18_light, anchor='lt')

        mod_bg = Image.new('RGBA', (len(mods)*49,36), color=(47, 49, 54, 255))
        a = Image.new('RGBA', (len(mods)*49,36), color=(47, 49, 54, 255))

        [a.paste(mods[x].resize((49,36)), (49*x,0)) for x in range(len(mods))]

        a = Image.alpha_composite(mod_bg, a)

        img.paste(a, (220, 200+decal))
    
    return img

def display_profile(response):
    img = Image.new('RGB', (400,200), color=(47, 49, 54))
    avatar = Image.open(requests.get(f'http://s.ppy.sh/a/{response.json()[0]["user_id"]}', stream=True).raw)
    flag = Image.open(requests.get(f'https://osu.ppy.sh/images/flags/{response.json()[0]["country"]}.png', stream=True).raw)
    title_font = ImageFont.truetype(lemon_milk_regular, 13)
    default_font = ImageFont.truetype(lemon_milk_light, 13)
    rank_font = ImageFont.truetype(lemon_milk_regular, 31)

    avatar = avatar.resize((200,200))
    flag = flag.resize((21,15))

    img.paste(avatar, (200,0))

    draw = ImageDraw.Draw(img)
    draw.polygon([0, 0, 240, 0, 310, 200, 0, 200], fill=(47, 49, 54))
    draw.line([(240, 0), (310, 200)], fill=(102, 104, 110), width=3)

    img.paste(flag, (16,14))

    draw.text((42,12), f'{response.json()[0]["username"]} profile', fill=(255, 255, 255), font=title_font)

    draw.text((16,44), 'rank:', fill=(255, 255, 255), font=default_font)
    draw.text((65,44), f'#{response.json()[0]["pp_rank"]} ({response.json()[0]["country"]}#{response.json()[0]["pp_country_rank"]})', fill=(240, 90, 90), font=default_font)

    draw.text((16,64), 'level:', fill=(255, 255, 255), font=default_font)
    level = response.json()[0]["level"]
    draw.text((69,64), f'{int(float(level))} ({(( float(level)- int(float(level)) )*100):.2f}%)', fill=(240, 90, 90), font=default_font)

    draw.text((16,84), 'net pp:', fill=(255, 255, 255), font=default_font)
    draw.text((75,84), f'{response.json()[0]["pp_raw"]}', fill=(240, 90, 90), font=default_font)

    draw.text((16,104), 'hit accuracy:', fill=(255, 255, 255), font=default_font)
    draw.text((129,104), f'{float(response.json()[0]["accuracy"]):.2f}%', fill=(240, 90, 90), font=default_font)

    draw.text((16,124), 'playcount:', fill=(255, 255, 255), font=default_font)
    draw.text((112,124), f'{response.json()[0]["playcount"]}', fill=(240, 90, 90), font=default_font)

    draw.text((40,148), 'SS', fill=(162, 162, 162), font=rank_font, anchor='mt')
    draw.text((120,148), 'S', fill=(245, 225, 90), font=rank_font, anchor='mt')
    draw.text((200,148), 'A', fill=(76, 208, 54), font=rank_font, anchor='mt')

    draw.text((40,178), f'{int(response.json()[0]["count_rank_ss"]) + int(response.json()[0]["count_rank_ssh"])}', fill=(255, 255, 255), font=default_font, anchor='mt')
    draw.text((120,178), f'{int(response.json()[0]["count_rank_s"]) + int(response.json()[0]["count_rank_sh"])}', fill=(255, 255, 255), font=default_font, anchor='mt')
    draw.text((200,178), f'{int(response.json()[0]["count_rank_a"])}', fill=(255, 255, 255), font=default_font, anchor='mt')

    return img

async def fetch_user_information(msg, cursor, message, special_params):
    try:
        user = msg[1]
        mode = 0

        if user.startswith('<@!'):
            try:
                discord_id = user[user.rfind('!')+1: user.rfind('>')] 
                cursor.execute(f'SELECT user_id FROM users WHERE discord_id={discord_id}') 
                user = cursor.fetchall()
                cursor.execute(f'SELECT gamemode FROM users WHERE discord_id={discord_id}') 
                mode = cursor.fetchall()
                mode = mode[0][0]
                user = int(user[0][0])

            except IndexError:
                await message.channel.send(f'User has not linked their osu account yet')
                return

    except:
        try:
            discord_id = message.author.id
            cursor.execute(f'SELECT user_id FROM users WHERE discord_id={discord_id}') 
            user = cursor.fetchall()
            cursor.execute(f'SELECT gamemode FROM users WHERE discord_id={discord_id}') 
            mode = cursor.fetchall()
            mode = mode[0][0]
            user = int(user[0][0])
        except IndexError:
            await message.channel.send(f'Please set your username first with: `{prefix}setuser <osu username>`')
            return

    if any([x[:3] == '-m=' for x in special_params]):
        try:
            mode = int([x[-1:] for x in special_params if x[:3] == '-m='][0])

            if (mode < 0) or (mode > 3):
                await message.channel.send('Specified gamemode is invalid. \nMake sure you have the right gamemode code: `0= standard; 1= taiko; 2= ctb; 3= mania`!')
                return
        except ValueError:
            await message.channel.send('Specified gamemode is invalid. \nMake sure you have the right gamemode code: `0= standard; 1= taiko; 2= ctb; 3= mania`!')
            return
    
    return (user, mode)

async def send_image(img, message, message_id):
    with BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)

        fetch_message = await message.channel.fetch_message(message_id)
        await fetch_message.delete()

        await message.channel.send(file=discord.File(fp=image_binary, filename=f'response.png'))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    try: 
        if message.content.startswith(re.findall('^<:\w+:\d+>$', message.content)[0]):
            return
    except IndexError:
        pass

    try:
        if message.content.startswith(re.findall('^<@!\d+>$', message.content)[0]):
            return
    except IndexError:
        pass

    try:
        prefix = json.loads(config['SERVERS'][f'{message.channel.guild.id}'])['prefix']

    except KeyError:
        config['SERVERS'][f'{message.channel.guild.id}'] = '{"prefix": "$", "last_map_sent": ""}'  
        with open('config.ini', 'w') as file:  
            config.write(file) 
        
        prefix = '$'

    mydb = mysql.connect(host=config['INIT']['HOST'], user=config['INIT']['USER'], password=config['INIT']['PASSWORD'], db=config['CONFIG']['DATABASE']) 
    mycursor = mydb.cursor()

    try:
        if re.findall('^https://osu.ppy.sh/beatmapsets/\d+#\w+/\d+$', message.content)[0] in message.content:
            config['SERVERS'][f'{message.channel.guild.id}'] = '{"prefix": "' + prefix + '", "last_map_sent": "' + re.findall('\d+$', message.content)[0] + '"}'  
            with open('config.ini', 'w') as file:  
                config.write(file) 
    except IndexError:
        pass

    if message.content.startswith(prefix):
        msg = message.content[len(prefix):]
        msg = msg.split(' ')
        special_params = [msg.pop(-1) for x in range(len(msg)) if msg[-1][:3:2] == '-=']

        if msg[0] == ('hello'):
            await message.channel.send('Hey! How\'s it going?')

        elif msg[0] == ('setuser'):
            try:
                user = msg[1]
            except:
                await message.channel.send(f'Not enough arguments! Command should be formatted as: `{prefix}setuser <osu username>`')
                return

            if any([x[:3] == '-m=' for x in special_params]):
                try:
                    mode = int([x[-1:] for x in special_params if x[:3] == '-m='][0])

                    if (mode < 0) or (mode > 3):
                        await message.channel.send('Specified gamemode is invalid. \nMake sure you have the right gamemode code: `0= standard; 1= taiko; 2= ctb; 3= mania`!')
                        return
                except ValueError:
                    await message.channel.send('Specified gamemode is invalid. \nMake sure you have the right gamemode code: `0= standard; 1= taiko; 2= ctb; 3= mania`!')
                    return

            else:
                mode = 0

            mode_names = ['standard', 'taiko', 'catch the beat', 'mania']
            
            response = requests.get(f'{api_link}get_user?k={api_key}&u={user}')

            if response.json() == []:
                await message.channel.send('Specified username is invalid. \nMake sure you have no spelling mistakes and that spaces are replaced with `_`!')
                return
            else:
                try:
                    mycursor.execute(
                        'INSERT INTO users (discord_id, user_id, username, gamemode) VALUES ' +
                        f'({message.author.id},'+
                        f'{response.json()[0]["user_id"]},' +
                        f'\'{response.json()[0]["username"]}\',' +
                        f'\'{mode}\') ' +
                        f'ON DUPLICATE KEY UPDATE '+
                        f'user_id = {response.json()[0]["user_id"]},'+
                        f'gamemode = {mode},'+
                        f'username = \'{response.json()[0]["username"]}\';'
                    ) 
                    mydb.commit()

                    await message.channel.send(f'Successfully set user for `{mode_names[mode]}`!')

                except Exception as e:
                    await message.channel.send('Something went wrong :pensive:')
                    return
        
        elif msg[0] == ('osu'):
            user, mode = await fetch_user_information(msg, mycursor, message, special_params)

            response = requests.get(f'{api_link}get_user?k={api_key}&u={user}&m={mode}')

            if response.json() == []:
                await message.channel.send('Specified username is invalid. \nMake sure you have no spelling mistakes and that spaces are replaced with `_`!')
                return

            await message.channel.send('Processing...')
            message_id = message.channel.last_message_id

            img = display_profile(response)

            await send_image(img, message, message_id)

        elif msg[0] == ('recent') or msg[0] == ('rs'):
            user, mode = await fetch_user_information(msg, mycursor, message, special_params)

            response = requests.get(f'{api_link}get_user_recent?k={api_key}&u={user}&m={mode}')

            if response.json() == []:
                await message.channel.send('Specified username is either invalid or player has no recent plays within the last 24 hours!')
                return

            await message.channel.send('Processing...')
            message_id = message.channel.last_message_id

            config['SERVERS'][f'{message.channel.guild.id}'] = '{"prefix": "' + prefix + '", "last_map_sent": "' + response.json()[0]['beatmap_id'] + '"}'  
            with open('config.ini', 'w') as file:  
                config.write(file) 

            img = display_play(api_link, api_key, response, mode)
            
            await send_image(img, message, message_id)

        elif msg[0] == ('top') or msg[0] == ('osutop') or msg[0] == ('ot'):
            user, mode = await fetch_user_information(msg, mycursor, message, special_params)

            response = requests.get(f'{api_link}get_user_best?k={api_key}&u={user}&m={mode}')

            if response.json() == []:
                await message.channel.send('Specified username is invalid. \nMake sure you have no spelling mistakes and that spaces are replaced with `_`!')
                return

            await message.channel.send('Processing...')
            message_id = message.channel.last_message_id

            img = display_plays(mode= mode, response= response, api_link= api_link, api_key= api_key)

            await send_image(img, message, message_id)

        elif msg[0] == ('compare') or msg[0] == ('c'):
            user, mode = await fetch_user_information(msg, mycursor, message, special_params)

            last_map = json.loads(config['SERVERS'][f'{message.channel.guild.id}'])['last_map_sent']
            
            if last_map == '':
                await message.channel.send('No recent map detected!')
                return

            response = requests.get(f'{api_link}get_scores?k={api_key}&u={user}&m={mode}&b={last_map}')

            if response.json() == []:
                await message.channel.send('Specified username is invalid or player has no scores on this map. \nMake sure you have no spelling mistakes and that spaces are replaced with `_`!')
                return


            await message.channel.send('Processing...')
            message_id = message.channel.last_message_id

            img = display_plays(mode= mode, beatmap_id= last_map, response= response, api_link= api_link, api_key= api_key, repetitions= len(response.json()))

            await send_image(img, message, message_id)

        elif msg[0] == ('help') or msg[0] == ('h'):
            try:
                param = msg[1]

                if param == ('hello'):
                    embed=discord.Embed(title=f"```{prefix}hello```", description="Command to test if the bot is online", color=0xd77f7f)
                    embed.add_field(name="[example]", value=f"`{prefix}hello` \n`> Hey! How's it going?`", inline=False)
                    await message.channel.send(embed=embed)

                elif param == ('setuser'):
                    embed=discord.Embed(title=f"```{prefix}setuser <osu username> [special params...]```", description="Links your osu account with your discord account. There should be no space after the `=` in a parameter", color=0xd77f7f)
                    embed.add_field(name="[parameters]", value="`<osu username>` - Required parameter. You can specify either osu username or osu user_id.\n"
                                                             + "`[-m=]` - Optional parameter. Specify default mode: `0= standard; 1= taiko; 2= ctb; 3= mania`. Mode is standard by default.\n", inline=False)
                    embed.add_field(name="[example]", value=f"`{prefix}setuser clorox_1g`", inline=False)
                    await message.channel.send(embed=embed)

                elif param == ('osu'):
                    embed=discord.Embed(title=f"```{prefix}osu [osu username] [special params...]```", description="Display osu account stats", color=0xd77f7f)
                    embed.add_field(name="[parameters]", value="`[osu username]` - Optional parameter. You can either input a valid osu username or osu user_id, or you can mention a discord user whose account is linked."
                                                             + "`[-m=] - Optional parameter. Specify which mode you would like to get stats for: `0= standard; 1= taiko; 2= ctb; 3= mania`. Mode is user's default by default.", inline=False)
                    embed.add_field(name="[example]", value=f"`{prefix}osu @clorox_1g`", inline=False)
                    await message.channel.send(embed=embed)

                elif param == ('recent'):
                    embed=discord.Embed(title=f"```{prefix}recent [osu username] [special params...]```", description=f"Display your most recent play. Can be written as either `{prefix}recent` or `{prefix}rs`", color=0xd77f7f)
                    embed.add_field(name="[parameters]", value="`[osu username]` - Optional parameter. You can either input a valid osu username or osu user_id, or you can mention a discord user whose account is linked."
                                                             + "`[-m=] - Optional parameter. Specify which mode you would like to get stats for: `0= standard; 1= taiko; 2= ctb; 3= mania`. Mode is user's default by default."
                                                             + "`[-b=] - Optional parameter. Displays your most recent play within your top 100.", inline=False)
                    embed.add_field(name="[example]", value=f"`{prefix}recent clorox_1g`", inline=False)
                    await message.channel.send(embed=embed)

                elif param == ('osutop'):
                    embed=discord.Embed(title=f"```{prefix}osutop [osu username] [special params...]```", description=f"Display your top 5 pp plays in osu. Can be written as either `{prefix}osutop`, `{prefix}top` or `{prefix}ot`", color=0xd77f7f)
                    embed.add_field(name="[parameters]", value="`[osu username]` - Optional parameter. You can either input a valid osu username or osu user_id, or you can mention a discord user whose account is linked."
                                                             + "`[-m=] - Optional parameter. Specify which mode you would like to get stats for: `0= standard; 1= taiko; 2= ctb; 3= mania`. Mode is user's default by default."
                                                             + "`[-p=] - Optional parameter. Display a certain play in your top 100 plays.", inline=False)
                    embed.add_field(name="[example]", value=f"`{prefix}osutop`", inline=False)
                    await message.channel.send(embed=embed)

                elif param == ('help'):
                    embed=discord.Embed(title=f"```{prefix}help [command]```", description=f"Displays information about a specific command; if nothing is input every available command will be displayed. Can be written as either `{prefix}help` or `{prefix}h`", color=0xd77f7f)
                    embed.add_field(name="[parameters]", value="`[command]` - Optional parameter. You can input a command you would like to know more information about", inline=False)
                    embed.add_field(name="[example]", value=f"`{prefix}help setuser`", inline=False)
                    await message.channel.send(embed=embed)

                elif param == ('changeprefix'):
                    embed=discord.Embed(title=f"```{prefix}changeprefix <new prefix>```", description=f"Changes command prefix. Can only be executed by a user with the 'Administrator' permission.", color=0xd77f7f)
                    embed.add_field(name="[parameters]", value="`<new prefix>` - Required parameter. Input a new parameter", inline=False)
                    embed.add_field(name="[example]", value=f"`{prefix}changeprefix >`", inline=False)
                    await message.channel.send(embed=embed)

                else:
                    await message.channel.send(f'Unknown command. You can use `{prefix}help` or `{prefix}h` to check available commands.')
        
            except:
                embed=discord.Embed(title="Clorox bot Command help", description=f'type `{prefix}help <command>` to get more information about a certain command', color=0xdedede)
                embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/214683663990784002/df18598aed06d8119e1cd09672c369c0.png?size=128")
                embed.add_field(name=f"{prefix}hello", value="Command to test if the bot is online", inline=False)
                embed.add_field(name=f"{prefix}setuser \<osu username\> [special params...]", value="Links your osu account with your discord account", inline=False)
                embed.add_field(name=f"{prefix}osu [osu username] [special params...]", value="Display osu account stats", inline=False)
                embed.add_field(name=f"{prefix}recent [osu username] [special params...]", value="Display your most recent play", inline=False)
                embed.add_field(name=f"{prefix}osutop [osu username] [special params...]", value="Display your top 5 pp plays in osu", inline=False)
                embed.add_field(name=f"{prefix}help [command]", value="Display your top 5 pp plays in osu", inline=False)
                embed.add_field(name=f"{prefix}changeprefix \<new prefix\>", value="Display your top 5 pp plays in osu", inline=False)
                await message.channel.send(embed=embed)

        elif msg[0] == ('osuset'):
            await message.channel.send(f'Please set your username with: `{prefix}setuser <osu username>`')

        elif msg[0] == ('changeprefix'):
            if message.author.guild_permissions.administrator:
                try:
                    new_prefix = msg[1]

                    config['SERVERS'][f'{message.channel.guild.id}'] = '{"prefix": "' + new_prefix + '"}'  
                    with open('config.ini', 'w') as file:  
                        config.write(file) 
                    
                    await message.channel.send(f'Prefix successfully changed to `{new_prefix}`')

                except:
                    await message.channel.send(f'Not enough arguments! Command should be formatted as: `{prefix}changeprefix <new prefix>`')
                    return
            
            else:
                await message.channel.send(f'You do not have enough permissions to execute this command! Please contact an administrator of the server.')

        else:
            await message.channel.send(f'Unknown command. You can use `{prefix}help` or `{prefix}h` to check available commands.')
        
if __name__ == '__main__':
    client.run(config['INIT']['TOKEN'])
