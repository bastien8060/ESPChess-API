import selenium.webdriver, re, chess
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver import ActionChains  
from time import sleep as delay
from bs4 import BeautifulSoup
import numpy as np

def hanging_line(point1, point2):
	a = (point2[1] - point1[1])/(np.cosh(point2[0]) - np.cosh(point1[0]))
	b = point1[1] - a*np.cosh(point1[0])
	x = np.linspace(point1[0], point2[0], 100)
	y = a*np.cosh(x) + b
	return (x,y)

def square2num(square,prefix=True):
	square = str(ord(square[0]) - 96)+square[1]
	if prefix:
		return "square-"+square
	return square


def make_move(square1,square2,color,driver):
	element = driver.find_element_by_class_name('piece')
	height = element.size['height']

	try:
		square1selector = f"div.piece.{square2num(square1)}"
		element = driver.find_element_by_css_selector(square1selector)
		element.click()
	except:
		return False
	#x1,y1 = element.location['x'],element.location['y']
	#print("Location:",x1,y1)


	square1 = square2num(square1,prefix=False)
	square2 = square2num(square2,prefix=False)

	#print(f'from {square1} to {square2} - square notation\n\n')

	if color == 'white':
		xdiff = -(int(square1[0]) - int(square2[0]))
		ydiff = -(int(square1[1]) - int(square2[1]))
	else:
		xdiff = (int(square1[0]) - int(square2[0]))
		ydiff = (int(square1[1]) - int(square2[1]))
	#print(f'meaning moving right {xdiff} squares')
	#print(f'meaning moving up {ydiff} squares\n\n')

	targetx = int((xdiff * height) + 30)
	targety = int(-(ydiff * height) + 60)

	#print(f'meaning moving right {targetx}px')
	#print(f'meaning moving up {targety}px\n\n')

	actionmouse = ActionChains(driver)
	actionmouse.move_to_element(element)
	actionmouse.perform()




	'''	
	points = hanging_line((0,0),(targetx,targety))
	for i in range(len(points[0])):
		x = int(round(points[0][i],1))
		y = int(round(points[1][i],1))
	
		print('moving')
		actionmouse.move_by_offset(x, y)
		print('performing')
		actionmouse.perform()
		print(x,y)'''


	action = ActionChains(driver)
	action.move_to_element_with_offset(element, targetx, targety).click().perform()
	delay(0.3)

	try:
		driver.find_element_by_css_selector(square1selector)
		return False
	except:
		return True



def myturn(driver):
	try:
		driver.find_element_by_css_selector('.clock-bottom.clock-player-turn')
		return 'true'
	except Exception:
		return 'false'



def gameover(driver):
	try:
		if len(driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[3]/div/div[1]/div')) > 0:
			return {'ended':True}
		else:
			raise Exception('Skipping')
	except Exception as e:
		try:
			count = driver.find_element_by_class_name('key')
			return {'ended':True}
		except Exception as e:
			try:
				count = len(driver.find_elements_by_xpath('/html/body/div[3]/div/div[2]/div/div[4]/div[1]/button[1]')) > 0
				if count:
					return {'ended':True}
				else:
					return {'ended':False}
			except Exception as e:
				try:
					count = len(driver.find_elements_by_xpath('/html/body/div[3]/div/div[2]/div/div[3]/div[1]/div[2]/span[2]')) > 0
					if count:
						print('\n\ncause 4\n\n')
						return {'ended':False}
					else:
						print('\n\ncause 4\n\n')
						return {'ended':True}
				except Exception as e:
					print('\n\ncause 5\n\n')
					print(e)
					source = driver.page_source
					soup = BeautifulSoup(source,features='lxml')
					element = soup.findAll('div', attrs={'class':'live-chat-room'})
					if len(element) > 0:
						if 'Game Over' in str(element):
							return {'ended':True}
					return {'ended':False}



def timecontrol(rated,time,driver):	
	try:
		driver.find_element_by_css_selector('.board-modal-header-close').click() #close you won popup
	except:
		pass
	try:
		driver.find_element_by_css_selector('span.x:nth-child(3)').click() #close game screen
	except:
		pass
	delay(.1)
	try:
		driver.find_element_by_css_selector('span.x:nth-child(3)').click() #close game screen
	except:
		pass
	try:
		driver.find_element_by_class_name('tabs-close').click() #close game screen
	except:
		pass
	driver.find_element_by_xpath('//*[@id="board-layout-sidebar"]/div/div[2]/div/div[1]/div[1]/div/div/button').click()
	if time == '10-0':
		driver.find_element_by_xpath('//*[@id="board-layout-sidebar"]/div/div[2]/div/div[1]/div[1]/div/div/div/div[3]/div/button[1]').click()
	delay(.1)

	if not rated:
		driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[1]/div[3]/div/button[1]').click() #cusstom game menu

		try:
			driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[2]/div/div[1]/div[5]')  #special menu
		except NoSuchElementException:
			driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[2]/div/div[1]/div[4]/div/label/div').click() #toggle


		try:
			driver.find_element_by_xpath('/html/body/div[16]/div/div/button').click()
		except:
			pass

		try:
			driver.find_element_by_xpath('/html/body/div[17]/div/div/button').click()
		except:
			pass
			
		try:
			driver.find_element_by_xpath('/html/body/div[9]/div[3]/a[1]').click() #close lesson popup
		except:
			pass
		try:
			driver.find_element_by_xpath('/html/body/div[9]/div[2]/a[1]').click() #close 'want more lesson popup' popup
		except:
			pass
		try:
			driver.find_element_by_css_selector('.board-modal-header-close').click() 
		except:
			pass
		try:
			driver.find_element_by_css_selector('.board-modal-header-close').click() #close you won popup
		except:
			pass
		try:
			driver.find_element_by_css_selector('span.x:nth-child(3)').click() #close game screen
		except:
			pass
		delay(.1)
		try:
			driver.find_element_by_css_selector('span.x:nth-child(3)').click() #close game screen
		except:
			pass

			


		driver.find_element_by_css_selector('.form-button-component').click()#
	else:
		try:
			driver.find_element_by_xpath('/html/body/div[16]/div/div/button').click()
		except:
			pass

		try:
			driver.find_element_by_xpath('/html/body/div[17]/div/div/button').click()
		except:
			pass
		driver.find_element_by_css_selector('.form-button-component').click()#
		driver.find_element_by_xpath('//*[@id="board-layout-sidebar"]/div/div[2]/div/div[1]/div[1]/div/button').click()

	while ('com/play/online' in driver.current_url):
		delay(.1)

	gameid = re.findall(r'([\d]+)',driver.current_url)[0]
	return gameid


def get_fen(driver,original):
	try:
		soup = BeautifulSoup(original.page_source,features="lxml")
		board = chess.Board()
		for i in soup.find_all('div',{'class':"node"}):
			board.push_san(i.text)
		return str(board.fen())
	except:
		pass


	try:
		delay(1)
		driver.find_element_by_class_name('share').click()
		delay(0.01)
		driver.find_element_by_class_name('share-menu-tab-selector-tab').click()
		try:
			fen = str(driver.find_elements_by_css_selector('input.form-input-input')[1].get_attribute("value"))
		except Exception as e:
			print(e)
			try:
				fen = str(driver.find_elements_by_css_selector('input.form-input-input')[0].get_attribute("value"))
			except:
				try:
					fen = str(driver.find_element_by_css_selector('div.share-menu-tab-pgn-section:nth-child(1) > div:nth-child(2) > input:nth-child(1)').get_attribute("value"))
				except:
					try:
						fen = str(driver.find_element_by_xpath('/html/body/div[8]/div[2]/div[2]/div/section/div[1]/div[1]/div[2]/input').get_attribute("value"))
					except:
						fen = str(driver.find_elements_by_class_name('form-input-input').get_attribute("value"))
		#print(f'\n\n\n\n\n\n\n\ngotcha {fen}')

		driver.find_element_by_xpath('/html/body/div[8]/div[2]/div[1]').click()
		return fen
	except Exception as e:
		try:
			driver.find_element_by_xpath('/html/body/div[8]/div[2]/div[1]').click()
		except:
			pass
		print("\n\n\n\n\n\n\n\nError:",e)

	source = driver.page_source
	soup = BeautifulSoup(source,features="lxml")

	try:
		last_move = soup.find_all('div',{"class":"move"})[-1].attrs['data-whole-move-number']
	except:
		last_move = 1

	matrix = [
	['','','','','','','',''],
	['','','','','','','',''],
	['','','','','','','',''],
	['','','','','','','',''],
	['','','','','','','',''],
	['','','','','','','',''],
	['','','','','','','',''],
	['','','','','','','','']
	]

	chessboard = soup.find('chess-board')
	for i in chessboard.find_all("div", {"class": "piece"}):
		piece = i.attrs['class']
		if piece[1][0] == 'w':
			color = 'w'
		elif piece[1][0] == 'b':
			color = 'b'
		else:
			raise Exception(f'error color not found {piece[1][0]}')
		letter = int(piece[2].replace('square-','')[0])
		number = int(piece[2].replace('square-','')[1])
		name = piece[1][1]
		if color=='w':
			piecename = name.upper()
		else:
			piecename = name
		matrix[7-(number-1)][(letter-1)] = piecename


	fen = ''
	counter = 0
	for line in matrix:
		for square in line:
			if square != '':
				if counter != 0:
					fen += str(counter)
				fen += square
				counter = 0
			else:
				counter += 1
		if counter != 0:
			fen += str(counter)
			counter = 0
		fen += '/'
	fen = fen[:-1]+f' w KQkq - 0 {str(int(last_move)+1)}'
	return fen

