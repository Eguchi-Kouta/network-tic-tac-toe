import socket
import json
import sys

def recv_line(sock: socket.socket) -> str:
	buf = b""
	while b"\n" not in buf:
		chunk = sock.recv(1024)
		if not chunk:
			raise ConnectionError("サーバーが切断しました")
		buf += chunk
	line, _, _ = buf.partition(b"\n")
	return line.decode("utf-8")
def print_board(board):
	for row in board:
		print(row)
def main():
	IPADDR = input("サーバー側のlocal_ipを入力してください: ")
	PORT = input("サーバー側のPORTを入力してください: ")
	if not PORT.isdigit():
		print("ポート番号が数値ではありません")
		return 
	PORT = int(PORT)
	
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((IPADDR, PORT))
	except Exception as e:
		print("接続できませんでした:",e)
		sys.exit()
	print("サーバーとの接続に成功しました")
	
	try:
		while True:
			print("始めるなら's',終わるなら'f'を入力してください")
			c = input(">>> ").strip()
			sock.sendall((c + "\n").encode("utf-8"))
			
			if c in ("s","S","ｓ","Ｓ"):
				game = "start"
				print("sが入力されました")
				print("game start")
				print("○(先行)か×(後攻)かが選ばれます")
				you = recv_line(sock)
				print(f"あなたの記号: {you}")
				
				board_json = recv_line(sock)
				board = json.loads(board_json)
				print("初期ボード:")
				print_board(board)
				
				sock.sendall(b"ok\n")

				turn = "○"
				
				while game == "start":
					status = recv_line(sock)
					if status != "e":
						if status == "draw":
							print("結果: 引き分け")
						else:
							print(f"結果: {status}の勝ち")
						game = "finish"
						break
					if turn == you:
						print("your turn")
						while True:
							move = input("座標をa,bの形式(0 <= a,b < 3)で入力してください >>> ").strip()
							sock.sendall((move + "\n").encode("utf-8"))
							resp = recv_line(sock)
							if resp.startswith("ERR:"):
								print(resp[4:])
							else:
								board = json.loads(resp)
								print("現在のボード:")
								print_board(board)
								break
					else:
						print("AI の手を待っています...")
						board_json = recv_line(sock)
						board = json.loads(board_json)
						print("現在のボード:")
						print_board(board)
					
					turn = "○" if turn == "×" else "×"
					sock.sendall(("reset\n").encode("utf-8"))
			elif c in ("f","F","ｆ","Ｆ"):
				print("fが入力されました")
				print("ゲームを終了します\nお疲れさまでした")
				break
			else:
				print("不明な入力です")
	except ConnectionError as e:
		print("接続エラー:",e)
	finally:
		sock.close()
		print("接続を閉じました")

if __name__ == "__main__":
	main()
