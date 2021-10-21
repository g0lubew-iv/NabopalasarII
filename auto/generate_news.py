def generate_news(
		title: str, text: str, href_names: list, href_src: list, author="Nabopalasar II team", img=None,
		meaning="secondary",
		color_text="#ffffff"):
	"""From the news text (and the list of links that will become buttons,
	and an optional image, color of card, etc), we form html markup.
	Everything gets into the json file news. json."""

	import json
	import datetime

	# We use only Bootstrap cards.
	text = text.replace('\n', '<br>')
	href = []
	if len(href_names) != len(href_src):
		return False
	if color_text == '#ffffff':
		color_text = 'white'
	else:
		color_text = 'black'
	for i in zip(href_names, href_src):
		href.append(
			f'<a href="{i[1]}" class="btn btn-outline-{"light" if color_text == "white" else "dark"}" target="_blank">{i[0]}</a>')
	href = '\n'.join(href)
	if img:
		img = f'<img src="{img}" class="card-img-top" alt="An image was here...">'
	else:
		img = ""
	now = datetime.datetime.now()

	res = f"""
	<div class="card text-{color_text} bg-{meaning} mb-3">
    <div class="card-header">
        {author}
    </div>
    <div class="card-body">
	    <h5 class="card-title">{title}</h5>
		<h6 style="color:{'#cccccc' if meaning in ('secondary', 'primary', 'info') else '#333333'};">
	Written {now.day}.{now.month}.{now.year} at {now.hour}:{now.minute}</h6>
	    <p class="card-text">
	        {text}
	    </p>
	    {href}
    </div>
    {img}
	</div>
	"""

	try:
		with open('news.json', mode='r', encoding='utf-8') as f:
			data = json.load(f)
		data['news'].append(res)
		with open('news.json', mode='w', encoding='utf-8') as file:
			json.dump(data, file)
	except Exception as error:
		print(error)
		return False
	return True


if __name__ == '__main__':
	# Our team's news
	pass
	# generate_news(
	# 	'Some advertising', '''A digital board game by <a href="https://itch.io/profile/studiowumpus" style="color: #ffffff" target="_blank">Wumpus studio</a>. Are you interested? Our Nabopalasar II team will be able to tell you everything!
    #             Okay, let's tell you in more detail. Sumer is a cutthroat digital board game about four Sumerian nobles engaged in the game of worship.
    #             What is the genre of this game, you ask? Action meets strategy in this raw struggle for power set at the dawn of civilization.
    #             Barley, pots, goats and gods: all this is in the best Akkadian traditions!''',
	# 	['Read more', 'In Steam'],
	# 	['https://www.sumergame.com', 'https://store.steampowered.com/app/464950/Sumer'], author='Nabopalasar II team',
	# 	img='../static/img/news/outNow_sumer.png', color_text='#ffffff')
	# generate_news(
	# 	'Cookies: do we need milk?', '''As you know very well, our site actively uses cookies. Is it really so dangerous?
    #             A <a href="https://en.wikipedia.org/wiki/HTTP_cookie" style="color: #000000" target="_blank">little theory</a> (Sumerians are allowed). HTTP cookies (also called web cookies, Internet cookies, browser cookies, or simply cookies) are small blocks of data created by a web server while a user is browsing a website and placed on the user's computer or other device by the user’s web browser. Cookies are placed on the device used to access a website, and more than one cookie may be placed on a user’s device during a session. Wiki, thanks.
    #             If you read more than the first paragraph, then we assure you that we only use authentication cookies. Now about our security.
    #             The framework on which Nabopalasar II is written is Tornado. Tornado supports the xsrf_cookies method, this is the most common solution to the cookie vulnerability problem.
    #             <b>Everything all right</b>. Your data will not fall into the hands of intruders.''',
	# 	['Our cookie policy'],
	# 	['/legal/cookie-policy'], author='Nabopalasar II team',
	# 	img='../static/img/news/cook.jpg', color_text='#000000', meaning='warning')
	# generate_news(
	# 	'Check out our error handlers!', '''Of course, no server is protected from errors. Usually because it has clients. In Nabopalasar II, as it is not sad, mistakes also happen...
	# 	Try following <a href= "/vnoevmcoijwemvio4v "style=" color: #ffffff; " >this link</a>. <i>Do you see the eyes?!</i>
	# 	Error 500 is also handled separately. We hope you will never see these eyes. The other errors are an ordinary flashlight.
	# 	Have a good day, our dear Akkadians!''',
	# 	['Generate your own error'],
	# 	['/legal/cookie-policy'], author='Nabopalasar II team',
	# 	img='../static/img/news/oops.jpg', color_text='#ffffff', meaning='danger')
	# generate_news(
	# 	'Gifs on avatars: will they conquer the world?!', '''Today our team noticed a couple of < i>moving avatars</i>, for example, this < a href= "/dfsa"style=" color: #ffffff;">young Akkadian</a> <i>has a ship floating</i>.
	# 	Now you understand our concerns?! No, the server speed will not suffer in any way, we assure you: it is asynchronous. But... Why do you like gifs so much?..
	# 	The standard avatar is the handsome Schumer. What's wrong with him?!
	# 	... As you know. Do not forget that when we reduce the image, we <b>chew</b> it a little.
	# 	Here is this <a href= "/one_eyed John "style=" color: #ffffff; " >Akkadian</a> anime on the avatar is terribly < b>chewed</b>. The quality is spoiling.
	# 	No, we just want to do our best. Remember this.
	# 	All the best, our dear Akkadians!
	# 	''',
	# 	['Get a GIF', 'Get a GIF in another way'],
	# 	['https://giphy.com/', 'https://tenor.com/search/gif-gifs'], author='Nabopalasar II team',
	# 	img='../static/img/news/oops.jpg', color_text='#ffffff', meaning='success')
	#
	# 	generate_news('How does it work?! #1', ''''You noticed <a href= "/teams "style=" color: #000000;">these beautiful pages</a>? Firstly, <i>pagination</i> works everywhere, that is, a huge set of data that we store is divided into separate pages, and everything is for your convenience. The code of the corresponding js functions is partially taken from <a href="/???" style="color: #000000;">StackOwerflow</a>. From here, we also have a few css files (they determine the appearance of pages).
	# Secondly, a lot of our beautiful pieces are borrowed from <a href="/???"style=" color: #000000; ">CodePen</a>, for example, all pages with errors (see our post " Check out our error handlers!"). Thanks to the frontend developers from there! Our team is sincerely grateful to them: we would never agree to do what they do.
	# All the best, our dear Akkadians! Take care of yourself and your cats!
	# ------------
	# An important addition from 2.8.2021. <b>Many thanks</b> to the Tornado team for their work <a href="https://github.com/tornadoweb/tornado/tree/master/demos/chat" style= "color: #000000;" >here</a>.''', [], [], meaning='info', color_text='#000000')
	generate_news('How does it work?! #2', ''''Not only do we have various interesting things (like pagination), we have new interesting things!
Now everything is in order. First of all:
<a href= "/chess" style=" color: #ffffff; " >/chess</a> - super cool chess from the man <b>jakealbaugh</b> (source: https://codepen.io/jakealbaugh/pen/JjRGQPY ). Here you can play for white or black, with a friend or a computer on high or low difficulty. And you can also rotate the board. Phew, that's about it.

Secondly, <a href= "/runner" style=" color: #ffffff; " >/runner</a>. These are pixel runners. Source: https://codepen.io/prim4t/pen/XWdXeab . Well, there's nothing more to say. Just try it!


Third, <a href= "/scrolling" style=" color: #ffffff; " >/scrolling</a>. Source: https://codepen.io/nealagarwal/pen/QpOqQG . Try to find out how fast you scroll the mouse. Everything?
I hope so...''', [], [], color_text='#ffffff')
