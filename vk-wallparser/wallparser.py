import requests, time, os

def ParseUnicode(text):  #магия, не трогать
	global count
	global testfile
	text = list(text)
	text2 = ""
	for i in range(len(text)):
		temp = text[i]
		try:
			print(temp, file=testfile)
		except UnicodeEncodeError:
			text[i] = " "
	for elem in text:
		text2 += elem
	if count > 30:
		testfile.close()
		testfile = open(".lock", "w")
		count = 0
	count += 1
	return(text2)

def ProcessPosts(id, offs, pcount):
	global token
	global procount
	post = requests.get("https://api.vk.com/method/wall.get?owner_id=" + id + "&offset=" + str(offs) + "&count=" + str(pcount) + "&v=5.52").json()
	posts = post.get("response").get("items")
	posts.reverse()
	for elem in posts:        #получаем пост
		post_id = elem.get("id")
		text = ParseUnicode(elem.get("text"))
		if "attachments" in elem:
			for element in elem.get("attachments"):
				if element.get("type") == "poll":           #проверяем, есть ли вопрос
					poll_text = element.get("poll").get("question")
					answers = element.get("poll").get("answers")
				else:
					answers = -1
		else:
			answers = -1
		print("Запись", id + "_" + str(post_id) + ":", file=outfile)
		print(text, file=outfile)
		if answers != -1:
			print("\nОпрос:", ParseUnicode(poll_text), file=outfile)       #пишем в файл
			print("Варианты ответа:", file=outfile)
			for element in answers:
				print("   -", ParseUnicode(element.get("text")), "(" + str(element.get("votes")), "человек)", file=outfile)
		print("\n", file=outfile)
		print("Processed post", id + "_" + str(post_id))
		procount += 1

token = open("token.txt", "r").read()  #токен в файле
outfile = open("posts.txt", "w")
testfile = open(".lock", "w")
flag = False
count = 0
procount = 0
while flag == False:                                 #получаем id группы
	target = input("ID группы или короткое имя: ")
	id = requests.get("https://api.vk.com/method/groups.getById?group_id=" + target + "&v=5.52&access_token=" + token).json()
	if "response" in id:
		flag = True
		id = "-" + str(id.get("response")[0].get("id"))
		print("Will process group", id)
	else:
		print("Ошибка. Повторите ввод")

wall_count = requests.get("https://api.vk.com/method/wall.get?owner_id=" + id + "&v=5.52&access_token=" + token).json()
if "error" not in wall_count:                     #получаем количество постов
	wall_count = wall_count.get("response").get("count")
else:
	print("Error")
	exit()
posts = []
if wall_count <= 100:
	ProcessPosts(id, 0, 100)
else:
	for i in range(wall_count - 1, -1, -100):
		print("\n\n\n=== Requesting posts... === \n\n\n")
		ProcessPosts(id, i - 1, 100)
		time.sleep(0.355)
if wall_count > 100:
	ProcessPosts(id, 0, wall_count - procount)
outfile.close()
testfile.close()
os.remove(".lock")
print("Все посты сохранены в posts.txt")
