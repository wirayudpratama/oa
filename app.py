from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests, json


import errno
import os
import sys, random, datetime, time, re
import tempfile
import urllib
import cmds
import cinemaxxi
import yify_torrent
import imdbthing
import acc
import sesuatu
import imp
import schedule
import notif
import quiz

from acc import (namaBot, google_key, line_bot_api, handler, db, owner)
from sesuatu import (mau_nonton, pengaturan, panggil)
from bs4 import BeautifulSoup
from linebot.exceptions import LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, CarouselContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, Error, ErrorDetail
)

app = Flask(__name__)

sleep = False

#===========[ NOTE SAVER ]=======================
notes = {}
tokenz = {}
perintah = {}

# Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text="Terima Kasih telah memasukkan "+namaBot.capitalize()+" dalam chat ini ;D\nType Help for command"
            ),
            TextSendMessage(
                text='Agar dapat menggunakan fitur-fitur yang ada, harus add '+namaBot.capitalize()+' sebagai teman dulu yak ;D',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label=namaBot.capitalize(),
                                text=namaBot.capitalize()
                            )
                        )
                    ]
                )  
            )
        ]
    )
    if isinstance(event.source, SourceGroup):
        ruang = event.source.sender_id
    elif isinstance(event.source, SourceRoom):
        ruang = event.source.room_id
    
    db.child(event.source.type).child(ruang).set(time.time())
    try:
        jumlah = db.child(event.source.type).get().val()["total"]
        db.child(event.source.type).child("total").update(jumlah+1)
    except:
        db.child(event.source.type).child("total").set(1)

@handler.add(LeaveEvent)
def handle_leave(event):
    if isinstance(event.source, SourceGroup):
        ruang = event.source.sender_id
    elif isinstance(event.source, SourceRoom):
        ruang = event.source.room_id

    db.child(event.source.type).child(ruang).remove()
    try:
        jumlah = db.child(event.source.type).get().val()["total"]
        db.child(event.source.type).child("total").update(jumlah-1)
    except:
        db.child(event.source.type).child("total").set(0)

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(event.reply_token,
        [
            TextSendMessage(
                text='Terima kasih telah menambahkan '+namaBot+' sebagai teman ;D\n'+namaBot+' akan membantu kamu ketika kamu ingin bermain, cek film bioskop, download film, dan download youtube ;)\nKak '+line_bot_api.get_profile(event.source.user_id).display_name+' bisa mematikan notifikasi jika '+namaBot+' mengganggu :('
            ),
            TextSendMessage(
                text='Panggil saja namaku jika kamu ingin ditemani ;D',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label='Panggil',
                                text=namaBot.capitalize()
                            )
                        )
                    ]
                )
            )
        ]
    )
    data = {'nama':line_bot_api.get_profile(event.source.user_id).display_name,
            'foto':line_bot_api.get_profile(event.source.user_id).picture_url,
            'status':line_bot_api.get_profile(event.source.user_id).status_message,
            'waktu_add':time.time()}
    db.child("pengguna").child(event.source.user_id).set(data)
    try:
        jumlah = db.child("pengguna").get().val()["total"]
        db.child("pengguna").child("total").update(jumlah+1)
    except:
        db.child("pengguna").child("total").set(1)

@handler.add(PostbackEvent)
def handle_postback(event):
    cmds.handle_postback(event)
    yify_torrent.handle_postback(event)
    cinemaxxi.handle_postback(event)
    notif.handle_postback(event)
    quiz.handle_postback(event)
    imdbthing.handle_postback(event)
    sender = event.source.user_id
    if isinstance(event.source, SourceGroup):
        kirim = gid
    elif isinstance(event.source, SourceRoom):
        kirim = event.source.room_id
    else:
        kirim = sender
    
    try:
        if event.postback.data[0] == '/':
            data = event.postback.data[1:].split(" ",1)
            if len(data) > 1:
                cmd, args = data[0].lower(), data[1]
            else:
                cmd, args = data[0].lower(), ""

            if cmd == "pengaturan":
                line_bot_api.reply_message(event.reply_token, pengaturan(sender))

            elif cmd == "lokasi":
                line_bot_api.reply_message(event.reply_token, 
                    TextSendMessage(
                        text='Share lokasi dulu kak '+panggil(sender)+' ;)', 
                        quick_reply=QuickReply(
                            items=[
                            QuickReplyButton(
                                action=LocationAction(
                                    label='Share lokasi'
                                    )
                                )
                            ]
                        )
                    )
                )
                perintah.update({sender:['lokasi',time.time()]})

            elif cmd == "nick":

                if args == sender:
                    gunakan = args
                else:
                    gunakan = sender

                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kak "+panggil(gunakan)+" mau dipanggil apa?"))
                perintah.update({sender:['panggilan', time.time()]})

            elif cmd == "tanggal_lahir":
                
                if args == sender:
                    gunakan = args
                else:
                    gunakan = sender
                    
                db.child("pengguna").child(gunakan).child("tambahan").child("tanggal_lahir").set(event.postback.params['date'])
                sekarang = datetime.datetime.utcfromtimestamp(time.time())
                tanggal = int(sekarang.strftime('%d'))
                bulan = int(sekarang.strftime('%m'))
                tahun = int(sekarang.strftime('%Y'))
                utahun, ubulan, utanggal = event.postback.params['date'].split('-')
                umur = tahun - int(utahun)
                    
                if tanggal < int(utanggal):
                    if bulan < int(ubulan):
                        umur = umur - 1

                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kak "+panggil(gunakan)+" sekarang berumur "+str(umur)+" tahun ;D"))



    except Exception as e:
        try:
            et, ev, tb = sys.exc_info()
            lineno = tb.tb_lineno
            fn = tb.tb_frame.f_code.co_filename
            if sender != owner:
                line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(text='Oopps.. '+namaBot.capitalize()+' ada kesalahan kak :('),
                    TextSendMessage(text='Tapi tenang kak, laporan kesalahan ini terkirim ke owner untuk diperbaiki ;D')
                    ]
                )
            line_bot_api.push_message(owner, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
        except:
            line_bot_api.push_message(owner, TextSendMessage(text="Undescribeable error detected!!"))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    cinemaxxi.handle_location_message(event)
    if event.source.user_id in perintah:
        komando, waktu = perintah[event.source.user_id]
        if komando == "lokasi":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(event.source.user_id)+' sekarang berada di '+event.message.address+' ;)'))
            data = {'nama_lokasi':event.message.address,
                    'latitude':event.message.latitude,
                    'longitude':event.message.longitude}
            db.child("pengguna").child(event.source.user_id).child("tambahan").child("lokasi").set(data)
            del perintah[event.source.user_id]


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    sender = event.source.user_id
    text = event.message.text
    try:

        startTime = time.time()
        cmds.handle_message(event)
        cinemaxxi.handle_message(event)
        yify_torrent.handle_message(event)
        quiz.handle_message(event)
        notif.handle_message(event)
        imdbthing.handle_message(event)
        gid = event.source.sender_id #get group_id
        profil = line_bot_api.get_profile(sender)
        try:
            nama = panggil(sender) #Ini buat nama
        except:
            data = {'nama':line_bot_api.get_profile(event.source.user_id).display_name,
                    'foto':line_bot_api.get_profile(event.source.user_id).picture_url,
                    'status':line_bot_api.get_profile(event.source.user_id).status_message,
                    'waktu_add':time.time()}
            db.child("pengguna").child(event.source.user_id).set(data)
        gambar = profil.picture_url #Ini profile picture
        status = profil.status_message #Ini status di line

        def stimey(total_seconds):
            try:

                MINUTE  = 60
                HOUR    = MINUTE * 60
                DAY     = HOUR * 24

                days    = int( total_seconds / DAY )
                hours   = int( ( total_seconds % DAY ) / HOUR )
                minutes = int( ( total_seconds % HOUR ) / MINUTE )
                seconds = int( total_seconds % MINUTE )

                string = list()
                if days > 0:
                    string.append(str(days) + " hari")
                if hours > 0:
                    string.append(str(hours) + " jam")
                if minutes > 0:
                    string.append(str(minutes) + " menit")
                if seconds > 0:
                    string.append(str(seconds) + " detik")
                else:
                    if len(string) == 0:string.append("0 detik")
                if len(string) > 1:
                    return ", ".join(string[:-1])+", dan "+string[-1]
                else:
                    return ", ".join(string)

            except Exception as e:
                try:
                    et, ev, tb = sys.exc_info()
                    lineno = tb.tb_lineno
                    fn = tb.tb_frame.f_code.co_filename
                    if sender != owner:
                        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Oopps.. '+namaBot.capitalize()+' ada kesalahan kak :('),TextSendMessage(text='Tapi tenang kak, laporan kesalahan ini terkirim ke owner untuk diperbaiki ;D')])
                    line_bot_api.push_message(owner, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
                except:
                    line_bot_api.push_message(owner, TextSendMessage(text="Undescribeable error detected!!"))
        
        if isinstance(event.source, SourceGroup):
            kirim = gid
        elif isinstance(event.source, SourceRoom):
            kirim = event.source.room_id
        else:
            kirim = sender

        def balas(args):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=args))

        def message(args):
            line_bot_api.push_message(kirim, TextSendMessage(text=args))

        def img(args):
            line_bot_api.push_message(kirim, ImageSendMessage(
                original_content_url=args,
                preview_image_url=args))

        if sender in perintah:
            komando, waktu = perintah[sender]

            if komando == "panggilan":
                if text == "Ubah nama panggilan":return
                db.child("pengguna").child(sender).child("tambahan").child("panggilan").set(text)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Mulai sekarang kakak akan kupanggil "+text+" ;D"))
                del perintah[sender]

        if text.lower() == namaBot:
            pesan = FlexSendMessage(
                alt_text="Menu",
                contents=CarouselContainer(
                    contents=[
                        BubbleContainer(
                            styles=BubbleStyle(
                                header=BlockStyle(
                                    background_color='#223e7c'
                                )
                            ),
                            header=BoxComponent(
                                layout='vertical',
                                contents=[
                                    TextComponent(
                                        text='MENU',
                                        align='center',
                                        color='#ffffff'
                                    )
                                ]
                            ),
                            body=BoxComponent(
                                layout='vertical',
                                spacing='md',
                                contents=[
                                    BoxComponent(
                                        layout='horizontal',
                                        spacing='sm',
                                        contents=[
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/k4ybdVvm/movie-icon-11.png',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Film',
                                                            text='Nonton film kuy'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Film',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/CKL3jFbc/theatre-131979040865277936-512.png',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Drama',
                                                            text='Mau nonton drama nih'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Drama',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://goo.gl/S9GjL7',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='YouTube',
                                                            text='Mau nonton YouTube'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='YouTube',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='horizontal',
                                        spacing='sm',
                                        contents=[
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/DzD04rPf/70.png',
                                                        align='center',
                                                        action=PostbackAction(
                                                            label='Main',
                                                            text='Main kuy',
                                                            data='/main'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Permainan',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/q75v5Q3X/69.png',
                                                        align='center',
                                                        action=PostbackAction(
                                                            label='Pengingat',
                                                            text='Atur pengingat',
                                                            data='/pengingat'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Pengingat',
                                                        wrap=True,
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/YqqXtBh6/settings-3-icon.png',
                                                        align='center',
                                                        action=PostbackAction(
                                                            label='Pengaturan',
                                                            text='Pengaturan',
                                                            data='/pengaturan'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Pengaturan',
                                                        size='xs',
                                                        align='center',
                                                        wrap=True
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            footer=BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='© YRP',
                                        size='xxs',
                                        align='start'
                                    ),
                                    TextComponent(
                                        text=namaBot.capitalize()+' '+os.environ.get('HEROKU_RELEASE_VERSION'),
                                        size='xxs',
                                        align='end'
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, [TextComponent(text="Kamu ingin apa hari ini?"), pesan])

        elif text == "Nonton film kuy":
            balas("Ini aku punya beberapa fungsi kalau kak "+nama+" mau nonton film ;)")
            line_bot_api.push_message(kirim, mau_nonton())

        elif namaBot in text.lower() and not text.lower() == namaBot and not sender in cmds.perintah:
            
            if "apa" in text.lower():
                if text.lower()[len(text)-1] == "?":
                    balas(random.choice(["Ya","Tidak","Terkadang","Mungkin","Coba tanya lagi","Entah","Hmm..."]))
                else:
                    balas("Situ bertanya?")

    #=====[ LEAVE GROUP OR ROOM ]==========
        elif 'get out' == text.lower() or 'bye' == text.lower():
            if sender != owner:
                balas("STFU!")
                return
            if isinstance(event.source, SourceGroup):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Good Bye Cruel World'))
                line_bot_api.leave_group(event.source.group_id)
            elif isinstance(event.source, SourceRoom):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Good Bye Cruel World'))
                line_bot_api.leave_room(event.source.room_id)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="No!"))

    if text == '#yudbye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Yudha pergi bye-bye'),
                    TextSendMessage(text='https://secreto.site/id/4462337')
                ])
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Yudha pergi bye-bye'),
                    TextSendMessage(text='https://secreto.site/id/4462337')
                ])
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))
        ################################################

        elif text.lower() == "who am i?":
            #message("You're "+nama)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="You're "+nama))
            line_bot_api.push_message(kirim, ImageSendMessage(
                original_content_url=gambar,
                preview_image_url=gambar
            ))

        elif text[0] == "=":
            data = text[1:].split(" ",1)
            if len(data) > 1:
                cmd, args = data[0].lower(), data[1]
            else:
                cmd, args = data[0].lower(), ""
            
            if cmd == "e":
                if sender != owner:
                    message('STFU!')
                    return
                try:
                    ret = eval(args)
                    if ret == None:
                        message("Done.")
                        return
                    message(str(ret))
                except Exception as e:
                    try:
                        et, ev, tb = sys.exc_info()
                        lineno = tb.tb_lineno
                        fn = tb.tb_frame.f_code.co_filename
                        message("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
                    except:
                        message("Undescribeable error detected!!")

    #=====[ FLEX MESSAGE ]==========
        elif text == 'creator':
            bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://i.postimg.cc/TPMyw4m2/4ed6ac1d5519accf2f7501cc99886dc8.jpg',
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=URIAction(uri='http://line.me/ti/p/%40175qduzr', label='label')
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # title
                        TextComponent(text='Yudha', weight='bold', size='xl'),
                        # review
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/grey_star.png'),
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/grey_star.png'),
                                TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                            flex=0)
                            ]
                        ),
                        # info
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Place',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text='Indonesia',
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Time',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text="10:00 - 23:00",
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        # separator
                        SeparatorComponent(),
                        # websiteAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='Yudha', uri="https://line.me/ti/p/%40175qduzr")
                        )
                    ]
                ),
            )
            message = FlexSendMessage(alt_text="Hi there!", contents=bubble)
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
#=======================================================================================================================
    if text == "redtube on":
    	angka = random.randint(1, 200)
    	r = requests.get('https://api.boteater.co/redtube?page={}'.format(angka))
    	data=r.text
    	data=json.loads(data)
    	for anu in data["result"]:
        	line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url=anu["dl"], preview_image_url=anu["img"]))
    elif text == "xvideos on":
    	angka = random.randint(1, 200)
    	r = requests.get('https://api.boteater.co/xvideos?page={}'.format(angka))
    	data=r.text
    	data=json.loads(data)
    	for anu in data["result"]:
    		line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url=anu["dl"], preview_image_url=anu["img"]))
#=====[ TES MESSAGE ]=============[ ARSYBAI ]======================
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Bot nya bagus?', actions=[
            MessageTemplateAction(label='Yes', text='Yes!'),
            MessageTemplateAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif "/idline: " in event.message.text:
        skss = event.message.text.replace('/idline: ', '')
        sasa = "line.me/ti/p/~" + skss
        text_message = TextSendMessage(text=sasa)
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/artinama: " in event.message.text:
        skss = event.message.text.replace('/artinama: ', '')
        url = requests.get("https://rest.farzain.com/api/nama.php?&apikey=3w92e8nR5eWuDWQShRlh6C1ye&q="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["result"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/zodiac: " in event.message.text:
        skss = event.message.text.replace('/zodiac: ', '')
        url = requests.get("https://triopekokbots026.herokuapp.com/zodiak="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["result"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/tr-th: " in event.message.text:
        skss = event.message.text.replace('/tr-th: ', '')
        url = requests.get("https://api.tanyz.xyz/translateText/?&to=th&text="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["Hasil"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/tr-en: " in event.message.text:
        skss = event.message.text.replace('/tr-en: ', '')
        url = requests.get("https://api.tanyz.xyz/translateText/?&to=en&text="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["Hasil"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/tr-id: " in event.message.text:
        skss = event.message.text.replace('/tr-id: ', '')
        url = requests.get("https://api.tanyz.xyz/translateText/?&to=id&text="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["Hasil"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/acaratv: " in event.message.text:
        skss = event.message.text.replace('/acaratv: ', '')
        url = requests.get("https://rest.farzain.com/api/acaratv.php?&apikey=3w92e8nR5eWuDWQShRlh6C1ye&id="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["result"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/shorturl: " in event.message.text:
        skss = event.message.text.replace('/shorturl: ', '')
        url = requests.get("https://rest.farzain.com/api/url.php?&apikey=3w92e8nR5eWuDWQShRlh6C1ye&id="+ skss)
        data = url.json()
        text_message = TextSendMessage(text=data["url"])
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
    elif "/fs1: " in event.message.text:
        skss = event.message.text.replace('/fs1: ', '')
        message = ImageSendMessage(
        original_content_url='https://rest.farzain.com/api/special/fansign/indo/viloid.php?apikey=rambu&text=' + skss,
        preview_image_url='https://rest.farzain.com/api/special/fansign/indo/viloid.php?apikey=rambu&text=' + skss
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/fs2: " in event.message.text:
        skss = event.message.text.replace('/fs2: ', '')
        message = ImageSendMessage(
        original_content_url='https://rest.farzain.com/api/special/fansign/cosplay/cosplay.php?apikey=rambu&text=' + skss,
        preview_image_url='https://rest.farzain.com/api/special/fansign/cosplay/cosplay.php?apikey=rambu&text=' + skss
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/graffiti: " in event.message.text:
        skss = event.message.text.replace('/graffiti: ', '')
        message = ImageSendMessage(
        original_content_url='https://rest.farzain.com/api/photofunia/graffiti_wall.php?&apikey=3w92e8nR5eWuDWQShRlh6C1ye&text2=Gans&text1=' + skss,
        preview_image_url='https://rest.farzain.com/api/photofunia/graffiti_wall.php?&apikey=3w92e8nR5eWuDWQShRlh6C1ye&text2=Gans&text1=' + skss
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/audio: " in event.message.text:
        skss = event.message.text.replace('/audio: ', '')
        message = AudioSendMessage(
        original_content_url=skss,
        duration=60000
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/video: " in event.message.text:
        skss = event.message.text.replace('/video: ', '')
        message = VideoSendMessage(
        original_content_url=skss,
        preview_image_url='https://i.ibb.co/GFWPRCV/1545946474474.jpg'
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/image: " in event.message.text:
        skss = event.message.text.replace('/image: ', '')
        message = ImageSendMessage(
        original_content_url=skss,
        preview_image_url='https://i.ibb.co/GFWPRCV/1545946474474.jpg'
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/linepost: " in event.message.text:
        skss = event.message.text.replace('/linepost: ', '')
        url = requests.get("https://rest.farzain.com/api/special/line.php?&apikey=vhbotsline&id="+ skss)
        data = url.json()
        message = VideoSendMessage(
        original_content_url=data["result"],
        preview_image_url='https://i.ibb.co/GFWPRCV/1545946474474.jpg'
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/youtubemp4: " in event.message.text:
        skss = event.message.text.replace('/youtubemp4: ', '')
        url = requests.get("https://api.tanyz.xyz/api/ytDown/?link="+ skss)
        data = url.json()
        message = VideoSendMessage(
        original_content_url=data["Hasil"]["urls"][0]["id"],
        preview_image_url='https://i.ibb.co/GFWPRCV/1545946474474.jpg'
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/youtubemp3: " in event.message.text:
        skss = event.message.text.replace('/youtubemp3: ', '')
        url = requests.get("https://rest.farzain.com/api/ytaudio.php?&apikey=rambu&id="+ skss)
        data = url.json()
        message = AudioSendMessage(
        original_content_url=data["result"]["webm"],
        duration=60000
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/smulevideo: " in event.message.text:
        skss = event.message.text.replace('/smulevideo: ', '')
        url = requests.get("https://api.eater.pw/smule?url="+ skss)
        data = url.json()
        message = VideoSendMessage(
        original_content_url=data["result"][0]["video"],
        preview_image_url=data["result"][0]["thumb"]
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/smuleaudio: " in event.message.text:
        skss = event.message.text.replace('/smuleaudio: ', '')
        url = requests.get("https://api.eater.pw/smule?url="+ skss)
        data = url.json()
        message = AudioSendMessage(
        original_content_url=data["result"][0]["video"],
        duration=60000
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/music: " in event.message.text:
        skss = event.message.text.replace('/music: ', '')
        url = requests.get("http://api.zicor.ooo/joox.php?song="+ skss)
        data = url.json()
        message = AudioSendMessage(
        original_content_url=data["url"],
        duration=240000
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/light: " in event.message.text:
        skss = event.message.text.replace('/light: ', '')
        url = requests.get("http://api.zicor.ooo/graffiti.php?text="+ skss)
        data = url.json()
        message = ImageSendMessage(
        original_content_url=data["image"],
        preview_image_url=data["image"]
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/street: " in event.message.text:
        skss = event.message.text.replace('/street: ', '')
        url = requests.get("http://api.zicor.ooo/streets.php?text="+ skss)
        data = url.json()
        message = ImageSendMessage(
        original_content_url=data["image"],
        preview_image_url=data["image"]
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/cookies: " in event.message.text:
        skss = event.message.text.replace('/cookies: ', '')
        url = requests.get("http://api.zicor.ooo/wcookies.php?text="+ skss)
        data = url.json()
        message = ImageSendMessage(
        original_content_url=data["image"],
        preview_image_url=data["image"]
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/sletters: " in event.message.text:
        skss = event.message.text.replace('/sletters: ', '')
        url = requests.get("http://api.zicor.ooo/sletters.php?text="+ skss)
        data = url.json()
        message = ImageSendMessage(
        original_content_url=data["image"],
        preview_image_url=data["image"]
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/goimage: " in event.message.text:
        skss = event.message.text.replace('/goimage: ', '')
        url = requests.get("https://api.eater.pw/googleimg?search="+ skss)
        data = url.json()
        message = ImageSendMessage(
        original_content_url=data["result"][0]["img"],
        preview_image_url=data["result"][0]["img"]
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0

    elif "/apakah " in event.message.text:
        quo = ('Iya','Tidak','Gak tau','Bisa jadi','Mungkin iya','Mungkin tidak')
        jwb = random.choice(quo)
        text_message = TextSendMessage(text=jwb)
        line_bot_api.reply_message(event.reply_token, text_message)
        return 0
        
    if text == '/tiktok':
        url = requests.get("https://rest.farzain.com/api/tiktok.php?country=jp&apikey=3w92e8nR5eWuDWQShRlh6C1ye&type=json")
        data = url.json()
        message = VideoSendMessage(
        original_content_url=data["first_video"],
        preview_image_url='https://i.ibb.co/GFWPRCV/1545946474474.jpg'
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif "/xvideos: " in event.message.text:
        skss = event.message.text.replace('/xvideos: ', '')
        url = requests.get("https://api.boteater.co/xvideos?page="+ skss)
        data = url.json()
        message = VideoSendMessage(
        original_content_url=data["result"][0]["dl"],
        preview_image_url='https://i.ibb.co/GFWPRCV/1545946474474.jpg'
        )
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif (text == '/lokasi') or (text == 'Mylokasi'):
        message = LocationSendMessage(
        title='my location',
        address='Gg. Tentrem, Pasuruhan Lor, Jati, Kabupaten Kudus, Jawa Tengah 59349, Indonesia',
        latitude=-6.8172919,
        longitude=110.8217371
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/bmkg') or (text == 'Bmkg'):
        url = requests.get("https://api.tanyz.xyz/infoUpdateBMKG")
        data = url.json()
        message = TextSendMessage(text=data["Hasil"]["info"])
        line_bot_api.reply_message(event.reply_token, message)
   
#=============[ TOKEN ]=============[ ARSYBAI ]======================
    elif (text == '/chromeos') or (text == 'Chromeos'):
        url = requests.get("https://api.eater.pw/token?header=CHROMEOS")
        data = url.json()
        bsy = data['result'][0]['linktkn']
        bsyr = data['result'][0]['linkqr']
        tokenz[event.source.user_id]= bsy
        message = TextSendMessage(text='「 yudarea 」\nKlik Link Dibawah Ini Untuk Login Token Chrome\n'+bsyr+'\n\nketik /done untuk mendapatkan tokennya')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/iosipad') or (text == 'Iosipad'):
        url = requests.get("https://api.eater.pw/token?header=IOSIPAD")
        data = url.json()
        bsy = data['result'][0]['linktkn']
        bsyr = data['result'][0]['linkqr']
        tokenz[event.source.user_id]= bsy
        message = TextSendMessage(text='「 yudarea 」\nKlik Link Dibawah Ini Untuk Login Token Iosipad\n'+bsyr+'\n\nketik /done untuk mendapatkan tokennya')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/desktopmac') or (text == 'Desktopmac'):
        url = requests.get("https://api.eater.pw/token?header=DESKTOPMAC")
        data = url.json()
        bsy = data['result'][0]['linktkn']
        bsyr = data['result'][0]['linkqr']
        tokenz[event.source.user_id]= bsy
        message = TextSendMessage(text='「 yudarea 」\nKlik Link Dibawah Ini Untuk Login Token Desktopmac\n'+bsyr+'\n\nketik /done untuk mendapatkan tokennya')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/desktopwin') or (text == 'Desktopwin'):
        url = requests.get("https://api.eater.pw/token?header=DESKTOPWIN")
        data = url.json()
        bsy = data['result'][0]['linktkn']
        bsyr = data['result'][0]['linkqr']
        tokenz[event.source.user_id]= bsy
        message = TextSendMessage(text='「 yudarea 」\nKlik Link Dibawah Ini Untuk Login Token Desktopwin\n'+bsyr+'\n\nketik /done untuk mendapatkan tokennya')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/win10') or (text == 'Win10'):
        url = requests.get("https://api.eater.pw/token?header=WIN10")
        data = url.json()
        bsy = data['result'][0]['linktkn']
        bsyr = data['result'][0]['linkqr']
        tokenz[event.source.user_id]= bsy
        message = TextSendMessage(text='「 yudarea 」\nKlik Link Dibawah Ini Untuk Login Token Win10\n'+bsyr+'\n\nketik /done untuk mendapatkan tokennya')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/clova') or (text == 'Clova'):
        url = requests.get("https://api.eater.pw/token?header=CLOVAFRIENDS")
        data = url.json()
        bsy = data['result'][0]['linktkn']
        bsyr = data['result'][0]['linkqr']
        tokenz[event.source.user_id]= bsy
        message = TextSendMessage(text='「 yudarea 」\nKlik Link Dibawah Ini Untuk Login Token Clova\n'+bsyr+'\n\nketik /done untuk mendapatkan tokennya')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '/done') or (text == 'Done'):
        data = tokenz[event.source.user_id]
        cok = requests.get(url = data)
        asu = cok.text
        message = TextSendMessage(text=asu)
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == '999+') or (text == '999++'):
        message = TextSendMessage(text='ckk by')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Bot') or (text == 'bot'):
        message = TextSendMessage(text='Siapa bot? ke bot an lu')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Tes') or (text == 'tes') or (text == 'Test') or (text == 'test'):
        message = TextSendMessage(text='suk beybeh')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Yudha') or (text == 'Yud') or (text == 'yud') or (text == 'yudha'):
        message = TextSendMessage(text='Apa manggil-manggil cogan')
        line_bot_api.reply_message(event.reply_token, message)
    elif text == '.':
        message = TextSendMessage(text='Titik titik amat so high lu')
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Bah') or (text == 'bah'):
        message = TextSendMessage(text='Beh')
        line_bot_api.reply_message(event.reply_token, message)
#=====[ TEMPLATE MESSAGE ]=============[ ARSYBAI ]======================
    elif (text == '/help') or (text == 'help') or (text == 'Help'):
        buttons_template = TemplateSendMessage(
            alt_text='Help message',
            template=ButtonsTemplate(
                title='[ HELP MESSAGE ]',
                text= 'Tap the Button',
                actions=[
                    MessageTemplateAction(
                        label='My Creator',
                        text='/creator'
                    ),
                    MessageTemplateAction(
                        label='Media',
                        text='/media'
                    ),
                    MessageTemplateAction(
                        label='Musik',
                        text='/musik'
                    ),
                    MessageTemplateAction(
                        label='Bot bye',
                        text='#yudbye'
                    )
                ]
            )
        )
        
        line_bot_api.reply_message(event.reply_token, buttons_template)
    elif text == '/media':
        buttons_template = TemplateSendMessage(
            alt_text='Media message',
            template=ButtonsTemplate(
                title='[ MEDIA MESSAGE ]',
                text= '>Tap the Button<',
                actions=[
                    MessageTemplateAction(
                        label='Media 1',
                        text='/media1'
                    ),
                    MessageTemplateAction(
                        label='Media 2',
                        text='/media2'
                    ),
                    MessageTemplateAction(
                        label='Token',
                        text='/listtoken'
                    )
                ]
            )
        )
        
        line_bot_api.reply_message(event.reply_token, buttons_template)
    elif (text == '/media1') or (text == 'media1') or (text == 'Media1'):
        buttons_template = TemplateSendMessage(
            alt_text='Media area',
            template=ButtonsTemplate(
                title='MEDIA COMMAND',
                text= '>Tap the Button<',
                weight= "bold",
                align= 'center',
                actions=[
                    MessageTemplateAction(
                        label='Youtube',
                        text='≽ Use:\n• /youtubemp3:<link>\n• /youtubemp4:<link>'
                    ),
                    MessageTemplateAction(
                        label='Download Smule',
                        text='≽ Use:\n• /smuleaudio:<Link>\n• /smulevideo:<Link>'
                    ),
                    MessageTemplateAction(
                        label='Translate',
                        text='≽ Use:\n• /tr-id:<text>\n• /tr-en:<text>\n• /tr-th:<text>'
                    ),
                    MessageTemplateAction(
                        label='Info Bmkg',
                        text='≽ Use:\n• /bmkg'
                    )
                ]
            )
        )
        
        line_bot_api.reply_message(event.reply_token, buttons_template)
        
    elif (text == '/media2') or (text == 'Media2') or (text == 'media2'):
        buttons_template = TemplateSendMessage(
            alt_text='media area',
            template=ButtonsTemplate(
                title='MEDIA COMMAND',
                text= '>Tap the Button<',
                weight= "bold",
                align= 'center',
                actions=[
                    MessageTemplateAction(
                        label='Image Text',
                        text='≽ Use:\n• /fs1:<Text>\n• /fs1:<Text>\n• /graffiti:<text>\n• /light:<text>\n• /street:<text>\n• /cookies:<text>\n• /sletters:<text>'
                    ),
                    MessageTemplateAction(
                        label='Zodiac',
                        text='≽ Use:\n• /zodiac: <text>'
                    ),
                    MessageTemplateAction(
                        label='Download Timeline',
                        text='≽ Use:\n• /linepost: <LinkTimeline>'
                    ),
                    MessageTemplateAction(
                        label='Checking',
                        text='≽ Use:\n• /audio:<link>\n• /video:<link>\n• /image:<link>'
                    )
                ]
            )
        )
        
        line_bot_api.reply_message(event.reply_token, buttons_template)
#=====[ CAROUSEL MESSAGE ]==========[ ARSYBAI ]======================
    elif text == '/musik':
        buttons_template = TemplateSendMessage(
            alt_text='Enjoy whit music',
            template=ButtonsTemplate(
                title='[ GENDRE MUSIC ]',
                text= '>Tap the Button<',
                actions=[
                    MessageTemplateAction(
                        label='Music Indonesia',
                        text='/Mindo'
                    ),
                    MessageTemplateAction(
                        label='Music Barat',
                        text='/Mbarat'
                    ),
                    MessageTemplateAction(
                        label='Music Kpop',
                        text='/Mkpop'
                    )
                ]
            )
        )
        
        line_bot_api.reply_message(event.reply_token, buttons_template)

    elif text == '/listtoken':
        message = TemplateSendMessage(
            alt_text='Token area',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        title='> LIST TOKEN <',
                        text='yudarea',
                        actions=[
                            MessageTemplateAction(
                                label='>Chromeos<',
                                text='/chromeos'
                            ),
                            MessageTemplateAction(
                                label='>Iosipad<',
                                text='/iosipad'
                            )
                        ]
                    ),
                    CarouselColumn(
                        title='> LIST TOKEN <',
                        text='yudarea',
                        actions=[
                            MessageTemplateAction(
                                label='>Desktopmac<',
                                text='/desktopmac'
                            ),
                            MessageTemplateAction(
                                label='>Desktopwin<',
                                text='/desktopwin'
                            )
                        ]
                    ),
                    CarouselColumn(
                        title='> LIST TOKEN <',
                        text='yudarea',
                        actions=[
                            MessageTemplateAction(
                                label='>Win10<',
                                text='/win10'
                            ),
                            MessageTemplateAction(
                                label='>Clova<',
                                text='/clova'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
#=====[ CAROUSEL MESSAGE ]==========[ ARSYBAI ]======================
    elif (text == '/creator') or (text == 'About'):
        message = TemplateSendMessage(
            alt_text='>My creator<',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        title='Creator-PC',
                        text='This is my creator',
                        actions=[
                            URITemplateAction(
                                label='>ƴudha<',
                                uri='https://line.me/ti/p/~yud.xx'
                            )
                        ]
                    ),
                    CarouselColumn(
                        title='Creator-OA',
                        text='This is my creator',
                        actions=[
                            URITemplateAction(
                                label='>ƴudha<',
                                uri='https://line.me/ti/p/%40175qduzr'
                            )
                        ]
                    ),
                    CarouselColumn(
                        title='My web',
                        text='Hehe',
                        actions=[
                            URITemplateAction(
                                label='>ƴudha<',
                                uri='line://app/1588295307-b1WvO88v'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    if event.message.text == "/app clone":
        buttons_template = TemplateSendMessage(
            alt_text='App clone',
            template=ButtonsTemplate(
                title='Aplikasi clone',
                text='Klik salah satu menu dibawah ini.',
                thumbnail_image_url='https://imgur.com/Hbv4GWl.jpg',
                actions=[
                    URITemplateAction(
                        label='Parallel Space',
                        uri='https://play.google.com/store/apps/details?id=com.lbe.parallel.intl'
                    ),
                    URITemplateAction(
                        label='APP Cloner',
                        uri='https://play.google.com/store/apps/details?id=com.applisto.appcloner'
                    ),
                    URITemplateAction(
                        label='2Accounts',
                        uri='https://play.google.com/store/apps/details?id=com.excelliance.multiaccount'
                    ),
                    URITemplateAction(
                        label='Multi clone',
                        uri='https://play.google.com/store/apps/details?id=com.jumobile.multiapp'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
#=======[ FLEX MESSAGE ]==========[ ARSYBAI ]======================
    elif text == 'yud test':
        message = ImagemapSendMessage(
            base_url='https://i.imgur.com/g8P1V9Q.jpg',
            alt_text='manyimak corom',
            base_size=BaseSize(height=1040, width=1040),
            actions=[
                URIImagemapAction(
                    link_uri='https://line.me/ti/p/%40ajd1759p',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=1040
                    )
                ),
                MessageImagemapAction(
                    text='yudha ganteng',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=1040
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token, message)

#=====[ Sticker MESSAGE ]==========[ ARSYBAI ]======================
    elif (text == 'anjir') or (text == 'Anjir'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/16135443/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'astaghfirullah') or (text == 'Astaghfirullah'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/16135442/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'sackid') or (text == 'Sackid'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/15664374/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'kam') or (text == 'Kam'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/51626494/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Mantul') or (text == 'mantul') or (text == 'Mantap') or (text == 'mantap'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/1072597/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Wadaw') or (text == 'wadaw'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/15671736/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Hlh') or (text == 'hlh'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/15708876/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Huh') or (text == 'huh'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/12690693/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'kaget') or (text == 'Kaget'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/49279761/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'Ngakak') or (text == 'ngakak'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/73760360/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'oksip') or (text == 'Oksip'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
              columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/52002735/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'aw i cry') or (text == 'Aw i cry') or (text == 'Aw i cri') or (text == 'aw i cri'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/19599278/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'makasih') or (text == 'Makasih'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/153453/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'nyimak') or (text == 'Nyimak'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/13162615/IOS/sticker.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'ga') or (text == 'gak') or (text == 'gamau') or (text == 'Gamau') or (text == 'Ga') or (text == 'Gak'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/8683557/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'good night') or (text == 'Good night') or (text == 'selamat malam') or (text == 'Selamat malam'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/8683546/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'hai') or (text == 'Hai') or (text == 'halo') or (text == 'Halo'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/52002738/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'sabar') or (text == 'Sabar'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/22499899/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'wkwk') or (text == 'Wkwk'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/27695296/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'hehe') or (text == 'Hehe'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/52002763/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'siap') or (text == 'Siap'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/51626520/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif text == '?':
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/34751035/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'please') or (text == 'Please') or (text == 'tolong') or (text == 'Tolong'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/51626499/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'ok') or (text == 'oke') or (text == 'Ok') or (text == 'Oke'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/51626500/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'hahaha') or (text == 'Hahaha') or (text == 'Haha')or (text == 'haha'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/40381622/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif (text == 'sebel') or (text == 'Sebel'):
        message = TemplateSendMessage(
            alt_text='yudarea',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://stickershop.line-scdn.net/stickershop/v1/sticker/52114135/IOS/sticker_animation@2x.png',
                        action=URIAction(uri='http://line.me/ti/p/%40175qduzr')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
#=======================================================================================================================
    ############ ERROR HANDLING ############

    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

import os
if __name__ == "__main__":
    sesuatu.reminder()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
