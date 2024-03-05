import os
import pprint
from random import randint

import discord
from discord import Intents, Client, Interaction, Message, app_commands, Embed, ui, ButtonStyle, ChannelType
from discord.app_commands import CommandTree, Group
from discord.ext import tasks

from modules.pickleDef import link_dump, link_load, osu_dump, osu_load, name_dump, name_load
from modules.related_mention import find_related_user
from modules.osuDef import osu_id_convert, osu_now_pp, osu_name_convert

#osuコマンド関連
class OsuGroup(Group):

  def __init__(self):
    super().__init__(name="osu", description="osu関連のコマンドです。")

  @app_commands.command(name="link", description="osuのアカウント情報を紐づけます。")
  @app_commands.rename(name="ユーザー名")
  @app_commands.describe(name="osuのユーザー名(表示名)を入力してください。")
  async def link(self, inter: Interaction, name: str):
    global osu_link
    id = osu_id_convert(name)
    if id == None:
      await inter.response.send_message(f"{name}のosu情報が見つかりませんでした。",
                                        ephemeral=True)
    elif inter.user.id in osu_link:
      await inter.response.send_message(
          f"{name}のosu情報はすでにあなたのアカウントに紐づいています。変更する場合は'/osu edit'を利用してください。",
          ephemeral=True)
    else:
      osu_link[inter.user.id] = id
      osu_dump(osu_link)
      await inter.response.send_message(
          f"{inter.user.mention}と{name}のosu情報を紐づけました。", ephemeral=True)

  @app_commands.command(name="edit", description="紐づけ情報を修正します。")
  @app_commands.rename(name="ユーザー名")
  @app_commands.describe(name="新しく紐づけるosuのユーザー名(表示名)を入力してください。")
  async def edit(self, inter: Interaction, name: str):
    global osu_link
    id = osu_id_convert(name)
    if id == None:
      await inter.response.send_message(f"{name}のosu情報が見つかりませんでした。",
                                        ephemeral=True)
    else:
      if inter.user.id in osu_link:
        if (inter.user.id, id) in osu_link.items():
          await inter.response.send_message(f"{name}のosu情報はすでに紐づけられています。",
                                            ephemeral=True)
        else:
          old_name = osu_name_convert(osu_link(inter.user.id))
          osu_link[inter.user.id] = id
          osu_dump(osu_link)
          await inter.response.send_message(
              f"{inter.user.mention}に紐づけられているosu情報を{old_name}から{name}に変更しました。",
              ephemeral=True)

  @app_commands.command(name="refresh",
                        description="osuの情報を更新します。ニックネーム内のppも更新されます。")
  async def refresh(self, inter: Interaction):
    client.schedule.restart()
    await inter.response.send_message("osuの情報を更新しました。", ephemeral=True)

  @app_commands.command(name="delete", description="紐づけ情報を削除します。")
  async def delete(self, inter: Interaction):
    if inter.user.id in osu_link:
      del osu_link[inter.user.id]
      osu_dump(osu_link)
      await inter.response.send_message(
          f"{inter.user.mention}に紐づけられているosu情報を削除しました。", ephemeral=True)

class MLink(Group):

  def __init__(self):
    super().__init__(name="mlink", description="mlink関連のコマンドです。")

  @app_commands.command(name="new", description="2つのアカウントのメンションを紐づけます。")
  @app_commands.rename(acc1="アカウント1", acc2="アカウント2")
  async def new(self, inter: Interaction, acc1: discord.Member,
                acc2: discord.Member):
    global links

    if [acc1.mention, acc2.mention] in links or [acc2.mention, acc1.mention
                                                 ] in links:
      await inter.response.send_message(f"すでにリンクされています。", ephemeral=True)
    else:
      links.append([acc1.mention, acc2.mention])
      link_dump(links)
      await inter.response.send_message(
          f"{acc1.mention}と{acc2.mention}のメンションを紐づけました。", ephemeral=True)

  @app_commands.command(name="delete", description="紐づけ情報を削除します。(入力は順不同)")
  @app_commands.rename(acc1="紐づけたアカウント1", acc2="紐づけたアカウント2")
  async def delete(self, inter: Interaction, acc1: discord.Member,
                   acc2: discord.Member):
    global links

    if [acc1.mention, acc2.mention] in links or [acc2.mention, acc1.mention
                                                 ] in links:
      try:
        del links[links.index([acc1.mention, acc2.mention])]
      except:
        del links[links.index([acc2.mention, acc1.mention])]
      link_dump(links)
      await inter.response.send_message(
          f"{acc1.mention}と{acc2.mention}の紐づけを解除しました。", ephemeral=True)
    else:
      await inter.response.send_message(
          f"{acc1.mention}と{acc2.mention}の紐づけ情報が見つかりませんでした。", ephemeral=True)

#クライアントクラス
class Test(Client):

  #継承
  def __init__(self, intents: Intents):
    super().__init__(intents=intents)
    self.tree = CommandTree(self)

  #同期
  async def setup_hook(self):
    self.tree.add_command(OsuGroup())
    self.tree.add_command(MLink())
    commands = await self.tree.sync()
    pprint.pprint(commands)

  #起動時
  async def on_ready(self):
    print("--------------------")
    print("-----Login Info-----")
    print("--------------------")
    print("Name: " + str(client.user))
    print("ID: " + str(client.user.id))
    print("Discord ver: " + str(discord.__version__))
    print("--------------------")
    print("---Variables Info---")
    print("--------------------")
    print(f"{links=}")
    print(f"{osu_link=}")
    print(f"{base_name=}")
    await client.user.edit(username="なんやかんやbot")
    #await client.change_presence(activity=discord.CustomActivity(name="テスト中", emoji="🤖"))
    await client.change_presence(activity=discord.Activity(name="テスト", type=5))
    client.schedule.start()

  #メッセージ受信時
  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return
    if message.mentions:
      mentioned_user = find_related_user(message, links)
      if mentioned_user:
        await message.reply(f"{' '.join(mentioned_user)}")

  @tasks.loop(seconds=600)
  async def schedule(self):
    global base_name
    for guild in client.guilds:
      for member in guild.members:
        if member.id in osu_link:
          if "<pp>" in member.display_name:
            base_name[member.id, guild.id] = [member.display_name, None]
            name_dump(base_name)
            for k, v in base_name.items():
              if guild.id in k:
                new_name = member.display_name.replace("<pp>", str(osu_now_pp(osu_link[member.id])))
                l = list(base_name[member.id, guild.id])
                l[1] = new_name
                base_name[member.id, guild.id] = l
                name_dump(base_name)

          else:
            if (member.id, guild.id) in base_name:
              for k, v in base_name.items():
                if guild.id in k and base_name[member.id, guild.id][1] == member.display_name:
                  new_name = str(base_name[member.id, guild.id]).replace("<pp>", str(osu_now_pp(osu_link[member.id])))
                  l = list(base_name[member.id, guild.id])
                  l[1] = new_name
                  base_name[member.id, guild.id] = l
                  name_dump(base_name)
            else:
              new_name = None
          try:
            if new_name != None:
              await member.edit(nick=new_name)
              print(f"{guild}の{member}のニックネームを{new_name}に変更")
            else:
              print(f"{guild}の{member}のニックネームに変更なし")
          except:
            print(f"{guild}の{member}のニックネームを変更できず")

class SendChannelView(ui.View):

  def __init__(self, embed: Embed, url_view: ui.View):
    super().__init__()
    self.send_embed = embed
    self.send_url_view = url_view

  @ui.select(cls=ui.ChannelSelect,
             placeholder="チャンネルを選択",
             channel_types=[ChannelType.text])
  async def set_channel(self, inter: Interaction, select: ui.ChannelSelect):
    self.send_button.disabled = False
    self.send_button.style = ButtonStyle.green
    await inter.response.edit_message(view=self)
    self.fav_channel = await select.values[0].fetch()

  @ui.button(label="送信", disabled=True, style=ButtonStyle.gray)
  async def send_button(self, inter: Interaction, button: ui.Button):
    for item in self.children:
      item.disabled = True
    self.send_button.style = ButtonStyle.gray
    await inter.response.edit_message(view=self)
    await self.fav_channel.send(embed=self.send_embed, view=self.send_url_view)
    await inter.delete_original_response()

#初期設定
TOKEN = os.environ["DISCORD_TOKEN"]
intents = Intents.default()
intents.message_content = True
intents.members = True
client = Test(intents=intents)
links = link_load() or []
osu_link = osu_load() or {}
base_name = name_load() or {}

#pingコマンド
@client.tree.command(name="ping", description="動作確認用")
async def ping(inter: Interaction, ):
  await inter.response.send_message(f"pong({round(client.latency * 1000)}ms)",
                                    ephemeral=True)

#イベント発生時の処理
@client.event
async def on_interaction(inter: discord.Interaction):
  try:
    if inter.data["component_type"] == 2:
      await on_button_click(inter)
  except KeyError:
    pass

async def on_button_click(inter: discord.Interaction):
  custom_id = inter.data["custom_id"]
  hands = {"rock": [1, "✊"], "scissor": [2, "✌"], "paper": [3, "✋"]}
  result = [["勝ち", "green"], ["引き分け", "lighter_grey"], ["負け", "red"]]
  cpu_num = randint(1, 3)
  cpu_hand = [k for k, v in hands.items() if v[0] == cpu_num]
  result_num = (hands[custom_id][0] - hands[cpu_hand[0]][0] + 4) % 3
  user_id = inter.user.id

  if custom_id in hands:
    embed = discord.Embed(
        title="じゃんけん結果",
        description=
        f"<@{user_id}>：{hands[custom_id][1]} vs 🤖：{hands[cpu_hand[0]][1]}",
        color=getattr(discord.Colour, result[result_num][1])())
    if result_num == 1:
      embed.add_field(name="", value="あいこ😐")
    else:
      embed.add_field(name="", value=f"<@{user_id}>の{result[result_num][0]}‼️")
    await inter.response.send_message(embed=embed)

#jnknコマンド
@client.tree.command(name="jnkn", description="じゃんけんしろ")
async def jnkn(inter: Interaction):
  button_rock = discord.ui.Button(label="\U0000270A",
                                  style=discord.ButtonStyle.grey,
                                  custom_id="rock")
  button_scissor = discord.ui.Button(label="\U0000270C",
                                     style=discord.ButtonStyle.grey,
                                     custom_id="scissor")
  button_paper = discord.ui.Button(label="\U0001F590",
                                   style=discord.ButtonStyle.grey,
                                   custom_id="paper")
  view = discord.ui.View()
  view.add_item(button_rock)
  view.add_item(button_scissor)
  view.add_item(button_paper)
  await inter.response.send_message("じゃーーんけーーん・・・", view=view, ephemeral=True)

#message_forwardコマンド
@client.tree.context_menu(name="メッセージ転送")
async def message_forward(inter: Interaction, message: Message):
  embed = Embed(title=None)
  attch_desc = []
  if message.content:
    embed.description = message.content
  for attch in message.attachments:
    attch_type, attch_format = attch.content_type.split('/')
    if attch_type == "image" or attch_type == "gif":
      embed.set_image(url=message.attachments[0].url)
      attch_desc.append(f"🖼️{attch.filename}")
    elif attch_type == "video":
      attch_desc.append(f"📺{attch.filename}")
    elif attch_type == "audio":
      attch_desc.append(f"🔊{attch.filename}")
    else:
      attch_desc.append(f"📄{attch.filename}")
  if len(attch_desc) > 0:
    embed.add_field(name="",
                    value=f"---添付ファイル{len(attch_desc)}件---",
                    inline=False)
    for i in range(len(attch_desc)):
      embed.add_field(name="", value=attch_desc[i], inline=False)

  embed.timestamp = message.created_at

  embed.set_author(name=message.author.display_name,
                   icon_url=message.author.display_avatar.url).set_footer(
                       text=f"{inter.user.display_name}により転送",
                       icon_url=inter.user.display_avatar.url)

  url_view = ui.View()
  url_view.add_item(
      ui.Button(label="メッセージに移動する",
                style=ButtonStyle.url,
                url=message.jump_url))

  send_channel_view = SendChannelView(embed=embed, url_view=url_view)
  await inter.response.send_message("どこへ転送しますか？",
                                    view=send_channel_view,
                                    ephemeral=True)

client.run(TOKEN)

