# network-tic-tac-toe
Pythonのsocketを使った三目並べ(oxゲーム)です。  
サーバーとクライアントがTCP通信で対戦します。  
AIは勝利手、妨害手、中央優先などのロジックを実装しています。  
server.pyがサーバー,client.pyがクライアントのプログラムファイルです。  
PowerShellで実行することを前提に作成しています。  
## 実行方法  
PowerShellを2つ立ち上げる。  
2つともプログラムのあるファイルに移動する。  
それぞれで以下を実行する。  
### サーバー  
python server.py  
### クライアント  
python client.py  
