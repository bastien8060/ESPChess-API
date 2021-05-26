import chess,chess.engine
import requests,json,random,time,sys,math

engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")
session = 'Saj2UmOZRdwtJvU'
playedbefore = False
oponent_time = 0

def getfen(gameid):
	data = json.loads(requests.get(f'http://127.0.0.1:5000/api/fen?key={session}&gameid={gameid}').content)
	return data['fen']

def gameover(gameid):
	data = requests.get(f'http://127.0.0.1:5000/api/gameover?key={session}&gameid={gameid}').content
	return data.decode().strip() == "true" or 'true' in data

def myturn(gameid):
	data = requests.get(f'http://127.0.0.1:5000/api/myturn?key={session}&gameid={gameid}').content.decode()
	return data.lower() == 'true'

def makemove(start,end,color,gameid):
	print('color:',color)
	data = json.loads(requests.get(f'http://127.0.0.1:5000/api/makemove?key={session}&gameid={gameid}&color={color}&start={start}&end={end}').content)
	return data['result'].lower() == 'true'

def makegame():
	data = json.loads(requests.get(f'http://127.0.0.1:5000/api/create_game?key={session}&time=10-0&username=test_api').content)
	if data['status'] == "True":
		gameid = data['gameid']
		color = data['color']
		print(f'Starting Game ({gameid}) as {color}!')
		return data['gameid'],data['color']
	else:
		raise Exception('Api Error')

def promote(start,end):
	if end[1].isalpha():
		if start[1] == '2': 
			end = start[0]+'1'
		else:
			end = start[0]+'8'
	return end	 

def randfloat():
    return float(random.uniform(0,1))

def getRndBias(mini, maxi, bias=False, influence=0.78):
    if not bias:
        bias = (maxi/100.0)*98.0
    mini,maxi,bias,influence = float(mini),float(maxi),float(bias),float(influence)
    rnd = float(randfloat()) * float(float(maxi - mini) + mini)   # random in range
    mix = randfloat() * influence # random mixer
    i = 1 - mix
    return rnd * i + bias * mix

def getBestMove(fen,color):
	global oponent_time
	board = chess.Board(fen=fen)

	if color == 'black':
		board.turn = chess.BLACK
	oponent_time += 0
	print(f'thinking up to {str(oponent_time)}')
	delay = getRndBias(0, oponent_time)
	oponent_time = 0
	print(f'thinking for {delay}')
	result = engine.play(board, chess.engine.Limit(time=delay))
	board.push(result.move)
	move = str(result.move)
	start = move[:2]
	end = move[-2:]

	print(start,end)

	return start,end

try:
	arg = sys.argv
	gameid = arg[1]
	color = arg[2]
except Exception as e:
	time.sleep(5)
	gameid,color = makegame()

def main():
	global oponent_time
	while True:
		global playedbefore
		if gameover(gameid):
			print('Already Over?')
			engine.quit()
			exit()
		if myturn(gameid):
			print('My Turn!')
			if playedbefore:
				start,end = getBestMove(getfen(gameid),color)
				end = promote(start,end)
			else:
				if color.lower() == 'white':
					print('e4 Player as always')
					start,end = 'e2','e4'
				else:
					print('Scandy going brr')
					start,end = 'd7','d5'
			oponent_time = 0
			print(f'I play {start}{end}')
			if not makemove(start,end,color,gameid):
				print(f"Error! for {start} and {end} on {gameid}")

			if not playedbefore:
				playedbefore = True
				_ = getfen(gameid)

		else:
			oponent_time += 1.1
			print('.',end="")
			sys.stdout.flush()
			time.sleep(1)

'''move = getBestMove('8/8/8/2p3p1/3b4/3k4/6p1/3K4 b - - 1 51','black')

print(move[0],promote(move[0],move[1]))'''

main()





'''

http://127.0.0.1:5000/api/create_game?key={session}&time=10-0&username=test_api
{"gameid":"13630933849","color":"black","status":"True","msg":""}


http://127.0.0.1:5000/api/makemove?key={session}&color=black&start=f7&end=f5
{"result":"True", "status":"", "msg":""}


http://127.0.0.1:5000/api/fen?key={session}&gameid=13533732301
{"fen":"1n3b2/p1r5/8/8/4B1k1/1K1P4/PPP5/8 w KQkq - 0 2","status":"True","msg":""}'''