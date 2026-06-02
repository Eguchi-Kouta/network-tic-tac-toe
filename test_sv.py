import socket
import json
import random
#IPの自動取得
def get_local_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]
	finally:
		s.close()
def recv_line(sock: socket.socket) -> str:
	buf = b""
	while b"\n" not in buf:
		chunk = sock.recv(1024)
		if not chunk:
			raise ConnectionError("クライアントが切断しました")
		buf += chunk
	line, _, _ = buf.partition(b"\n")
	return line.decode("utf-8")
#マップは3×3である
#勝利者の確認判定
def winner_check(board):
	#斜め
	if board[1][1] != "e":
		if board[0][0] == board[1][1] == board[2][2]:
			return board[1][1]
		if board[0][2] == board[1][1] == board[2][0]:
			return board[1][1]
	for i in range(3):
		#横
		if board[i][0] == board[i][1] == board[i][2] and board[i][0] != "e":
			return board[i][0]
		#縦
		if board[0][i] == board[1][i] == board[2][i] and board[0][i] != "e":
			return board[0][i]
	#引き分け
	if all("e" not in row for row in board):
		return "draw"
	#継続
	return "e"
#プレイヤーの移動判定
#入力は"a,b"の形
def player_move_check(c,board):
	if c.count(",") != 1:
		return "形式が正しくありません"
	i,j = c.split(",")
	if not (i.isdigit() and j.isdigit()):
		return "座標が数値になっていません"
	i = int(i)
	j = int(j)
	if not (0 <= i < 3 and 0 <= j < 3):
		return "その座標は存在しません"
	if board[i][j] != "e":
		return "その座標は埋まっています"
	return i,j
#AIの次の手の確認
Lines = [
	#横
	[(0,0),(0,1),(0,2)],
	[(1,0),(1,1),(1,2)],
	[(2,0),(2,1),(2,2)],
	#縦
	[(0,0),(1,0),(2,0)],
	[(0,1),(1,1),(2,1)],
	[(0,2),(1,2),(2,2)],
	#斜め
	[(0,0),(1,1),(2,2)],
	[(0,2),(1,1),(2,0)]]
def find_winning_move(board,target):
	for line in Lines:
		cells = [board[i][j] for i,j in line]
		if cells.count(target) == 2 and cells.count("e") == 1:
			idx = cells.index("e")
			return line[idx]
	return None
def next_move(board, me, enemy):
	#勝利の一手
	pos = find_winning_move(board,me)
	if pos:
		return pos
	#妨害の一手
	pos = find_winning_move(board,enemy)
	if pos:
		return pos
	#中央の確認
	if board[1][1] == "e":
		return 1,1
	#斜めの確認
	for i in (0,2):
		for j in (0,2):
			if board[i][j] == "e":
				return i,j
	#残りを埋める
	for i in range(3):
		for j in range(3):
			if board[i][j] == "e":
				return i,j
IPADDR = get_local_ip()
PORT = 49152
print(f"現在のlocal_ip:{IPADDR}")
print(f"現在のPORT:{PORT}")

sock_sv = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR,PORT))
sock_sv.listen()
print("接続待ち...")
sock_cl, addr = sock_sv.accept()
print("プレイヤーが接続しました")

try:
	while True:
		print("sで開始 / fで終了 を待機中...")
		try:
			res = recv_line(sock_cl)
		except ConnectionError as e:
			print(e)
			break
		if res in ("s","S","ｓ","Ｓ"):
			print("ゲーム開始要求を受信")
			board = [["e" for _ in range(3)] for _ in range(3)]

			print("○(先攻)か×(後攻)か選ばれます")
			selected = random.choice(["○","×"])
			print(f"player：{selected}")
			sock_cl.sendall((selected + "\n").encode("utf-8"))

			if selected == "○":
				player = "○"
				ai = "×"
			else:
				player = "×"
				ai = "○"

			v = json.dumps(board) + "\n"
			sock_cl.sendall(v.encode("utf-8"))
			
			_ = recv_line(sock_cl)

			turn = "○"
			while True:
				w = winner_check(board)
				if w != "e":
					sock_cl.sendall((w + "\n").encode("utf-8"))
					if w == "draw":
						print("draw")
					else:
						print(f"{w} win")
					break
				else:
					sock_cl.sendall(("e\n").encode("utf-8"))

				if turn == player:
					print("your turn")
					error_count = 0
					while True:
						error_count += 1
						try:
							c = recv_line(sock_cl)
						except ConnectionError as e:
							print(e)
							raise
						print(f"player input:  {c}")
						m = player_move_check(c, board)
						if isinstance(m, tuple):
							i,j = m
							break
						else:
							sock_cl.sendall(("ERR:" + m + "\n").encode("utf-8"))
						if error_count >= 20:
							print("入力エラーが多すぎるため終了します")
							raise RuntimeError
					board[i][j] = player
				else:
					print("AI turn")
					i,j = next_move(board,ai,player)
					board[i][j] = ai
				
				v = json.dumps(board) + "\n"
				sock_cl.sendall(v.encode("utf-8"))

				turn = "○" if turn == "×" else "×"
				_ = recv_line(sock_cl)
		elif res in ("f","F","ｆ","Ｆ"):
			print("終了要求を受信")
			print("接続を終了します")
			break
		else:
			print(f"不明なコマンド: {res}")
finally:
	sock_cl.close()
	sock_sv.close()
	print("サーバーを終了しました")