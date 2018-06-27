import os
from pathlib import Path
import shutil
import urllib.request
import lxml
from peewee import *
import sqlite3
import bs4 as bs
import telebot





##### Create SQLite DB, check if file exists - if yes, delete file. Create Database.
sqlite_file = 'seans.sqlite'
db = SqliteDatabase(sqlite_file)
my_file=Path ("db.sqlite")
if my_file.is_file():
    os.remove(sqlite_file)

##### DB Table Description
class BaseModel(Model):
    class Meta:
        database = db

class Seans(BaseModel):
    movie = TextField()
    showtime = TextField()
    cinema = TextField()
    misc = TextField()
    host = TextField()

    def FullName(self):
    	return "*%s*  _\n %s  (%s)  [%s]_  %s" % (self.movie.upper(), self.showtime.upper(), self.cinema.upper(), self.misc.upper(), self.host.upper())

##### Connect to DB
db.connect()
db.create_tables([Seans])

##### For self-check
print("db connected")

##### Cookie handling and parsing source definition for ParkCinema
d = urllib.request.urlopen('start page')
t=d.getheader('Set-Cookie')
req = urllib.request.Request('table page')
req.add_header('Referer', 'start page')
req.add_header('User-Agent', 'USER AGENT')
req.add_header('Cookie',t)
req.add_header('Accept-Language','*****')
req.add_header('Connection','keep-alive')
req.add_header('DNT','1')
req.add_header('Host','host')
req.add_header('X-Requested-With','XMLHttpRequest')
source = urllib.request.urlopen(req)

##### Parsing source for CinemaPlus
source2 = urllib.request.urlopen('another start page')




##### Fetch, parse and organize the data, create HTML file.
f= open("TEMP","a+")

# start HTML
f.write('''
	<head>
		<meta charset="UTF-8">
		<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/material-design-lite/1.1.0/material.min.css">
		<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.16/css/dataTables.material.min.css">
	</head>
	<table id="example" class="mdl-data-table" style="width:100%">
        <thead>
            <tr>
                <th>Movie</th>
                <th>Time</th>
                <th>Cinema</th>
                <th>Misc</th>
                <th>Host</th>
            </tr>
        </thead>
        <tbody>
	''')
all_count=0

# parse first source, organaize, clean and add to DB and HTML
soup = bs.BeautifulSoup(source, 'lxml')
table = soup.find('table')
table_rows = table.find_all('tr')
for tr in table_rows:
     td = tr.find_all('td')
     row = [i.text for i in td]
     row = [w.replace('\n', '') for w in row]
     row = [w.replace('Купить билет ', '') for w in row]
     del row[3]
     all_count+=1
     Seans.create(movie=row[0].upper(), showtime=row[1].upper(), cinema=row[2].upper(), misc=row[3].upper(), host="[PARK CINEMA](https://parkcinema.az)")
     f.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2], row[3], '<a href="https://parkcinema.az">ParkCinema</a>')) 

# For self-check
print("parkcinema")

# parse second source, organaize, clean and add to DB and HTML
soup = bs.BeautifulSoup(source2, 'lxml')
table = soup
table_rows = table.find_all('tr')
for tr in table_rows:
     td = tr.find_all('td')
     row = [i.text for i in td]
     del row[5:7]
     del row[3]
     all_count+=1
     row = [w.replace('Film 3D formatında nümayiş olunurFilm Dolby Atmos formatında nümayiş olunur.Ətraflı məlumat üçün buraya daxil olun.Film Rus dilində nümayiş olunurRU', 'RU ATMOS') for w in row]
     row = [w.replace('Film Azərbaycan subtitrları ilə nümayiş olunurFilm Rus dilində nümayiş olunurRU', 'RU') for w in row]
     row = [w.replace('Film 3D formatında nümayiş olunurFilm Azərbaycan dilində nümayiş olunurAZ', 'AZ 3D') for w in row]
     row = [w.replace('Film 3D formatında nümayiş olunurFilm Rus dilində nümayiş olunurRU', 'RU 3D') for w in row]
     row = [w.replace('Film Azərbaycan subtitrları ilə nümayiş olunurFilm Türk dilində nümayiş olunurTR', 'TR') for w in row]
     row = [w.replace('Film 2D formatında nümayiş olunur2DFilm Azərbaycan dilində nümayiş olunurAZ', 'AZ 2D') for w in row]
     row = [w.replace('Film 2D formatında nümayiş olunur2DFilm Rus dilində nümayiş olunurRU', 'RU 2D') for w in row]
     row = [w.replace('Film 2D formatında nümayiş olunur2DFilm Türk dilində nümayiş olunurTR', 'TR 2D') for w in row]
     row = [w.replace('Film Dolby Atmos formatında nümayiş olunur.Ətraflı məlumat üçün buraya daxil olun.RU 3D', 'RU 3D ATMOS') for w in row]
     Seans.create(movie=row[0].upper(), showtime=row[1].upper(), cinema=row[2].upper(), misc=row[3].upper(), host="[CINEMA PLUS](https://cinemaplus.az)")
     f.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2], row[3], '<a href="https://cinemaplus.az">CinemaPlus</a>'))

# close HTML structure
f.write('''
	        </tbody>
        <tfoot>
            <tr>
                <th>Movie</th>
                <th>Time</th>
                <th>Cinema</th>
                <th>Misc</th>
                <th>Host</th>
            </tr>
        </tfoot>
    </table>
    <script src="https://code.jquery.com/jquery-3.3.1.js"></script>
    <script src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.16/js/dataTables.material.min.js"></script>
    <script>
    $(document).ready(function() {
    $('#example').DataTable( {
        columnDefs: [
            {
                targets: [ 0, 1, 2 ],
                className: 'mdl-data-table__cell--non-numeric'
            }
        ]
    	} );
	} );
	</script>
    ''')


# Close HTML File, remove old file, rename temp file to main
f.close()
my_file=Path ("main.html")
if my_file.is_file():
	os.remove("main.html")

os.rename ("TEMP","main.html")


# For self-check
print("cinemaplus and file")


##### Initiate bot

bot = telebot.TeleBot("MAH TOKEN")

# Bot /start comand handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Здравствуйте! Этот бот создан чтобы собрать все сеансы сетей ParkCinema и CinemaPlus в одном месте. Отправьте команду /all /today или /find для большей информации")


# Bot /all comand handler, drops the link to the HTML file generated earlier
@bot.message_handler(commands=['all'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Сегодня у нас %d сеансов. Чтоб увидеть все - пройдите по [ссылке](your link)" % all_count, parse_mode='Markdown')


# Bot /find comand handler, explains how to use search
@bot.message_handler(commands=['find'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Для поиска по сеансам введите любой текст. Это может быть часть названия фильма ('соло'), названия кинотеатра('bulvar'), или время('16:20'). Пожалуйста, при поиске учитывайте что некоторые сеансы могут быть объявлены на другом языке. Также, учитывайте что некоторые слова могут встречаться слишком часто (например, 'park')")


# Bot /today comand handler, shows all the unique movie titles avialable for today
@bot.message_handler(commands=['today'])
def send_welcome(message):
    unique_today=(Seans.select(Seans.movie).distinct())
    NewMessage="Сегодня в наших кинотеатрах представлены следующие фильмы: \n*"
    for unique in unique_today:
        NewMessage=NewMessage+unique.movie.title()+"\n"
    NewMessage=NewMessage+"*"
    bot.send_message(message.chat.id, NewMessage, parse_mode='Markdown')


# Simple credits
@bot.message_handler(commands=['credits'])
  def send_usd(message):
    bot.send_message(message.chat.id, 'This bot is made by Anvar Shirinbayli aka @muyfamoso (https://t.me/muyfamoso - let me know if there are any issues with bot or you just wanna chat maybe, I dunno) \nCode is (or will be soon) available at https://github.com/AnvarSh1/azn_bot_telegram/ \nFeel free to contact me at enver.shirinbayli@gmal.com \n(You can also send me some PayPal on that e-mail, just sayin) \nYay! \nAnvar Shirinbayli, 2017. \n\n Special thanks to Ramin Q. for his MASSIVE help with this bot.')



# Bot search handler, makes request to the SQLite file
@bot.message_handler(content_types=['text'])
def echo_all(message):
    if len(message.text)==1:
        message.text=message.text+"ts"
    

    my_input = message.text
    NewMessage=""
    all_seans = Seans.select().where(Seans.movie.contains(my_input.upper()) | Seans.cinema.contains(my_input.upper()) | Seans.showtime.contains(my_input.upper()) | Seans.misc.contains(my_input.upper()))
    if not all_seans:
        bot.send_message(message.chat.id, "Ничего не нашлось. Попробуйте поискать что-нибудь еще")
    else:
        for movienames in all_seans:
            NewMessage=NewMessage+movienames.FullName().title()+"\n\n"
            if len(NewMessage)>2900: #splits message if it is too large
                bot.send_message(message.chat.id, NewMessage, parse_mode='Markdown')
                NewMessage=""
        bot.send_message(message.chat.id, NewMessage, parse_mode='Markdown')

# For self-check
print("bot start")

bot.polling()
