from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import config

def draw_text_centered(draw, text, center_point, max_width=80, max_lines=4, fill='white'):
	lines = []
	string = ''
	size = 20
	done = False
	while not done:
		font = ImageFont.truetype("arial.ttf", size)
		for word in text.split(' '):
			if draw.textsize(string,font=font)[0] >= max_width:
				lines.append(string.strip())
				string = f'{word} '
			else:
				string += f'{word} '
		lines.append(string)
		if len(lines)>max_lines:
			lines=[]
			string=''
			done=False
			size-=2
			if size<12: size+=1
		else: done=True
	y = center_point[1]-(draw.textsize(lines[0],font=font)[1]*len(lines)/2)
	for i,line in enumerate(lines):
		x = center_point[0]-(draw.textsize(lines[i],font=font)[0]/2)
		draw.text((x, y), line, font=font, fill=fill)
		y += draw.textsize(string,font=font)[1]

def draw_title(draw, text):
	size = 30
	font=ImageFont.truetype("arial.ttf", size)
	if draw.textsize(text,font=font)[0]<600: #single line code
		while draw.textsize(text,font=font)[0]>300:
			size-=2
			font=ImageFont.truetype("arial.ttf", size)
		x, y = 150-draw.textsize(text,font=font)[0]/2, 10
		draw.text((x, y), text, font=font, fill="black")
	else: #multi line code
		draw_text_centered(draw, text, (150,25), max_width=250, max_lines=2, fill='black')

def make_question(id, title, questions):
	source_img = Image.new('RGB', (300, 300), "white")
	draw = ImageDraw.Draw(source_img)
	draw.rectangle(((0, 50), (148, 173)), fill=(235, 59, 90)) # RED
	draw.rectangle(((152, 50), (300, 173)), fill=(56, 103, 214)) # BLUE
	draw.rectangle(((0, 177), (148, 300)), fill=(247, 183, 49)) #  YELLOW
	draw.rectangle(((152, 177), (300, 300)), fill=(32, 191, 107)) # GREEN
	
	draw_text_centered(draw, questions[0], (148//2,50+123//2))
	draw_text_centered(draw, questions[1], (152+148//2,50+123//2))
	if len(questions)>2:
		draw_text_centered(draw, questions[2], (148//2,177+123//2))
		if len(questions)>3:
			draw_text_centered(draw, questions[3], (152+148//2,177+123//2))
	draw_title(draw, title)
	source_img.save(config.datafolder+'questions/'+id+'.png', "PNG")