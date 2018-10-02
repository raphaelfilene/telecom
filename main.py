# -*- coding: utf-8 -*-

# para instalar as bibliotecas relativas ao reconhecimento de voz:
# sudo apt-get install python-pyaudio
# sudo pip install SpeechRecognition pyaudio

from pygame import*
from pygame.locals import*
import os,sys,random
import speech_recognition as sr #importamos o modúlo

init() #este init é do pygame e serve para iniciar o display e suas fontes

#agora, vou colocar a função "time" da biblioteca pygame dentro da variável "pytime", pois chamarei um outro "time" porém agora da biblioteca padrão do python
pytime=time

from time import time

class Janela:
	u'''Esta classe trabalhará as propriedades básicas da janela do jogo'''
	#ícone do jogo
	icone=image.load('imagens/icone.png')
	
	#título da janela
	nome='Jogo da Dama com Processamento de Voz'
	
	#tamanho da tela (largura x altura)
	dimensao=[800,600]
	
	#centro da tela
	centro=[i/2 for i in dimensao]
	
	#é tela fullscreen? True or False?
	fullscreen=False
	
	def __init__(self):
		#add nome à janela do jogo
		display.set_caption(self.nome)
		
		#add ícone à janela do jogo
		display.set_icon(self.icone)
		
		#criando o objeto 'tela' (é sobre tal objeto que colocarei todo o jogo)
		self.tela=display.set_mode((self.dimensao),[RESIZABLE,FULLSCREEN][self.fullscreen])
		
	def set_fullscreen(self):
		u'''Com esta função será possível trocar a tela de fullscreen pra modo janela e vice-versa'''
		if self.fullscreen:
			self.fullscreen=False
			self.tela=display.set_mode((self.dimensao),RESIZABLE)
		else:
			self.fullscreen=True
			self.tela=display.set_mode((self.dimensao),FULLSCREEN)
		

class Jogo:
	u'''Esta classe trabalhará nas propriedades gerais e básicas do jogo'''
	#é a variável que manterá o looping do jogo
	run=True
	
	#é o contador de tempo do jogo. Se o jogo tem, por exemplo, fps=60, então em cada segundo passarão 60 quadros e em cada quadro este "tempo" será acrescido em 60 e, em 3 segundos terei tempo=180 por exemplo.
	tempo=0
	
	#quantidade de quadros por segundo (tem um certo limite dado de pc para pc, de acordo tbm com os monitores...)
	fps=60
	
	def __init__(self,time_do_pygame):
		self.time=time_do_pygame
		
	def quit(self):
		u'''Sai do jogo'''
		self.run=False

class Teclas:
	u'''Nesta classe eu coloco as atividades básicas que os botões do teclado/mouse realizarão'''
	clicadas=[]
	pressionadas=[]
	
	def resetando_clicadas(self):
		u'''Limpa a lista de teclas clicadas'''
		self.clicadas=[]
	
	def situacao_teclas(self,evento):
		u'''Atualiza as variáveis "clicadas" e "pressionadas" com a lista de botões clicados/pressionados'''
		if evento.type==KEYDOWN:#se algum botao do teclado foi clicado
			self.clicadas.append(evento.key)
			self.pressionadas.append(evento.key)
		elif evento.type==KEYUP: #se soltei algum botao do teclado
			if evento.key in self.pressionadas:
				self.pressionadas.remove(evento.key)
		elif evento.type==MOUSEBUTTONDOWN: #se algum botao do mouse foi clicado
			self.clicadas.append(evento.button)
			self.pressionadas.append(evento.button)
		elif evento.type==MOUSEBUTTONUP: #se soltei algum botao do mouse
			if evento.button in self.pressionadas:
				self.pressionadas.remove(evento.button)

class Tabuleiro:
	margens=[0.23,0.15,0.02,0.15] #esquerda, cima, direita, baixo
	casas=[image.load('imagens/piso1.jpg'),image.load('imagens/piso2.jpg')]
	jogador_da_vez=1
	
	def __init__(self,qtd_casas,dimensao_tela):
		self.qtd_casas=qtd_casas

		#criando as listas com as posições das peças
		self.configuracao=[[0]*qtd_casas[0] for i in xrange(qtd_casas[1])] #0=vazia, 1='player 1', 2='player 2'
		self.configuracao[0]=[2]*qtd_casas[0]
		self.configuracao[1]=[2]*qtd_casas[0]
		self.configuracao[2]=[2]*qtd_casas[0]
		self.configuracao[3]=[2]*qtd_casas[0]
		self.configuracao[-1]=[1]*qtd_casas[0]
		self.configuracao[-2]=[1]*qtd_casas[0]
		self.configuracao[-3]=[1]*qtd_casas[0]
		self.configuracao[-4]=[1]*qtd_casas[0]

		for i in range(qtd_casas[0]):
			for j in range(qtd_casas[1]):
				if i % 2 == 0 and j % 2 == 0:
					self.configuracao[i][j]= 0
				if i % 2 != 0 and j % 2 != 0:
					self.configuracao[i][j]= 0


		#determinando as dimensões do tabuleiro
		self.dimensao=[
				int(dimensao_tela[0]*(1-self.margens[0]-self.margens[2])),
				int(dimensao_tela[1]*(1-self.margens[1]-self.margens[3]))
			]
		
		#achando as dimensões de cada 'casa' do tabuleiro
		self.dimensoes_casas=[a/b for a,b in zip(self.dimensao,qtd_casas)]

		#convertendo as imagens das casas para tornar sua manipulação mais rápida e com o tamanho desejado
		for i in xrange(2): self.casas[i]=transform.scale(self.casas[i].convert(),self.dimensoes_casas)

		#criando uma superfície onde sobreporei o tabuleiro
		self.imagem=Surface(self.dimensao)

		#desenhando as casas no tabuleiro
		for x in xrange(qtd_casas[0]):
			for y in xrange(qtd_casas[1]):
				self.imagem.blit(self.casas[(x+y)%2],[x*self.dimensoes_casas[0],y*self.dimensoes_casas[1]])

		#posição do tabuleiro na tela
		self.posicao=[int(a*b) for a,b in zip(dimensao_tela,self.margens)]

		#criando superfície que sobreporá as casas em que o mouse estiver sobreposto
		self.casa_mouseover=Surface(self.dimensoes_casas)
		self.casa_mouseover.fill((0,255,0))

		#criando superfície que sobreporá as casas para as quais a peça selecionada poderá se locomover
		self.casa_possivel=Surface(self.dimensoes_casas)
		self.casa_possivel.fill((0,255,255))

		#criando superfície de uma casa que receber o click do mouse
		self.casa_click=Surface(self.dimensoes_casas)
		self.casa_click.fill((0,0,255))
		self.peca_clicada=None

		#corrigindo o valor da dimensão (pois como há divisão esse valor precisa ser corrigido)
		self.dimensao=[self.qtd_casas[i]*self.dimensoes_casas[i] for i in [0,1]]

		#lista de comandos
		self.comandos=[]
		for i in ['a','b','c','d','e','f','g','h','i','j']:
			for j in ['um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito','nove','dez']:
				self.comandos.append(i+' '+j)
			for j in ['1', '2', '3', '4', '5', '6', '7', '8','9','10']:
				self.comandos.append(i+j)		

	def analisar_clicks(self,screen,mouse,houve_click,comando):
		comando=comando.lower()
		comando_valido=comando!='' and comando in self.comandos
		hop = False

		#verificando se o mouse está em cima de alguma das casas
		click_sobre_tabuleiro=False
		if comando_valido or (self.posicao[0]+self.dimensao[0]>mouse[0]>self.posicao[0] and self.posicao[1]+self.dimensao[1]>mouse[1]>self.posicao[1]):
			click_sobre_tabuleiro=True

			if comando_valido:
				try:
					for i in [[u'1',u'um'],[u'2',u'dois'],[u'3',u'três'],[u'4',u'quatro'],[u'5','cinco'],[u'6','seis'],[u'7',u'sete'],[u'8',u'oito'],[u'9',u'nove'],[u'10',u'dez']]:
						if i[0] in comando or i[1] in comando:
							x_over=int(i[0])-1
							if i[0] in comando:
								comando=comando.replace(i[0],'')
							else:
								comando=comando.replace(i[1],'')
							for j,v in enumerate([u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j']):
								if v in comando:
									y_over=j
									break
							break
					houve_click=True
				except:
					x_over,y_over=0,0
					houve_click=False

			else:
				#capturando os índices da casa sobre o qual o mouse está em cima
				x_over=(mouse[0]-self.posicao[0])/self.dimensoes_casas[0]
				y_over=(mouse[1]-self.posicao[1])/self.dimensoes_casas[1]
			
			#variável que dirá se a casa do mouseover é a mesma casa que foi clicada pelo mouse por último
			esta_sobre_casa_ja_clicada=True if self.peca_clicada and self.peca_clicada[0]==x_over and self.peca_clicada[1]==y_over else False
			
			#atualizando os índices da casa clicada
			if houve_click and self.configuracao[y_over][x_over]==self.jogador_da_vez:
				self.peca_clicada=None if esta_sobre_casa_ja_clicada else [x_over,y_over]
			
			#fazendo aparecer o efeito de uma casa cujo mouse está sobreposto a ela
			if not esta_sobre_casa_ja_clicada:
				screen.tela.blit(self.casa_mouseover,[self.posicao[0]+x_over*self.dimensoes_casas[0],self.posicao[1]+y_over*self.dimensoes_casas[1]])

		#fazendo aparecer o efeito de uma casa cujo mouse havia clicado por último
		if self.peca_clicada:
			hop = False
			x_click,y_click=self.peca_clicada
			screen.tela.blit(self.casa_click,[self.posicao[0]+x_click*self.dimensoes_casas[0],self.posicao[1]+y_click*self.dimensoes_casas[1]])

			if self.configuracao[y_click][x_click]==self.jogador_da_vez:
				if x_click==0:
					xs=[1]
				elif x_click==len(self.configuracao[0])-1:
					xs=[len(self.configuracao[0])-2]
				else:
					xs=[x_click-1,x_click+1]

				if y_click==0:
					ys=[1]
				elif y_click==len(self.configuracao)-1:
					ys=[len(self.configuracao)-2]
				else:
					ys=[y_click-1,y_click+1]

				casas=[]
				for x in xs:
					for y in ys:
						if self.configuracao[y][x]==0:
							casas.append([x,y])

						if self.jogador_da_vez == 1:
							if self.configuracao[y][x]==2:
								if self.configuracao[y-1][x+1 if x > x_click else x-1] == 0:
									hop = True
									casas.append([x+1 if x > x_click else x-1,y-1])

						if self.jogador_da_vez == 2:
							if self.configuracao[y][x] == 1:
								if self.configuracao[y+1][x+1 if x > x_click else x-1] == 0:
									hop = True
									casas.append([x+1 if x > x_click else x-1,y+1])

				for c in casas:
					screen.tela.blit(self.casa_possivel,[self.posicao[0]+c[0]*self.dimensoes_casas[0],self.posicao[1]+c[1]*self.dimensoes_casas[1]])

				#movendo peça:
				if houve_click and click_sobre_tabuleiro:
					for c in casas:
						if c[0]==x_over and c[1]==y_over:
							self.configuracao[y_click][x_click]=0
							self.configuracao[y_over][x_over]=self.jogador_da_vez

							if hop == True:

								if self.jogador_da_vez == 1:
									
									if x_over > x_click:
										self.configuracao[y_over+1][x_over-1] = 0
									else:
										self.configuracao[y_over+1][x_over+1] = 0

								if self.jogador_da_vez == 2:
									if x_over > x_click:
										self.configuracao[y_over-1][x_over-1] = 0
									else:
										self.configuracao[y_over-1][x_over+1] = 0

							self.jogador_da_vez=3-self.jogador_da_vez
							self.peca_clicada=None
							break


	def desenhar_pecas(self,screen,peca1,peca2):
		for y in xrange(self.qtd_casas[1]):
			for x in xrange(self.qtd_casas[0]):
				peca=[None,peca1,peca2][self.configuracao[y][x]]
				if peca:
					x_p,y_p=self.posicao[0],self.posicao[1]
					x_p+=(x+0.5)*self.dimensoes_casas[0]-0.5*peca.get_width()
					y_p+=(y+0.5)*self.dimensoes_casas[1]-0.5*peca.get_height()
					screen.tela.blit(peca,[int(x_p),int(y_p)])

class Avatar:
	dimensao_percentual=0.18
	nomes=['Chewbacca','Yoda','Darth Vader','Han Solo']
	tamanho_fonte=24
	fonte='arial'
	negrito=1
	italico=0
	cores=[(255,255,0),(0,255,0),(255,0,0),(0,0,255)] #cores para os avatares
	posicao_percentual_tela=[0.01,0.1]
	def __init__(self,numero_avatar,dimensao_tela,player):
		#dimensão do avatar
		self.dimensao=[int(self.dimensao_percentual*dimensao_tela[0]),int(self.dimensao_percentual*dimensao_tela[1])]

		#capturando e convertendo a imagem para um formato mais rápido e com as dimensões desejadas sem distorcê-la
		avatar=image.load('imagens/char%s.jpg'%numero_avatar).convert()
		xo,yo=avatar.get_size() #dimensões originais
		x,y=self.dimensao #dimensões desejadas
		if float(xo)/x>float(yo)/y:
			L=int(y*xo/float(yo))
			avatar=transform.scale(avatar,[L,y])
			avatar=avatar.subsurface([(L-x)/2,0,x,y])
		else:
			H=int(x*yo/float(xo))
			avatar=transform.scale(avatar,[x,H])
			avatar=avatar.subsurface([0,(H-y)/2,x,y])

		#criando a legenda com o nome
		legenda=font.SysFont(self.fonte,self.tamanho_fonte,self.negrito,self.italico).render(self.nomes[numero_avatar-1],1,self.cores[numero_avatar-1])

		#superfície com o avatar e a legenda
		self.imagem=Surface((x,y+legenda.get_height()))
		posicao_legenda_x=(x-legenda.get_width())/2 #é uma posição relativa à superfície que contém a legenda e o avatar

		if player==1:
			self.imagem.blit(avatar,(0,0))
			self.imagem.blit(legenda,(posicao_legenda_x,y))
		else:
			self.imagem.blit(legenda,(posicao_legenda_x,0))
			self.imagem.blit(avatar,(0,legenda.get_height()))

		#posição relativa a tela
		l,h=[int(a*b) for a,b in zip(self.posicao_percentual_tela,dimensao_tela)]
		if player==1:
			self.posicao=(l,h)
		else:
			self.posicao=(l,dimensao_tela[1]-h-self.imagem.get_height())

class Peca: #Peça
	dimensao_percentual=0.9
	def __init__(self,numero_peca,dimensao_casa,player):
		#dimensão de cada peça
		self.dimensao=[int(self.dimensao_percentual*dimensao_casa[0]),int(self.dimensao_percentual*dimensao_casa[1])]

		#capturando e convertendo a imagem para um formato mais rápido e com as dimensões desejadas sem distorcê-la
		peca=image.load('imagens/helm%s.png'%numero_peca).convert_alpha()

		xo,yo=peca.get_size() #dimensões originais
		x,y=self.dimensao #dimensões desejadas

		if float(xo)/x>float(yo)/y:
			L=int(y*xo/float(yo))
			peca=transform.scale(peca,[L,y])
		else:
			H=int(x*yo/float(xo))
			peca=transform.scale(peca,[x,H])

		self.imagem=peca

screen=Janela()
jogo=Jogo(pytime)

tab=Tabuleiro([10,10],screen.dimensao)

chars=range(1,len(Avatar.nomes)+1)
char1=random.choice(chars)
chars.remove(char1)
char2=random.choice(chars)

avatar1=Avatar(char1,screen.dimensao,player=1)
avatar2=Avatar(char2,screen.dimensao,player=2)

pecas=range(1,5)
peca1=random.choice(pecas)
pecas.remove(peca1)
peca2=random.choice(pecas)

peca1=Peca(peca1,tab.dimensoes_casas,player=1)
peca2=Peca(peca2,tab.dimensoes_casas,player=2)

teclas=Teclas()

rec = sr.Recognizer() #instanciamos o modúlo do reconhecedor

def comando_de_voz():
	#aplicando o reconhecedor de voz
	try:
		with sr.Microphone() as fala: #chamos a gravação do microphone de fala
			rec.adjust_for_ambient_noise(fala)
			frase = rec.listen(fala) #o metodo listen vai ouvir o que a gente falar e gravar na variavel frase
			comando=rec.recognize_google(frase, language='pt') #transformando nossa fala em texto
			comando = comando.lower().replace(" ","")
	except:
		comando=u'Fala não reconhecida'
	return comando

def rotinas():
	u'''Agrupei nesta função as atividades que precisam ser "rodadas" ao final de cada quadro'''
	#atualizando o tempo
	jogo.tempo+=1
	
	#atualizando a tela
	display.update()
	
	#"limpando"(na verdade eu estou pintando ela de rgb=(0,0,0)=preto) a tela --- essa limpeza só será visualizada na próxima vez que a tela for atualizada
	screen.tela.fill((0,0,0))
	
	#fazendo o jogo rodar com a qtd de quadros por segundos estabelecida
	#jogo.time.Clock().tick(jogo.fps) #neste software em particular eu não vou utilizar isso

	
def jogar():
	while jogo.run:
		#apagando o registro de teclas clicadas no quadro anterior
		teclas.resetando_clicadas()
		
		#analisando os eventos que ocorreram no quadro atual
		for evento in event.get():
			if evento.type==QUIT:
				jogo.quit()
			else:
				#atualizando a situação das teclas clicadas/pressionadas
				teclas.situacao_teclas(evento)

		if jogo.tempo>0:
			comando=comando_de_voz()
		else:
			comando=''

		print comando

		#desenhando o tabuleiro
		screen.tela.blit(tab.imagem,tab.posicao)

		#analisar clicks
		tab.analisar_clicks(screen,mouse.get_pos(),1 in teclas.clicadas,comando)
		
		#desenhando as peças
		tab.desenhar_pecas(screen,peca1.imagem,peca2.imagem)

		#posicionando os avatares
		screen.tela.blit(avatar1.imagem,avatar1.posicao)
		screen.tela.blit(avatar2.imagem,avatar2.posicao)
		
		#rotinas que preciso rodar toda vez que um quadro terminar
		rotinas()

jogar()

#fechar a janela do pygame
quit()

#fechar a aplicação python
sys.exit()