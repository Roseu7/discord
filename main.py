import os
import pprint
from typing import Optional, Literal
from random import randint, sample

import discord
from discord import Intents, Client, Interaction, Message, app_commands, Embed, ui, ButtonStyle, ChannelType, File
from discord.app_commands import CommandTree, Group
from discord.ext import tasks

from modules.pickleDef import link_dump, link_load, osu_dump, osu_load, name_dump, name_load
from modules.related_mention import find_related_user
from modules.osuDef import osu_id_convert, osu_now_pp, osu_name_convert
from modules.mcrconDef import mc_getlist

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
      await inter.response.send_message(f"{name}のosu情報が見つかりませんでした。", ephemeral=True)
    elif inter.user.id in osu_link:
      await inter.response.send_message(f"{name}のosu情報はすでにあなたのアカウントに紐づいています。変更する場合は'/osu edit'を利用してください。", ephemeral=True)
    else:
      osu_link[inter.user.id] = id
      osu_dump(osu_link)
      await inter.response.send_message(f"{inter.user.mention}と{name}のosu情報を紐づけました。", ephemeral=True)

  @app_commands.command(name="edit", description="紐づけ情報を修正します。")
  @app_commands.rename(name="ユーザー名")
  @app_commands.describe(name="新しく紐づけるosuのユーザー名(表示名)を入力してください。")
  async def edit(self, inter: Interaction, name: str):
    global osu_link
    id = osu_id_convert(name)
    if id == None:
      await inter.response.send_message(f"{name}のosu情報が見つかりませんでした。", ephemeral=True)
    else:
      if inter.user.id in osu_link:
        if (inter.user.id, id) in osu_link.items():
          await inter.response.send_message(f"{name}のosu情報はすでに紐づけられています。", ephemeral=True)
        else:
          old_name = osu_name_convert(osu_link(inter.user.id))
          osu_link[inter.user.id] = id
          osu_dump(osu_link)
          await inter.response.send_message(f"{inter.user.mention}に紐づけられているosu情報を{old_name}から{name}に変更しました。", ephemeral=True)

  @app_commands.command(name="refresh",description="osuの情報を更新します。ニックネーム内のppも更新されます。")
  async def refresh(self, inter: Interaction):
    client.schedule.restart()
    await inter.response.send_message("osuの情報を更新しました。", ephemeral=True)

  @app_commands.command(name="delete", description="紐づけ情報を削除します。")
  async def delete(self, inter: Interaction):
    global osu_link, base_name
    if inter.user.id in osu_link:
      del osu_link[inter.user.id]
      osu_dump(osu_link)
      for guild in client.guilds:
        for member in guild.members:
          if member.id == inter.user.id:
            del base_name[member.id, guild.id]
            name_dump(base_name)
      await inter.response.send_message(
          f"{inter.user.mention}に紐づけられているosu情報を削除しました。", ephemeral=True)

class MLink(Group):

  def __init__(self):
    super().__init__(name="mlink", description="mlink関連のコマンドです。")

  @app_commands.command(name="new", description="現在のアカウントともう一つのアカウントのメンションを紐づけます。")
  @app_commands.rename(acc="アカウント")
  async def new(self, inter: Interaction, acc: discord.Member):
    global links

    acc2 = inter.user.mention
    if [acc.mention, acc2] in links or [acc2, acc.mention] in links:
      await inter.response.send_message(f"すでにリンクされています。", ephemeral=True)
    else:
      links.append([acc.mention, acc2])
      link_dump(links)
      await inter.response.send_message(f"現在のアカウントと{acc.mention}のメンションを紐づけました。", ephemeral=True)

  @app_commands.command(name="delete", description="現在のアカウントともう一つのアカウントの紐づけを解除します。")
  @app_commands.rename(acc1="紐づけたアカウント")
  async def delete(self, inter: Interaction, acc1: discord.Member):
    global links

    acc2 = inter.user.mention
    if [acc1.mention, acc2] in links or [acc2, acc1.mention] in links:
      try:
        del links[links.index([acc1.mention, acc2])]
      except:
        del links[links.index([acc2, acc1.mention])]
      link_dump(links)
      await inter.response.send_message(f"現在のアカウントと{acc1.mention}の紐づけを解除しました。", ephemeral=True)
    else:
      await inter.response.send_message(f"現在のアカウントと{acc1.mention}の紐づけ情報が見つかりませんでした。", ephemeral=True)

  # @app_commands.command(name="setup", description="このチャンネルにアカウントリンクのボタンを作成します。")
  # async def setup(self, inter: Interaction):

class Valo(Group):
  def __init__(self):
    super().__init__(name="valo", description="VALORANT関連のコマンドです。")

  #valomapコマンド
  @app_commands.command(name="map", description="VALORANTのマップをランダムにピックします。")
  async def valomap(self, inter: Interaction):
    map_list = [["サンセット", os.path.join(current_dir, "png", "valo", "sunset.png")],
                ["ロータス", os.path.join(current_dir, "png", "valo", "lotus.png")],
                ["パール", os.path.join(current_dir, "png", "valo", "pearl.png")],
                ["フラクチャー", os.path.join(current_dir, "png", "valo", "fracture.png")],
                ["ブリーズ", os.path.join(current_dir, "png", "valo", "breeze.png")],
                ["アイスボックス", os.path.join(current_dir, "png", "valo", "icebox.png")],
                ["バインド", os.path.join(current_dir, "png", "valo", "bind.png")],
                ["ヘイブン", os.path.join(current_dir, "png", "valo", "haven.png")],
                ["スプリット", os.path.join(current_dir, "png", "valo", "split.png")],
                ["アセント", os.path.join(current_dir, "png", "valo", "ascent.png")]]
    n = randint(0, 9)
    await inter.response.send_message(f"{map_list[n][0]}", file=File(map_list[n][1]))

  #valocharaコマンド
  @app_commands.command(name="chara", description="VALORANTのキャラをランダムにピックします。(イメージ画像：白椅ぬゐ @VshiroinuV)")
  @app_commands.rename(player="人数", due="デュエリスト", ini="イニシエーター", con="コントローラー", sen="センチネル")
  @app_commands.describe(player="ランダムピックする人数を指定してください。", due="デュエリストの人数を指定してください。", ini="イニシエーターの人数を指定してください。", con="コントローラーの人数を指定してください。", sen="センチネルの人数を指定してください。")
  async def valochara(self, inter: Interaction, player: Optional[Literal[1, 2, 3, 4, 5]] = 5, due: Optional[Literal[1, 2, 3, 4, 5]] = 0, ini: Optional[Literal[1, 2, 3, 4, 5]] = 0, con: Optional[Literal[1, 2, 3, 4, 5]] = 0, sen: Optional[Literal[1, 2, 3, 4, 5]] = 0):
    chara_due = [["ジェット", os.path.join(current_dir, "png", "valo", "JETT.png")],
                 ["レイズ", os.path.join(current_dir, "png", "valo", "RAZE.png")],
                 ["フェニックス", os.path.join(current_dir, "png", "valo", "PHOENIX.png")],
                 ["レイナ", os.path.join(current_dir, "png", "valo", "RAYNA.png")],
                 ["ヨル", os.path.join(current_dir, "png", "valo", "YORU.png")],
                 ["ネオン", os.path.join(current_dir, "png", "valo", "NEON.png")],
                 ["アイソ", os.path.join(current_dir, "png", "valo", "ISO.png")]]
    chara_ini = [["ブリーチ", os.path.join(current_dir, "png", "valo", "BREACH.png")],
                 ["ソーヴァ", os.path.join(current_dir, "png", "valo", "SOVA.png")],
                 ["スカイ", os.path.join(current_dir, "png", "valo", "SKYE.png")],
                 ["KAY/O", os.path.join(current_dir, "png", "valo", "KAYO.png")],
                 ["フェイド", os.path.join(current_dir, "png", "valo", "FADE.png")],
                 ["ゲッコー", os.path.join(current_dir, "png", "valo", "GEKKO.png")]]
    chara_con = [["オーメン", os.path.join(current_dir, "png", "valo", "OMEN.png")],
                 ["ブリムストーン", os.path.join(current_dir, "png", "valo", "BRIMSTONE.png")],
                 ["ヴァイパー", os.path.join(current_dir, "png", "valo", "VIPER.png")],
                 ["アストラ", os.path.join(current_dir, "png", "valo", "ASTRA.png")],
                 ["ハーバー", os.path.join(current_dir, "png", "valo", "HARBOR.png")],
                 ["クローヴ", os.path.join(current_dir, "png", "valo", "CLOVE.png")]]
    chara_sen = [["セージ", os.path.join(current_dir, "png", "valo", "SAGE.png")],
                 ["サイファー", os.path.join(current_dir, "png", "valo", "CYPHER.png")],
                 ["キルジョイ", os.path.join(current_dir, "png", "valo", "KILLJOY.png")],
                 ["チェンバー", os.path.join(current_dir, "png", "valo", "CHAMBER.png")],
                 ["デッドロック", os.path.join(current_dir, "png", "valo", "DEADLOCK.png")]]
    chara_all = chara_due+chara_ini+chara_con+chara_sen
    pick = []
    message = ""
    images = []
    role = due+ini+con+sen

    if player < role:
      await inter.response.send_message("ロール指定数の合計がプレイヤー数を超えています。", ephemeral=True)
    else:
      if due != 0:
        n = sample(range(len(chara_due)), due)
        for i in range(due):
          pick.append(chara_due[n[i]])
        message += f"デュエリスト{due}人\n"
        chara_all = list(filter(lambda x: x not in chara_due, chara_all))
      if ini != 0:
        n = sample(range(len(chara_ini)), ini)
        for i in range(ini):
          pick.append(chara_ini[n[i]])
        message += f"イニシエーター{ini}人\n"
        chara_all = list(filter(lambda x: x not in chara_ini, chara_all))
      if con != 0:
        n = sample(range(len(chara_con)), con)
        for i in range(con):
          pick.append(chara_con[n[i]])
        message += f"コントローラー{con}人\n"
        chara_all = list(filter(lambda x: x not in chara_con, chara_all))
      if sen != 0:
        n = sample(range(len(chara_sen)), sen)
        for i in range(sen):
          pick.append(chara_sen[n[i]])
        message += f"センチネル{sen}人\n"
        chara_all = list(filter(lambda x: x not in chara_sen, chara_all))
      if role < player:
        n = sample(range(len(chara_all)), player-role)
        for i in range(player-role):
          pick.append(chara_all[n[i]])
        message += f"ランダム{len(n)}人\n"
      for i in range(len(pick)):
        message += f"{pick[i][0]}　　"
        images.append(File(pick[i][1]))
      await inter.response.send_message(message, files=images)

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
    self.tree.add_command(Valo())
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
                  new_name = str(base_name[member.id, guild.id][0]).replace("<pp>", str(osu_now_pp(osu_link[member.id])))
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

  @ui.select(cls=ui.ChannelSelect, placeholder="チャンネルを選択", channel_types=[ChannelType.text])
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
current_dir = os.path.dirname(os.path.abspath(__file__))

#pingコマンド
@client.tree.command(name="ping", description="動作確認用")
async def ping(inter: Interaction):
  await inter.response.send_message(f"pong({round(client.latency * 1000)}ms)", ephemeral=True)

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
  user_id = inter.user.id

  if custom_id in hands:
    result = [["勝ち", "green"], ["引き分け", "lighter_grey"], ["負け", "red"]]
    cpu_num = randint(1, 3)
    cpu_hand = [k for k, v in hands.items() if v[0] == cpu_num]
    result_num = (hands[custom_id][0] - hands[cpu_hand[0]][0] + 4) % 3
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
  elif custom_id == "link":
    await inter.response.send_message("リンクしたいアカウントをこのチャンネルにメンションしてください。", ephemeral=True)

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
    embed.add_field(name="", value=f"---添付ファイル{len(attch_desc)}件---", inline=False)
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
  
@client.tree.command(name="mclist", description="マイクラの鯖が立っている場合のみ、参加している人を表示します。")
async def mclist(inter: Interaction):
  res = mc_getlist()
  await inter.response.send_message(res, ephemeral=True)

client.run(TOKEN)