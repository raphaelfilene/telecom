# -*- coding: utf-8 -*-

# para instalar as bibliotecas relativas ao reconhecimento de voz:
# sudo apt-get install python-pyaudio
# sudo pip install SpeechRecognition pyaudio

from pygame import *
from pygame.locals import *
import os,sys,random
import speech_recognition as sr #importamos o modúlo
import numpy as np

init() #este init é do pygame e serve para iniciar o display e suas fontes

#agora, vou colocar a função "time" da biblioteca pygame dentro da variável "pytime", pois chamarei um outro "time" porém agora da biblioteca padrão do python
pytime=time

from time import time,sleep

class Janela:
	u'''Esta classe trabalhará as propriedades básicas da janela do jogo'''
	#ícone do jogo
	icone=image.load('imagens/icone.png')
	
	#título da janela
	nome='Jogo de Damas com Processamento de Voz'
	
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

		#desenhando o fundo
		fundo=image.load('imagens/fundo.jpg').convert()
		tam_fundo=fundo.get_size()
		tam_fundo=[self.dimensao[0],(tam_fundo[1]*self.dimensao[0])/tam_fundo[0]]
		self.fundo=transform.scale(fundo,tam_fundo)
		self.posicao_fundo=0
		
	def set_fullscreen(self):
		u'''Com esta função será possível trocar a tela de fullscreen pra modo janela e vice-versa'''
		if self.fullscreen:
			self.fullscreen=False
			self.tela=display.set_mode((self.dimensao),RESIZABLE)
		else:
			self.fullscreen=True
			self.tela=display.set_mode((self.dimensao),FULLSCREEN)	

	def desenhar_fundo(self):
		self.posicao_fundo=(self.posicao_fundo+3)%self.fundo.get_height()
		sobra=self.fundo.get_height()-self.posicao_fundo
		self.tela.blit(self.fundo,[0,-self.posicao_fundo])

		if sobra<self.dimensao[1]:
			self.tela.blit(self.fundo,[0,sobra])

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

class Tabuleiro:
	margens=[0.23,0.15,0.02,0.15] #esquerda, cima, direita, baixo
	casas=[image.load('imagens/piso1.jpg'),image.load('imagens/piso2.jpg')]
	jogador_da_vez=1
	tamanho_fonte=24
	fonte='arial'
	cor_fonte=(255,255,255)
	negrito=1
	italico=0
	jogo_escolhido = 0
	
	def __init__(self,qtd_casas,dimensao_tela,jogo):

		self.jogo_escolhido = jogo

		if self.jogo_escolhido == 2:
			qtd_casas = [8,8]

		self.qtd_casas=qtd_casas

		#jogo 1 = damas
		if self.jogo_escolhido == 1:
			#criando as listas com as posições das peças (monta o tabuleiro de damas)
			self.configuracao=[[0]*qtd_casas[0] for i in xrange(qtd_casas[1])] #0=vazia, 1='player 1', -1='player 2'
			for i in xrange(4):
				self.configuracao[i]=[-1]*qtd_casas[0]
				self.configuracao[-i-1]=[1]*qtd_casas[0]

			for i in range(qtd_casas[0]):
				for j in range(qtd_casas[1]):
					if i % 2 == 0 and j % 2 == 0:
						self.configuracao[i][j]= 0
					if i % 2 != 0 and j % 2 != 0:
						self.configuracao[i][j]= 0

		#jogo 2 = xadrez
		if self.jogo_escolhido == 2:
			#criando as listas com as posições das peças (monta o tabuleiro de xadrez)
			self.configuracao=[[0]*qtd_casas[0] for i in xrange(qtd_casas[1])] #0=vazia #3=peão #4=torre #5=cavalo #6=bispo #7=rainha #8=rei

			#posicionando os peões
			for i in xrange(8):
				self.configuracao[1][i] = 4
				self.configuracao[6][i] = 3

			#posicionando as torres
			self.configuracao[0][0] = 6
			self.configuracao[0][7] = 6
			self.configuracao[7][0] = 5
			self.configuracao[7][7] = 5

			#posicionando os cavalos
			self.configuracao[0][1] = 8
			self.configuracao[0][6] = 8
			self.configuracao[7][1] = 7
			self.configuracao[7][6] = 7

			#posicionando os bispos
			self.configuracao[0][2] = 10
			self.configuracao[0][5] = 10
			self.configuracao[7][2] = 9
			self.configuracao[7][5] = 9

			#posicionando as rainhas
			self.configuracao[0][3] = 12
			self.configuracao[7][3] = 11

			#posicionando os reis
			self.configuracao[0][4] = 14
			self.configuracao[7][4] = 13

		#determinando as dimensões do tabuleiro
		self.dimensao=[
				int((dimensao_tela[0]+1)*(1-self.margens[0]-self.margens[2])),
				int((dimensao_tela[1]+1)*(1-self.margens[1]-self.margens[3]))
			]
		
		#achando as dimensões de cada 'casa' do tabuleiro
		self.dimensoes_casas=[a/(b+1) for a,b in zip(self.dimensao,qtd_casas)]

		#convertendo as imagens das casas para tornar sua manipulação mais rápida e com o tamanho desejado
		for i in xrange(2): self.casas[i]=transform.scale(self.casas[i].convert(),self.dimensoes_casas)

		#criando uma superfície onde sobreporei o tabuleiro
		self.imagem=Surface(self.dimensao)
		self.imagem.set_colorkey(0)

		#desenhando as casas no tabuleiro
		for x in xrange(1,qtd_casas[0]+1):
			for y in xrange(1,qtd_casas[1]+1):
				self.imagem.blit(self.casas[(x+y)%2],[x*self.dimensoes_casas[0],y*self.dimensoes_casas[1]])

		#desenhando as letras e números para as coordenadas
		dx=self.dimensoes_casas[0]/2
		dy=self.dimensoes_casas[1]/2
		lateral=['A','B','C','D','E','F','G','H','I','J']
		vertical=[str(i) for i in xrange(1,11)]
		lateral_img=[font.SysFont(self.fonte,self.tamanho_fonte,self.negrito,self.italico).render(i,1,self.cor_fonte) for i in lateral]
		vertical_img=[font.SysFont(self.fonte,self.tamanho_fonte,self.negrito,self.italico).render(i,1,self.cor_fonte) for i in vertical]

		for i,v in enumerate(lateral_img):
			self.imagem.blit(v,[(i+1)*self.dimensoes_casas[0]+dx-v.get_width()/2,dy-v.get_height()/2])
		for i,v in enumerate(vertical_img):
			self.imagem.blit(v,[dx-v.get_width()/2,(i+1)*self.dimensoes_casas[1]+dy-v.get_height()/2])

		#posição do tabuleiro na tela
		self.posicao=[int(a*b) for a,b in zip(dimensao_tela,self.margens)]

		#criando superfície para a casa selecionada
		self.casa_selecionada=Surface(self.dimensoes_casas)

		self.casa_selecionada.fill((255,0,255))

		#criando superfície que sobreporá as casas para as quais a peça selecionada poderá se locomover
		self.casa_possivel=Surface(self.dimensoes_casas)
		self.casa_possivel.fill((0,255,255))

		#corrigindo o valor da dimensão (pois como há divisão esse valor precisa ser corrigido)
		self.dimensao=[self.qtd_casas[i]*self.dimensoes_casas[i] for i in [0,1]]

		#lista de comandos
		self.comandos=[]
		for i in ['a','b','c','d','e','f','g','h','i','j']:
			for j in ['um', 'dois', 'tres', 'quatro', 'cinco', 'seis', 'sete', 'oito','nove','dez']:
				self.comandos.append(i+' '+j)
			for j in ['1', '2', '3', '4', '5', '6', '7', '8','9','10']:
				self.comandos.append(i+j)		

		self.local_casa_selecionada=None
		self.locais_casas_possiveis=[]

		self.wcheck=False
		self.bcheck=False

		self.rei_branco = []
		self.rei_preto = []

	def desenhar_pecas(self,screen,peca1,peca2,peca3,peca4,peca5=None,peca6=None,peca7=None,peca8=None,peca9=None,peca10=None,peca11=None,peca12=None):
		#desenhando as casas no tabuleiro
		for x in xrange(1,self.qtd_casas[0]+1):
			for y in xrange(1,self.qtd_casas[1]+1):
				self.imagem.blit(self.casas[(x+y)%2],[x*self.dimensoes_casas[0],y*self.dimensoes_casas[1]])

		#desenhando a casa selecionada
		if self.local_casa_selecionada:
			x,y=self.local_casa_selecionada
			self.imagem.blit(self.casa_selecionada,[(x+1)*self.dimensoes_casas[0],(y+1)*self.dimensoes_casas[1]])

		#desenhando as casas que poderão ser alvos de escolha da peça selecionada
		for local in self.locais_casas_possiveis:
			x,y=local
			self.imagem.blit(self.casa_possivel,[(x+1)*self.dimensoes_casas[0],(y+1)*self.dimensoes_casas[1]])		

		#desenhando as peças
		for y in xrange(self.qtd_casas[1]):
			for x in xrange(self.qtd_casas[0]):
				if peca5 == None:
					peca=[None,peca1,peca2,peca3,peca4][self.configuracao[y][x]]
					if peca:
						x_p,y_p=self.posicao[0],self.posicao[1]
						x_p+=(x+1.5)*self.dimensoes_casas[0]-0.5*peca.get_width()
						y_p+=(y+1.5)*self.dimensoes_casas[1]-0.5*peca.get_height()
						screen.tela.blit(peca,[int(x_p),int(y_p)])
				else:
					peca=[peca1,peca2,peca3,peca4,peca5,peca6,peca7,peca8,peca9,peca10,peca11,peca12,None,None,None,None][self.configuracao[y][x]-3]
					if peca:
						x_p,y_p=self.posicao[0],self.posicao[1]
						x_p+=(x+1.5)*self.dimensoes_casas[0]-0.5*peca.get_width()
						y_p+=(y+1.5)*self.dimensoes_casas[1]-0.5*peca.get_height()
						screen.tela.blit(peca,[int(x_p),int(y_p)])

	def analisar_comando(self,comando):

		if comando in self.comandos:
			if comando in tab.comandos:
				for i in [[u'10',u'dez'],[u'1',u'um'],[u'2',u'dois'],[u'3',u'tres'],[u'4',u'quatro'],[u'5','cinco'],[u'6','seis'],[u'7',u'sete'],[u'8',u'oito'],[u'9',u'nove']]:
					if i[0] in comando or i[1] in comando:
						y_over=int(i[0])-1
						if i[0] in comando:
							comando=comando.replace(i[0],'')
						else:
							comando=comando.replace(i[1],'')
						for j,v in enumerate([u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j']):
							if v in comando:
								x_over=j
								break
						break

				if self.jogo_escolhido == 1:
					if x_over > 9:
						x_over = 9
					if y_over > 9:
						y_over = 9

				if self.jogo_escolhido == 2:
					if x_over > 7:
						x_over = 7
					if y_over > 7:
						y_over = 7

				self.local_casa_selecionada = [x_over,y_over]

				#lógica de damas
				if self.jogo_escolhido == 1:

					if [x_over,y_over] in self.locais_casas_possiveis:

						xo,yo=self.local_casa_atual
						self.configuracao[y_over][x_over] = self.configuracao[yo][xo]
						self.configuracao[yo][xo] = 0
						self.local_casa_atual = None

						#se tornar dama
						if y_over in [0,9]:
							self.configuracao[y_over][x_over] = 2*self.jogador_da_vez

						#se matar uma peca inimiga
						if y_over-yo not in [-1,1]:
							if x_over > xo:
								if y_over > yo:
									self.configuracao[y_over-1][x_over-1] = 0
								if y_over < yo:
									self.configuracao[y_over+1][x_over-1] = 0
							else:
								if y_over > yo:
									self.configuracao[y_over-1][x_over+1] = 0
								if y_over < yo:
									self.configuracao[y_over+1][x_over+1] = 0

						self.jogador_da_vez = -1*self.jogador_da_vez

					elif np.sign(self.configuracao[x_over][y_over]) == np.sign(self.jogador_da_vez):
						self.local_casa_selecionada = [x_over,y_over]
						self.local_casa_atual = [x_over,y_over]

					else:
						self.local_casa_atual = [x_over,y_over]

					self.set_casas_possiveis_prox_movimento()

					condicao_vitoria = 0

					for i in range(self.qtd_casas[0]):
						if all(x[i] >= 0 for x in self.configuracao):
							condicao_vitoria += 1

					if condicao_vitoria == self.qtd_casas[0]:
						print "Vitória do jogador 1"
					else:
						condicao_vitoria = 0

					for i in range(self.qtd_casas[0]):
						if all(x[i] <= 0 for x in self.configuracao):
							condicao_vitoria += 1

					if condicao_vitoria == self.qtd_casas[0]:
						print "Vitória do jogador 2"
					else:
						condicao_vitoria = 0

				#lógica de xadrez
				if self.jogo_escolhido == 2:

					if self.wcheck == False and self.bcheck == False:

						if [x_over,y_over] in self.locais_casas_possiveis:

							xo,yo=self.local_casa_atual
							self.configuracao[y_over][x_over] = self.configuracao[yo][xo]
							self.configuracao[yo][xo] = 0
							self.jogador_da_vez = -1*self.jogador_da_vez

						elif (self.configuracao[x_over][y_over]%2 == 1 and self.jogador_da_vez == 1) or (self.configuracao[x_over][y_over]%2 == 0 and self.jogador_da_vez == -1):
							self.local_casa_selecionada = [x_over,y_over]
							self.local_casa_atual = [x_over,y_over]

						else:
							self.local_casa_atual = [x_over,y_over]

						temp_local = self.local_casa_atual
						temp_selecionada = self.local_casa_selecionada

						#pega a localização atual dos dois reis
						for i in xrange(8):
							for j in xrange(8):
								if self.wcheck == False:
									if self.configuracao[j][i] == 13:
										self.local_casa_atual = [i,j]
										self.rei_branco = [i,j]

								if self.bcheck == False:
									if self.configuracao[j][i] == 14:
										self.local_casa_atual = [i,j]
										self.rei_preto = [i,j]
										
						a = self.jogador_da_vez

						#verifica se algum rei está em xeque
						for i in xrange(8):
							for j in xrange(8):
								if self.configuracao[j][i] %2 != 1 and self.configuracao[j][i] != 0 and self.configuracao[j][i] != 14:
									self.jogador_da_vez = -1
									self.local_casa_atual = [i,j]
									self.set_casas_possiveis_prox_movimento()
									if self.rei_branco in self.locais_casas_possiveis:
										self.wcheck = True
									self.jogador_da_vez = 1

								if self.configuracao[j][i] %2 != 0 and self.configuracao[j][i] != 13:
									self.jogador_da_vez = 1
									self.local_casa_atual = [i,j]
									self.set_casas_possiveis_prox_movimento()
									if self.rei_preto in self.locais_casas_possiveis:
										self.bcheck = True
									self.jogador_da_vez = -1

						self.jogador_da_vez = a
						self.local_casa_atual = temp_local

						self.set_casas_possiveis_prox_movimento()

					if self.wcheck == True:

						if [x_over,y_over] in self.locais_casas_possiveis:

							xo,yo=self.local_casa_atual
							self.configuracao[y_over][x_over] = self.configuracao[yo][xo]
							self.configuracao[yo][xo] = 0
							self.jogador_da_vez = -1*self.jogador_da_vez

						elif (self.configuracao[x_over][y_over]%2 == 1 and self.jogador_da_vez == 1) or (self.configuracao[x_over][y_over]%2 == 0 and self.jogador_da_vez == -1):
							self.local_casa_selecionada = [x_over,y_over]
							self.local_casa_atual = [x_over,y_over]

						else:
							self.local_casa_atual = [x_over,y_over]

						self.set_casas_possiveis_prox_movimento()

						temp_locais_casas_possiveis = self.locais_casas_possiveis + []
						temp_casa_atual = self.local_casa_atual + []

						for k in self.locais_casas_possiveis:
							for i in xrange(8):
								for j in xrange(8):
									if self.configuracao[j][i] %2 != 1 and self.configuracao[j][i] != 0 and self.configuracao[j][i] != 14:
										self.jogador_da_vez *= -1
										self.local_casa_atual = [i,j]

										temp = self.configuracao[k[1]][k[0]]

										k_temp = self.rei_branco + []

										if self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]] == 13:
											self.rei_branco = k

										self.configuracao[k[1]][k[0]] = self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]]
										self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]] = 0
										self.set_casas_possiveis_prox_movimento()

										if self.rei_branco in self.locais_casas_possiveis:
											try:
												temp_locais_casas_possiveis.remove(k)
											except:
												pass

										self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]] = self.configuracao[k[1]][k[0]]
										self.configuracao[k[1]][k[0]] = temp
										self.jogador_da_vez *= -1
										self.rei_branco = k_temp

						self.locais_casas_possiveis = temp_locais_casas_possiveis
						self.local_casa_atual = temp_casa_atual

						jogadas_possiveis = []

						for l in xrange(8):
							for m in xrange(8):
								self.local_casa_atual = [l,m]
								self.set_casas_possiveis_prox_movimento()

								temp_locais_casas_possiveis2 = self.locais_casas_possiveis + []
								temp_casa_atual2 = self.local_casa_atual + []

								for k in self.locais_casas_possiveis:
									for i in xrange(8):
										for j in xrange(8):
											if self.configuracao[j][i] %2 != 1 and self.configuracao[j][i] != 0 and self.configuracao[j][i] != 14:
												self.jogador_da_vez *= -1
												self.local_casa_atual = [i,j]

												temp = self.configuracao[k[1]][k[0]]

												k_temp = self.rei_branco + []

												if self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]] == 13:
													self.rei_branco = k

												self.configuracao[k[1]][k[0]] = self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]]
												self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]] = 0
												self.set_casas_possiveis_prox_movimento()

												if self.rei_branco in self.locais_casas_possiveis:
													try:
														temp_locais_casas_possiveis2.remove(k)
													except:
														pass

												self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]] = self.configuracao[k[1]][k[0]]
												self.configuracao[k[1]][k[0]] = temp
												self.jogador_da_vez *= -1
												self.rei_branco = k_temp

								self.locais_casas_possiveis = temp_locais_casas_possiveis2
								self.local_casa_atual = temp_casa_atual2

								jogadas_possiveis.append(self.locais_casas_possiveis)

						contador_xadrez = 0

						for jogada in jogadas_possiveis:
							if jogada != []:
								break
							else:
								contador_xadrez += 1

						if contador_xadrez == 64:
							self.jogador_da_vez = 0
							print "Xeque-mate; vitória do jogador 2"

						self.locais_casas_possiveis = temp_locais_casas_possiveis
						self.local_casa_atual = temp_casa_atual

					if self.bcheck == True:

						if [x_over,y_over] in self.locais_casas_possiveis:

							xo,yo=self.local_casa_atual
							self.configuracao[y_over][x_over] = self.configuracao[yo][xo]
							self.configuracao[yo][xo] = 0
							self.jogador_da_vez = -1*self.jogador_da_vez

						elif (self.configuracao[x_over][y_over]%2 == 1 and self.jogador_da_vez == 1) or (self.configuracao[x_over][y_over]%2 == 0 and self.jogador_da_vez == -1):
							self.local_casa_selecionada = [x_over,y_over]
							self.local_casa_atual = [x_over,y_over]

						else:
							self.local_casa_atual = [x_over,y_over]

						self.set_casas_possiveis_prox_movimento()

						temp_locais_casas_possiveis = self.locais_casas_possiveis + []
						temp_casa_atual = self.local_casa_atual + []

						for k in self.locais_casas_possiveis:
							for i in xrange(8):
								for j in xrange(8):
									if self.configuracao[j][i] %2 != 0 and self.configuracao[j][i] != 14:
										self.jogador_da_vez *= -1
										self.local_casa_atual = [i,j]

										temp = self.configuracao[k[1]][k[0]]

										k_temp = self.rei_preto + []

										if self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]] == 14:
											self.rei_preto = k

										self.configuracao[k[1]][k[0]] = self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]]
										self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]] = 0
										self.set_casas_possiveis_prox_movimento()

										if self.rei_preto in self.locais_casas_possiveis:
											try:
												temp_locais_casas_possiveis.remove(k)
											except:
												pass

										self.configuracao[temp_casa_atual[1]][temp_casa_atual[0]] = self.configuracao[k[1]][k[0]]
										self.configuracao[k[1]][k[0]] = temp
										self.jogador_da_vez *= -1
										self.rei_preto = k_temp

						self.locais_casas_possiveis = temp_locais_casas_possiveis
						self.local_casa_atual = temp_casa_atual

						jogadas_possiveis = []

						for l in xrange(8):
							for m in xrange(8):
								self.local_casa_atual = [l,m]
								self.set_casas_possiveis_prox_movimento()

								temp_locais_casas_possiveis2 = self.locais_casas_possiveis + []
								temp_casa_atual2 = self.local_casa_atual + []

								for k in self.locais_casas_possiveis:
									for i in xrange(8):
										for j in xrange(8):
											if self.configuracao[j][i] %2 != 0 and self.configuracao[j][i] != 14:
												self.jogador_da_vez *= -1
												self.local_casa_atual = [i,j]

												temp = self.configuracao[k[1]][k[0]]

												k_temp = self.rei_preto + []

												if self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]] == 14:
													self.rei_preto = k

												self.configuracao[k[1]][k[0]] = self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]]
												self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]] = 0
												self.set_casas_possiveis_prox_movimento()

												if self.rei_preto in self.locais_casas_possiveis:
													try:
														temp_locais_casas_possiveis2.remove(k)
													except:
														pass

												self.configuracao[temp_casa_atual2[1]][temp_casa_atual2[0]] = self.configuracao[k[1]][k[0]]
												self.configuracao[k[1]][k[0]] = temp
												self.jogador_da_vez *= -1
												self.rei_preto = k_temp

								self.locais_casas_possiveis = temp_locais_casas_possiveis2
								self.local_casa_atual = temp_casa_atual2

								jogadas_possiveis.append(self.locais_casas_possiveis)

						contador_xadrez = 0

						for jogada in jogadas_possiveis:
							if jogada != []:
								break
							else:
								contador_xadrez += 1

						if contador_xadrez == 64:
							self.jogador_da_vez = 0
							print "Xeque-mate; vitória do jogador 1"

						self.locais_casas_possiveis = temp_locais_casas_possiveis
						self.local_casa_atual = temp_casa_atual

					self.wcheck = False
					self.bcheck = False

	def set_casas_possiveis_prox_movimento(self):
		self.locais_casas_possiveis=[]
		if self.local_casa_atual:
			x,y=self.local_casa_atual

			#movimento de peça
			if np.sign(self.configuracao[y][x]) == np.sign(self.jogador_da_vez) and self.configuracao[y][x] in [-1,1]:
				posicoes_adjacentes=[]
				if x==0:
					if y==0:
						posicoes_adjacentes.append([x+1,y+1])
					elif y==self.qtd_casas[1]-1:
						posicoes_adjacentes.append([x+1,y-1])
					else:
						posicoes_adjacentes.extend([[x+1,y+1],[x+1,y-1]])

				elif x==self.qtd_casas[0]-1:
					if y==0:
						posicoes_adjacentes.append([x-1,y+1])
					elif y==self.qtd_casas[1]-1:
						posicoes_adjacentes.append([x-1,y-1])
					else:
						posicoes_adjacentes.extend([[x-1,y+1],[x-1,y-1]])
				else:
					if y==0:
						posicoes_adjacentes.extend([[x-1,y+1],[x+1,y+1]])
					elif y==self.qtd_casas[1]-1:
						posicoes_adjacentes.extend([[x-1,y-1],[x+1,y-1]])
					else:
						posicoes_adjacentes.extend([[x-1,y-1],[x+1,y-1],[x-1,y+1],[x+1,y+1]])

				for xp,yp in posicoes_adjacentes:
					if np.sign(self.configuracao[yp][xp]) != np.sign(self.jogador_da_vez):
						if self.configuracao[yp][xp] == 0:
							if self.jogador_da_vez == 1:
								if yp < y:
									self.locais_casas_possiveis.append([xp,yp])
							else:
								if yp > y:
									self.locais_casas_possiveis.append([xp,yp])

						if np.sign(self.configuracao[yp][xp]) == -1*np.sign(self.jogador_da_vez):
							if xp > x:
								xp = x+2
							else:
								xp = x-2
							if yp > y:
								yp = y+2
							else:
								yp = y-2
							if xp in xrange(10) and yp in xrange(10):
								if self.configuracao[yp][xp] == 0:
									self.locais_casas_possiveis.append([xp,yp])

			#movimento de damas
			elif np.sign(self.configuracao[y][x]) == np.sign(self.jogador_da_vez) and self.configuracao[y][x] in [-2,2]:
				posicoes_adjacentes=[]

				for a,b in [[-1,-1],[-1,1],[1,-1],[1,1]]:
					xo=xo+a
					yo=yo+b

					while (9>=xo>=0 and 9>=yo>=0):
						if self.configuracao[yo][xo]==0:
							posicoes_adjacentes.append([xo,yo])
						else:
							break
						xo=xo+a
						yo=yo+b

					if 9>=xo>=0 and 9>=yo>=0 and (self.configuracao[yo][xo] == -2*self.jogador_da_vez or self.configuracao[yo][xo] == -1*self.jogador_da_vez):
						posicoes_adjacentes.append([xo,yo])

				for xp,yp in posicoes_adjacentes:
					if np.sign(self.configuracao[yp][xp]) != np.sign(self.jogador_da_vez):
						if self.configuracao[yp][xp] == 0:
							self.locais_casas_possiveis.append([xp,yp])

						if np.sign(self.configuracao[yp][xp]) == -1*np.sign(self.jogador_da_vez):
							if xp > x:
								xp = xp+1
							else:
								xp = xp-1
							if yp > y:
								yp = yp+1
							else:
								yp = yp-1
							if xp in xrange(10) and yp in xrange(10):
								if self.configuracao[yp][xp] == 0:
									self.locais_casas_possiveis.append([xp,yp])

			#movimentos de xadrez
			elif (self.configuracao[y][x]%2 == 1 and self.jogador_da_vez == 1) or (self.configuracao[y][x]%2 == 0 and self.jogador_da_vez == -1):

				#movimento de peões brancos
				if self.configuracao[y][x] == 3:
					posicoes_adjacentes=[]

					xo = x-1
					yo = y-1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0 and self.configuracao[yo][xo] != 0:
							posicoes_adjacentes.append([xo,yo])

					xo = x
					yo = y-1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo] == 0:
							posicoes_adjacentes.append([xo,yo])

							if y == 6:
								if self.configuracao[yo-1][xo] == 0:
									posicoes_adjacentes.append([xo,yo-1])

					xo = x+1
					yo = y-1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0 and self.configuracao[yo][xo] != 0:
							posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == 1:
							if self.configuracao[yp][xp]%2 != 1:
								self.locais_casas_possiveis.append([xp,yp])

				#movimento de peões pretos
				if self.configuracao[y][x] == 4:
					posicoes_adjacentes=[]

					xo = x-1
					yo = y+1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1:
							posicoes_adjacentes.append([xo,yo])

					xo = x
					yo = y+1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == -1 and self.configuracao[yo][xo] == 0:
							posicoes_adjacentes.append([xo,yo])

							if y == 1:
								if self.configuracao[yo+1][xo] == 0:
									posicoes_adjacentes.append([xo,yo+1])

					xo = x+1
					yo = y+1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1:
							posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == -1:
							if self.configuracao[yp][xp] == 0:
								self.locais_casas_possiveis.append([xp,yp])
							elif self.configuracao[yp][xp]%2 != 0:
								self.locais_casas_possiveis.append([xp,yp])

				#movimento de torres
				elif self.configuracao[y][x] in [5,6]:
					posicoes_adjacentes=[]

					xo = x-1
					yo = y

					while(7>=xo>=0):

						if self.configuracao[yo][xo] == 0:
							posicoes_adjacentes.append([xo,yo])
						else:
							break

						xo -= 1

					if 7>=xo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0:
							posicoes_adjacentes.append([xo,yo])
						elif self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1:
							posicoes_adjacentes.append([xo,yo])					

					xo = x
					yo = y+1

					while(7>=yo>=0):

						if self.configuracao[yo][xo] == 0:
							posicoes_adjacentes.append([xo,yo])
						else:
							break

						yo += 1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0:
							posicoes_adjacentes.append([xo,yo])
						elif self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1:
							posicoes_adjacentes.append([xo,yo])	

					xo = x+1
					yo = y

					while(7>=xo>=0):

						if self.configuracao[yo][xo] == 0:
							posicoes_adjacentes.append([xo,yo])
						else:
							break

						xo += 1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0:
							posicoes_adjacentes.append([xo,yo])
						elif self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1:
							posicoes_adjacentes.append([xo,yo])	

					xo = x
					yo = y-1

					while(7>=yo>=0):

						if self.configuracao[yo][xo] == 0:
							posicoes_adjacentes.append([xo,yo])
						else:
							break

						yo -= 1

					if 7>=xo>=0 and 7>=yo>=0:
						if self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0:
							posicoes_adjacentes.append([xo,yo])
						if self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1:
							posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == 1:
							if self.configuracao[yp][xp]%2 != 1:
								self.locais_casas_possiveis.append([xp,yp])
						if self.jogador_da_vez == -1:
							if self.configuracao[yp][xp] == 0:
								self.locais_casas_possiveis.append([xp,yp])
							elif self.configuracao[yp][xp]%2 != 0:
								self.locais_casas_possiveis.append([xp,yp])

				#movimento de cavalos
				elif self.configuracao[y][x] in [7,8]:
					posicoes_adjacentes=[]

					for a,b in [[2,1],[2,-1],[-2,1],[-2,-1],[1,2],[-1,2],[1,-2],[-1,-2]]:
						xo=x+a
						yo=y+b
						if 7>=xo>=0 and 7>=yo>=0:
							if (self.jogador_da_vez==1 and self.configuracao[yo][xo]%2==0) or (self.jogador_da_vez==-1 and (self.configuracao[yo][xo]%2==1 or self.configuracao[yo][xo]==0)):
								posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == 1:
							if self.configuracao[yp][xp]%2 != 1:
								self.locais_casas_possiveis.append([xp,yp])
						if self.jogador_da_vez == -1:
							if self.configuracao[yp][xp] == 0:
								self.locais_casas_possiveis.append([xp,yp])
							elif self.configuracao[yp][xp]%2 != 0:
								self.locais_casas_possiveis.append([xp,yp])

				#movimento de bispos
				elif self.configuracao[y][x] in [9,10]:
					posicoes_adjacentes=[]

					for a,b in [[-1,-1],[-1,1],[1,-1],[1,1]]:
						xo=xo+a
						yo=yo+b

						while(7>=xo>=0 and 7>=yo>=0):
							if self.configuracao[yo][xo] == 0:
								posicoes_adjacentes.append([xo,yo])
							else:
								break

							xo=xo+a
							yo=yo+b

						if 7>=xo>=0 and 7>=yo>=0:
							if (self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0) or (self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1):
								posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == 1:
							if self.configuracao[yp][xp]%2 != 1:
								self.locais_casas_possiveis.append([xp,yp])
						if self.jogador_da_vez == -1:
							if self.configuracao[yp][xp] == 0:
								self.locais_casas_possiveis.append([xp,yp])
							elif self.configuracao[yp][xp]%2 != 0:
								self.locais_casas_possiveis.append([xp,yp])
								
				#movimento de rainhas
				elif self.configuracao[y][x] in [11,12]:
					posicoes_adjacentes=[]

					for a,b in [[-1,-1],[-1,1],[1,-1],[1,1],[-1,0],[0,1],[1,0],[0,-1]]:
						xo=x+a
						yo=y+b
						while (7>=xo>=0 and 7>=yo>=0):
							if self.configuracao[yo][xo]==0:
								posicoes_adjacentes.append([xo,yo])
							else:
								break
							xo=xo+a
							yo=yo+b

						if 7>=xo>=0 and 7>=yo>=0:
							if (self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0) or (self.jogador_da_vez == -1 and self.configuracao[yo][xo]%2 == 1):
								posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == 1:
							if self.configuracao[yp][xp]%2 != 1:
								self.locais_casas_possiveis.append([xp,yp])
						if self.jogador_da_vez == -1:
							if self.configuracao[yp][xp] == 0:
								self.locais_casas_possiveis.append([xp,yp])
							elif self.configuracao[yp][xp]%2 != 0:
								self.locais_casas_possiveis.append([xp,yp])

				#movimento de reis
				elif self.configuracao[y][x] in [13,14]:
					posicoes_adjacentes=[]

					for a,b in [[1,1],[1,0],[1,-1],[0,1],[0,-1],[-1,1],[-1,0],[-1,-1]]:
						xo=x+a
						yo=y+b
						if 7>=xo>=0 and 7>=yo>=0:
							if (self.jogador_da_vez == 1 and self.configuracao[yo][xo]%2 == 0) or (self.jogador_da_vez == -1 and (self.configuracao[yo][xo]%2 == 1 or self.configuracao[yo][xo] == 0)):
								posicoes_adjacentes.append([xo,yo])

					for xp,yp in posicoes_adjacentes:
						if self.jogador_da_vez == 1:
							if self.configuracao[yp][xp]%2 != 1:
								self.locais_casas_possiveis.append([xp,yp])
						if self.jogador_da_vez == -1:
							if self.configuracao[yp][xp] == 0:
								self.locais_casas_possiveis.append([xp,yp])
							elif self.configuracao[yp][xp]%2 != 0:
								self.locais_casas_possiveis.append([xp,yp])

					temp_casas_possiveis = self.locais_casas_possiveis
					temp = [x,y]
					temp_novas_casas_possiveis = temp_casas_possiveis + []

					for m in temp_casas_possiveis:
						if self.jogador_da_vez == 1:
							self.jogador_da_vez = -1
							for i in range(8):
								for j in range(8):
									if self.configuracao[j][i] %2 != 1 and self.configuracao[j][i] != 0 and self.configuracao[j][i] != 14:
										self.local_casa_atual = [i,j]
										temp_peca = self.configuracao[m[1]][m[0]]
										self.configuracao[m[1]][m[0]] = 13
										self.set_casas_possiveis_prox_movimento()
										for k in self.locais_casas_possiveis:
											if k == m:
												try:
													temp_novas_casas_possiveis.remove(k)
												except:
													pass
										self.configuracao[m[1]][m[0]] = temp_peca

									if self.configuracao[j][i] %2 != 1 and self.configuracao[j][i] != 0 and self.configuracao[j][i] == 14:
										for k in temp_novas_casas_possiveis:
											for a,b in [[1,-1],[1,0],[1,1],[0,-1],[0,1],[-1,-1],[-1,0],[-1,1]]:
												if k == [i+a,j+b]:
													try:
														temp_novas_casas_possiveis.remove(k)
													except:
														pass

							self.local_casa_atual = temp
							self.jogador_da_vez = 1

						if self.jogador_da_vez == -1:
							self.jogador_da_vez = 1
							for i in range(8):
								for j in range(8):
									if self.configuracao[j][i] %2 != 0 and self.configuracao[j][i] != 13:
										self.local_casa_atual = [i,j]
										temp_peca = self.configuracao[m[1]][m[0]]
										self.configuracao[m[1]][m[0]] = 14
										self.set_casas_possiveis_prox_movimento()
										for k in self.locais_casas_possiveis:
											if k == m:
												try:
													temp_novas_casas_possiveis.remove(k)
												except:
													pass
										self.configuracao[m[1]][m[0]] = temp_peca

									if self.configuracao[j][i] %2 != 0 and self.configuracao[j][i] == 13:
										for k in temp_novas_casas_possiveis:
											for a,b in [[1,-1],[1,0],[1,1],[0,-1],[0,1],[-1,-1],[-1,0],[-1,1]]:
												if k == [i+a,j+b]:
													try:
														temp_novas_casas_possiveis.remove(k)
													except:
														pass

							self.local_casa_atual = temp
							self.jogador_da_vez = -1
							
					self.locais_casas_possiveis = temp_novas_casas_possiveis

			else:
				return []

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
		self.imagem.set_colorkey(0)
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
	def __init__(self,numero_peca,dimensao_casa,player,jogo):
		#dimensão de cada peça
		self.dimensao=[int(self.dimensao_percentual*dimensao_casa[0]),int(self.dimensao_percentual*dimensao_casa[1])]

		if jogo == 1:
			#capturando e convertendo a imagem para um formato mais rápido e com as dimensões desejadas sem distorcê-la
			peca=image.load('imagens/helm%s.png'%numero_peca).convert_alpha()

		if jogo == 2:
			peca=image.load('imagens/xadrez%s.png'%numero_peca).convert_alpha()

		xo,yo=peca.get_size() #dimensões originais
		x,y=self.dimensao #dimensões desejadas

		if float(xo)/x>float(yo)/y:
			L=int(y*xo/float(yo))
			peca=transform.scale(peca,[L,y])
		else:
			H=int(x*yo/float(xo))
			peca=transform.scale(peca,[x,H])

		self.imagem=peca

#1 para damas; 2 para xadrez
jogo_selecionado = 2

screen=Janela()
jogo=Jogo(pytime)

tab=Tabuleiro([10,10],screen.dimensao,jogo_selecionado)

chars=range(1,len(Avatar.nomes)+1)
char1=random.choice(chars)
chars.remove(char1)
char2=random.choice(chars)

avatar1=Avatar(char1,screen.dimensao,player=1)
avatar2=Avatar(char2,screen.dimensao,player=-1)


#configurando fontes das legendas das telas iniciais e dos menus
diretorio_fonte='fontes/Starjedi.ttf'

negrito=1
italico=0
cor=(214,197,2)

#criando menu de seleção do jogo
tam1=30
fonte1=font.Font(diretorio_fonte,tam1)

tam2=50
fonte2=font.Font(diretorio_fonte,tam2)


legenda1=fonte1.render('selecione o jogo desejado:',1,cor)
pos1=[int(0.5*screen.dimensao[0]-0.5*legenda1.get_width()),int(0.22*screen.dimensao[1])]
legenda2=fonte2.render('damas',1,cor)
pos2=[int(0.5*screen.dimensao[0]-0.5*legenda2.get_width()),int(0.22*screen.dimensao[1]+2*legenda1.get_height())]
legenda3=fonte2.render('xadrez',1,cor)
pos3=[int(0.5*screen.dimensao[0]-0.5*legenda3.get_width()),int(0.22*screen.dimensao[1]+2*legenda2.get_height())]
selecionador=font.SysFont('arial',tam2,negrito,italico).render('>',1,cor)
pos_selecionador1=[int(pos2[0]-0.4*legenda2.get_width()),pos2[1]+0.2*selecionador.get_height()]
pos_selecionador2=[pos_selecionador1[0],pos3[1]+0.2*selecionador.get_height()]

jogo_selecionado=0
escolhendo_jogo=True
while escolhendo_jogo:
	for evento in event.get():
		if evento.type==QUIT:
			jogo.quit()
		if evento.type==KEYDOWN:
			if evento.key==K_UP:
				jogo_selecionado=0
			elif evento.key==K_DOWN:
				jogo_selecionado=1
			elif evento.key==13: #13 é o código do ENTER no pygame
				escolhendo_jogo=False
				break
	screen.tela.blit(legenda1,pos1)
	screen.tela.blit(legenda2,pos2)
	screen.tela.blit(legenda3,pos3)
	if jogo_selecionado:
		screen.tela.blit(selecionador,pos_selecionador2)
	else:
		screen.tela.blit(selecionador,pos_selecionador1)
	display.update()
	screen.tela.fill((0,0,0))
jogo_selecionado+=1

if jogo_selecionado == 1:
	pecas=range(1,5)
	peca1=random.choice(pecas)
	pecas.remove(peca1)
	peca2=random.choice(pecas)
	pecas.remove(peca2)
	peca3=random.choice(pecas)
	pecas.remove(peca3)
	peca4=random.choice(pecas)
	pecas.remove(peca4)

	peca1=Peca(peca1,tab.dimensoes_casas,1,1)
	peca2=Peca(peca2,tab.dimensoes_casas,-1,1)
	peca3=Peca(peca3,tab.dimensoes_casas,1,1)
	peca4=Peca(peca4,tab.dimensoes_casas,-1,1)

if jogo_selecionado == 2:
	peca1,peca2,peca3,peca4,peca5,peca6,peca7,peca8,peca9,peca10,peca11,peca12=[Peca(i,tab.dimensoes_casas,[-1,1][i%2],2) for i in xrange(3,15)]

rec = sr.Recognizer() #instanciamos o módulo do reconhecedor

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
	print u'\nVez do jogador %s\n'%tab.jogador_da_vez
	return comando

def rotinas():
	u'''Agrupei nesta função as atividades que precisam ser "rodadas" ao final de cada quadro'''
	#atualizando o tempo
	jogo.tempo+=1
	
	#atualizando a tela
	display.update()
	
	#"limpando"(na verdade eu estou pintando ela de rgb=(0,0,0)=preto) a tela --- essa limpeza só será visualizada na próxima vez que a tela for atualizada
	#screen.tela.fill((0,0,0))
	screen.desenhar_fundo()

	#fazendo o jogo rodar com a qtd de quadros por segundos estabelecida
	#jogo.time.Clock().tick(jogo.fps) #neste software em particular eu não vou utilizar isso

tempo_para_iniciar=3600

#tocando música de fundo
musica_fundo=mixer.Sound('som_fundo.ogg')
musica_fundo.play()

tam1=80
fonte1=font.Font(diretorio_fonte,tam1)

tam2=30
fonte2=font.Font(diretorio_fonte,tam2)

legenda1=fonte1.render(['jogo de damas','jogo de xadrez'][jogo_selecionado-1],1,cor)
pos1=[int(0.5*screen.dimensao[0]-0.5*legenda1.get_width()),int(0.2*screen.dimensao[1])]
legenda2=fonte2.render('com processamento de voz',1,cor)
pos2=[int(0.5*screen.dimensao[0]-0.5*legenda2.get_width()),int(0.22*screen.dimensao[1]+legenda1.get_height())]

def jogar():
	while jogo.run:
		#analisando os eventos que ocorreram no quadro atual
		for evento in event.get():
			if evento.type==QUIT:
				jogo.quit()

		if jogo.tempo>tempo_para_iniciar:
			
			if jogo.tempo>tempo_para_iniciar+1:
				#comando=comando_de_voz()
				comando = raw_input("Digite posicao: ")

				print comando

			else:
				comando=''

			#retira o delay no processo de colorir as peças
			for i in range(2):

				tab.analisar_comando(comando)
				
				#desenhando o tabuleiro
				screen.tela.blit(tab.imagem,tab.posicao)
				
				#desenhando as peças
				if jogo_selecionado == 1:
					tab.desenhar_pecas(screen,peca1.imagem,peca2.imagem,peca3.imagem,peca4.imagem)

				if jogo_selecionado == 2:
					tab.desenhar_pecas(screen,peca1.imagem,peca2.imagem,peca3.imagem,peca4.imagem,peca5.imagem,peca6.imagem,peca7.imagem,peca8.imagem,peca9.imagem,peca10.imagem,peca11.imagem,peca12.imagem)

				#posicionando os avatares
				screen.tela.blit(avatar1.imagem,avatar1.posicao)
				screen.tela.blit(avatar2.imagem,avatar2.posicao)

		else: #enquanto o jogo ainda está iniciando:
			screen.tela.blit(legenda1,pos1)
			screen.tela.blit(legenda2,pos2)
				
		#rotinas que preciso rodar toda vez que um quadro terminar
		rotinas()

jogar()

#fechar a janela do pygame
quit()

#fechar a aplicação python
sys.exit()