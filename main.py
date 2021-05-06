import selenium.webdriver, flask, random, string, pickle, sys, os, re
from flask import request, jsonify
from time import sleep as delay
from bs4 import BeautifulSoup
from flask import send_file


import chesscombot as cb

os.system("killall firefox")

try:
	with open('sessions.list', 'rb') as f:
		sessions = pickle.load(f)
except:
	sessions = {}



def navigate(page,sess=None,refresh=False,timing=False,ThirdUser=False):
	if ThirdUser:
		mydriver = driver
	else:
		mydriver = driver
	mydriver.delete_all_cookies()
	if sess == None or ThirdUser != False:
		pass
	else:
		try:
			cookies = sessions[sess]
			for cookie in cookies:
				mydriver.add_cookie(cookie)
		except KeyError:
			print("relogin")
			pass
	if refresh or mydriver.current_url != page:
		mydriver.get(page)
		if timing:
			delay(3)

def saveSessions():
	with open('sessions.list', 'wb') as f:
		pickle.dump(sessions, f)

def create_game(sess, time, username,rated):
	navigate("https://www.chess.com/play/online",sess,refresh=True)
	try:
		delay(1)
		#driver.find_element_by_css_selector("#board-layout-sidebar > div > div.tabs-component.tabs-with-dark-mode > a.tabs-tab.tabs-active").click()
		#delay(2)
		#driver.find_element_by_xpath("/html/body/div[3]/div/div[1]/a[1]/span[3]").click()
	except Exception as e:
		print("\n\n\n"+f"{e}")
		pass

	gameid = cb.timecontrol(rated,time,driver)
	#gameid = 2376463

	soup = BeautifulSoup(driver.page_source,features='lxml')
	color = None
	item = soup.find('div', attrs={'class':'clock-bottom'})
	if "clock-black" in item["class"]:
		color = 'black'
	else:
		color = 'white'

	return gameid,color

def move_game(sess, gameid):
	return True

def get_pgn(sess,gameid):
	pgn = "game pgn"
	return pgn

def create_session(username, password,ThirdUser=False):
	if ThirdUser:
		mydriver = driver
		key = 'ThirdUser'
	else:
		mydriver = driver
		key = ''.join(random.choices(string.ascii_letters + string.digits, k=15))

	navigate("https://www.chess.com/login_and_go",ThirdUser=ThirdUser)

	usernameField = mydriver.find_element_by_id("username")
	usernameField.send_keys(username)

	passwordField = mydriver.find_element_by_id("password")
	passwordField.send_keys(password)

	mydriver.find_element_by_id("_remember_me").click()

	Submit = mydriver.find_element_by_id("login")
	Submit.click()

	logged_in = mydriver.find_elements_by_class_name('home-profile-info')
	error = mydriver.find_elements_by_class_name('authentication-login-error')
	print(len(error))
	finished = False
	while not finished:
		logged_in = mydriver.find_elements_by_class_name('home-profile-info')
		error = mydriver.find_elements_by_class_name('authentication-login-error')
		delay(0.5)
		print(len(error))
		print(".",end="")
		sys.stdout.flush()
		if (len(logged_in) != 0 or len(error) != 0):
			finished = True


	sessions[key] = driver.get_cookies()
	saveSessions()

	#result = test_login(key,ThirdUser=ThirdUser)

	result = True

	if result != True:
		print("Log-In Failed")

	return result, key

def test_login(sess,ThirdUser=True):
	navigate("https://www.chess.com/home",sess,ThirdUser=ThirdUser)
	delay(1)
	if 'login' not in str(driver.current_url).lower():
		return True
	else:
		return False

def init():
	global driver

	profile = selenium.webdriver.FirefoxProfile('/home/festus8070/.mozilla/firefox/ys8519em.default-release/') 
	#profile.add_extension('ublock.xpi')
	firefox_options = selenium.webdriver.FirefoxOptions()
	firefox_options.headless = True
	firefox_options.add_argument("--start-maximized")
	driver = selenium.webdriver.Firefox(firefox_profile=profile,options=firefox_options)
	'''driver.install_addon('src/ublock.xpi')
				driver.install_addon('src/ublock.xpi')'''


	'''chrome_options = selenium.webdriver.ChromeOptions()
				chrome_options.add_argument('headless') # engage headless mode
				chrome_options.add_argument('window-size=1600x1200')
				driver = selenium.webdriver.Chrome(options=chrome_options)
				driver = selenium.webdriver.Chrome(options=chrome_options)'''




	driver.get("https://chess.com")
	delay(5)

	try:
		driver.find_element_by_class_name('section-link-x').click()
	except Exception as e: 
		print(e)

	try:
		driver.find_element_by_css_selector('div.icon-font-chess:nth-child(1)').click()
	except Exception as e: 
		print(e)

	try:
		driver.find_element_by_class_name('v5-header-dismissible-close').click()
	except Exception as e: 
		print(e)



class MyFlaskApp(flask.Flask):
	def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
		if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
			with self.app_context():
				init()
		super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)

@app.route('/test',methods=['GET'])
def api_test():
	if 'sess' in request.args:
		sess = request.args['sess']
	else:
		return '{"result":"", "status":"", "msg":"No sess"}'
	return '{"result":"'+str(test_login(sess))+'", "status":"", "msg":"No sess"}'

@app.route('/', methods=['GET'])

@app.route('/ss',methods=['GET'])
def api_ss():
	if 'driver' in request.args:
		if request.args['driver'] == 'driver':
		 	mydriver = driver
		else:
			return 'False'
	else:
		return 'False'
	mydriver.save_screenshot('ss.png')
	return send_file('/srv/http/gh-project/Chessduino.com/ss.png', mimetype='image/png')

@app.route('/viewer',methods=['GET'])
def api_viewer():
	if 'driver' in request.args:
		arg = request.args['driver']
	else:
		return 'False'
	return '''
	<iframe id="viewer" style="position:fixed; top:0; left:0; bottom:0; right:0; width:100%; height:100%; border:none; margin:0; padding:0; overflow:hidden; z-index:999999;" src="http://127.0.0.1:5000/ss?driver='''+arg+'''"></iframe>
	<script>
	setInterval(function() {
	    iframe = document.getElementById('viewer');
	    if (iframe.src.indexOf('timestamp') > -1) {
	        iframe.src = iframe.src.replace(/timestamp=[^&]+/, 'timestamp=' + Date.now());
	    } else {
	        iframe.src += (iframe.src.indexOf('?') > -1 ? "&" : "?") + 'timestamp=' + Date.now(); // If the URL contains a ?, append &timestamp=...; otherwise,
	    }
	    iframe.contentWindow.location.reload();
	}, 1000)
	</script>
	<style>body{
		background-color:#312E2B;
	}</style>
	'''

def home():
	return '''<h1>Hye</h1>
<p>...</p>'''


@app.route('/api/create_session', methods=['GET'])
def api_create_session():
	if 'username' in request.args:
		username = request.args['username']
	else:
		return '{"key":"", "status":"", "msg":"No username"}'
	if 'password' in request.args:
		password = request.args['password']
	else:
		return '{"key":"", "status":"", "msg":"No password"}'
	status,key = create_session(username,password)
	return '{"key":"'+key+'","status":"'+str(status)+'","msg":""}'


@app.route('/api/create_game', methods=['GET'])
def api_create_game():
	if 'time' in request.args:
		time = request.args['time']
	else:
		return '{"gameid":"", "status":"", "msg":"No time"}'
	if 'rated' in request.args:
		if request.args['rated'] == 'true':
			rated = True
		else:
			rated = False
	else:
		rated = True
	if 'username' in request.args:
		username = request.args['username']
	else:
		return '{"gameid":"", "status":"", "msg":"No username"}'
	if 'key' in request.args:
		key = request.args['key']
	else:
		return '{"key":"", "status":"", "msg":"No session key"}'
	gameid,color = create_game(key,time,username,rated)
	status = True
	return '{"gameid":"'+gameid+'","color":"'+color+'","status":"'+str(status)+'","msg":""}'


@app.route('/api/makemove',methods=['GET'])
def api_makemove():
	if 'key' in request.args:
		key = request.args['key']
	else:
		return '{"result":"", "status":"", "msg":"No key"}'
	if 'mode' in request.args:
		mode = request.args['mode']
	else:
		mode = 'live'
	if 'gameid' in request.args:
		gameid = request.args['gameid']
	else:
		gameid = False
	if 'start' in request.args:
		start = request.args['start']
	else:
		return '{"result":"", "status":"", "msg":"No start Square"}'
	if 'end' in request.args:
		end = request.args['end']
	else:
		return '{"result":"", "status":"", "msg":"No end Square"}'
	if 'color' in request.args:
		color = request.args['color']
	else:
		return '{"result":"", "status":"", "msg":"No color given"}'

	if gameid:
		navigate('https://www.chess.com/game/'+mode+'/'+gameid,key,timing=True)
	return '{"result":"'+str(cb.make_move(start,end,color,driver))+'", "status":"", "msg":""}'

@app.route('/api/gameover',methods=['GET'])
def api_gameover():
	if 'key' in request.args:
		key = request.args['key']
	else:
		return '{"fen":"", "status":"", "msg":"No key"}'
	if 'mode' in request.args:
		mode = request.args['mode']
	else:
		mode = 'live'
	if 'gameid' in request.args:
		gameid = request.args['gameid']
	else:
		return '{"fen":"", "status":"", "msg":"No gameid"}'

	navigate('https://www.chess.com/game/'+mode+'/'+gameid,key,timing=True)
	return str(cb.gameover(driver)["ended"]).lower()

@app.route('/api/myturn',methods=['GET'])
def api_myturn():
	if 'key' in request.args:
		key = request.args['key']
	else:
		return '{"result":"", "status":"", "msg":"No key"}'
	if 'mode' in request.args:
		mode = request.args['mode']
	else:
		mode = 'live'
	if 'gameid' in request.args:
		gameid = request.args['gameid']
	else:
		return '{"result":"", "status":"", "msg":"No gameid"}'

	navigate('https://www.chess.com/game/'+mode+'/'+gameid,key,timing=True)
	return cb.myturn(driver)


@app.after_request
def apply_caching(response):
	response.headers["Connection"] = "close"
	return response

@app.route('/api/test',methods=['GET'])
def api_demo():
	return 'Hello World'

@app.route('/api/fen',methods=['GET'])
def api_fen():
	if 'mode' in request.args:
		mode = request.args['mode']
	else:
		mode = 'live'
	if 'gameid' in request.args:
		gameid = request.args['gameid']
	else:
		return '{"fen":"", "status":"", "msg":"No gameid"}'

	if str(gameid) not in driver.current_url: 
		driver.get('https://www.chess.com/game/'+mode+'/'+gameid)
	fen = cb.get_fen(driver,driver)
	print(fen)
	return '{"fen":"'+fen+'","status":"True","msg":""}'


class x:
	def __del__(self):
		os.system("rm -rf geckodriver.log __pycache__;killall -s SIGKILL firefox")
		#driver.quit()

a = x()



try:	
	app.config["DEBUG"] = True
	app.run(host='0.0.0.0')
finally:
	try:
		driver.quit()
	except:
		pass
	try:
		driver.quit()
	except:
		pass




