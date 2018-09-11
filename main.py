# -*- coding: utf-8 -*-

from pygame import*
from pygame.locals import*
import os,sys

init() #este init é do pygame e serve para iniciar o display e suas fontes

#agora, vou colocar a função "time" da biblioteca pygame dentro da variável "pytime", pois chamarei um outro "time" porém agora da biblioteca padrão do python
pytime=time

from time import time

class Janela:
	u'''Esta classe trabalhará as propriedades básicas da janela do jogo'''
	#ícone do jogo
	icone=image.load('imagens/icone.jpg')
	
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
	def __init__(self,qtd_casas,dimensao_tela):
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

class Avatar:
	dimensao_percentual=0.18
	nomes=['Kim','Trump']
	tamanho_fonte=24
	fonte='arial'
	negrito=1
	italico=0
	cores=[(255,0,0),(0,0,255)] #cores para os avatares
	posicao_percentual_tela=[0.01,0.1]
	def __init__(self,numero_avatar,dimensao_tela,player):
		#dimensão do avatar
		self.dimensao=[int(self.dimensao_percentual*dimensao_tela[0]),int(self.dimensao_percentual*dimensao_tela[1])]

		#capturando e convertendo a imagem para um formato mais rápido e com as dimensões desejadas sem distorcê-la
		avatar=image.load('imagens/lider%s.jpg'%numero_avatar).convert()
		xo,yo=avatar.get_size() #dimensões originais
		x,y=self.dimensao #dimensões desejadas
		if xo>yo:
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
	dimensao_percentual=0.8
	def __init__(self,numero_peca,dimensao_casa,player):
		#dimensão de cada peça
		self.dimensao=[int(self.dimensao_percentual*dimensao_casa[0]),int(self.dimensao_percentual*dimensao_casa[1])]

		#capturando e convertendo a imagem para um formato mais rápido e com as dimensões desejadas sem distorcê-la
		peca=image.load('imagens/soldado%s.jpg'%numero_peca).convert()

		xo,yo=peca.get_size() #dimensões originais
		x,y=self.dimensao #dimensões desejadas

		print xo,yo,x,y
		if xo>yo:
			L=int(y*xo/float(yo))
			print L
			print [(L-x)/2,0,x,y]
			peca=transform.scale(peca,[L,y])
			peca=peca.subsurface([(L-x)/2,0,x,y])
		else:
			H=int(x*yo/float(xo))
			peca=transform.scale(peca,[x,H])
			peca=peca.subsurface([0,(H-y)/2,x,y])

screen=Janela()
jogo=Jogo(pytime)

tab=Tabuleiro([8,8],screen.dimensao)
avatar1=Avatar(1,screen.dimensao,player=1)
avatar2=Avatar(2,screen.dimensao,player=2)

#peca1=Peca(1,tab.dimensoes_casas,player=1)
#peca2=Peca(2,tab.dimensoes_casas,player=2)

teclas=Teclas()

def rotinas():
	u'''Agrupei nesta função as atividades que precisam ser "rodadas" ao final de cada quadro'''
	#atualizando o tempo
	jogo.tempo+=1
	
	#atualizando a tela
	display.update()
	
	#"limpando"(na verdade eu estou pintando ela de rgb=(0,0,0)=preto) a tela --- essa limpeza só será visualizada na próxima vez que a tela for atualizada
	screen.tela.fill((0,0,0))
	
	#fazendo o jogo rodar com a qtd de quadros por segundos estabelecida
	jogo.time.Clock().tick(jogo.fps)

u'''
def mover_boneco():
	#caso seja pressionado o botão 'w' ou  a 'seta para cima'
	if K_w in teclas.pressionadas or K_UP in teclas.pressionadas:
		boneco.posicao[1]+=-boneco.passo;
	
	#caso seja pressionado o botão 's' ou  a 'seta para baixo'
	if K_s in teclas.pressionadas or K_DOWN in teclas.pressionadas:
		boneco.posicao[1]+=+boneco.passo;
	
	#caso seja pressionado o botão 'a' ou  a 'seta para a esquerda'
	if K_a in teclas.pressionadas or K_LEFT in teclas.pressionadas:
		boneco.posicao[0]+=-boneco.passo;
	
	#caso seja pressionado o botão 'd' ou  a 'seta para a direita'
	if K_d in teclas.pressionadas or K_RIGHT in teclas.pressionadas:
		boneco.posicao[0]+=boneco.passo;'''
		
	
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

		#colocando o tabuleiro
		screen.tela.blit(tab.imagem,tab.posicao)

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