import random
import pygame
import sys
from pathlib import Path

pygame.init()

TAMANHO_BLOCO = 30
BOARD_LARGURA = 300
LARGURA = 420
ALTURA = 600
COLUNAS = BOARD_LARGURA // TAMANHO_BLOCO
LINHAS = ALTURA // TAMANHO_BLOCO
PAINEL_X = BOARD_LARGURA

PRETO = (0, 0, 0)
CINZA = (50, 50, 50)
BRANCO = (255, 255, 255)
PANEL_BG = (20, 20, 20)
CORES = [
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 165, 0),
]

PECAS = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
]

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tetris em tempo real")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 24)
fonte_pequena = pygame.font.SysFont("arial", 20)
ARQUIVO_RANKING = Path(__file__).with_name("ranking.txt")


def criar_grade():
    return [[0 for _ in range(COLUNAS)] for _ in range(LINHAS)]


def verificar_colisao(grade, peca, desloc_x, desloc_y):
    for y, linha in enumerate(peca):
        for x, celula in enumerate(linha):
            if not celula:
                continue
            novo_x = x + desloc_x
            novo_y = y + desloc_y
            if novo_x < 0 or novo_x >= COLUNAS or novo_y >= LINHAS:
                return True
            if novo_y >= 0 and grade[novo_y][novo_x]:
                return True
    return False


def mesclar_peca(grade, peca, desloc_x, desloc_y, cor_idx):
    for y, linha in enumerate(peca):
        for x, celula in enumerate(linha):
            if celula:
                grade[y + desloc_y][x + desloc_x] = cor_idx


def limpar_linhas(grade):
    linhas_limpas = 0
    y = LINHAS - 1
    
    while y >= 0:
        if 0 not in grade[y]:
            del grade[y]
            grade.insert(0, [0 for _ in range(COLUNAS)])
            linhas_limpas += 1
        else:
            y -= 1
            
    return linhas_limpas


def rotacionar_peca(peca):
    return [list(linha) for linha in zip(*peca[::-1])] 

def rotacionar_peca_antihorario(peca):
    return [list(linha) for linha in zip(*[linha[::-1] for linha in peca])]


def validar_peca(grade, peca, desloc_x, desloc_y):
    return not verificar_colisao(grade, peca, desloc_x, desloc_y)


def criar_nova_peca():
    peca = random.choice(PECAS)
    cor = PECAS.index(peca) + 1
    return peca, cor


def posicao_inicial(peca):
    return COLUNAS // 2 - len(peca[0]) // 2, 0


def desenhar_texto(texto, x, y, cor=BRANCO):
    imagem = fonte.render(texto, True, cor)
    tela.blit(imagem, (x, y))


def desenhar_texto_pequeno(texto, x, y, cor=BRANCO):
    imagem = fonte_pequena.render(texto, True, cor)
    tela.blit(imagem, (x, y))


def desenhar_grade(tela, grade):
    for y in range(LINHAS):
        for x in range(COLUNAS):
            cor = grade[y][x]
            retangulo = (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
            if cor:
                pygame.draw.rect(tela, CORES[cor - 1], retangulo)
                pygame.draw.rect(tela, BRANCO, retangulo, 1)
            else:
                pygame.draw.rect(tela, CINZA, retangulo, 1)


def desenhar_peca(tela, peca, cor_idx, x_peca, y_peca):
    for y, linha in enumerate(peca):
        for x, celula in enumerate(linha):
            if celula:
                retangulo = ((x_peca + x) * TAMANHO_BLOCO, (y_peca + y) * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
                pygame.draw.rect(tela, CORES[cor_idx - 1], retangulo)
                pygame.draw.rect(tela, BRANCO, retangulo, 1)


def desenhar_sombra(tela, grade, peca, cor_idx, x_peca, y_peca): # Utilizado para saber onde a peça atual irá cair!
    drop_y = y_peca
    while validar_peca(grade, peca, x_peca, drop_y + 1):
        drop_y += 1
    for y, linha in enumerate(peca):
        for x, celula in enumerate(linha):
            if celula:
                s = pygame.Surface((TAMANHO_BLOCO, TAMANHO_BLOCO), pygame.SRCALPHA)
                r, g, b = CORES[cor_idx - 1]
                s.fill((r, g, b, 80))
                pos = ((x_peca + x) * TAMANHO_BLOCO, (drop_y + y) * TAMANHO_BLOCO)
                tela.blit(s, pos)
                pygame.draw.rect(tela, BRANCO, (pos[0], pos[1], TAMANHO_BLOCO, TAMANHO_BLOCO), 1)


def desenhar_preview(peca, cor_idx, caixa_x, caixa_y, caixa_largura, caixa_altura):
    bloco = 18
    largura_peca = len(peca[0]) * bloco
    altura_peca = len(peca) * bloco
    offset_x = caixa_x + (caixa_largura - largura_peca) // 2
    offset_y = caixa_y + (caixa_altura - altura_peca) // 2

    for y, linha in enumerate(peca):
        for x, celula in enumerate(linha):
            if celula:
                retangulo = (offset_x + x * bloco, offset_y + y * bloco, bloco, bloco)
                pygame.draw.rect(tela, CORES[cor_idx - 1], retangulo)
                pygame.draw.rect(tela, BRANCO, retangulo, 1)


def desenhar_painel(peca_seguinte, cor_seguinte, peca_segura, cor_segura):
    painel_largura = LARGURA - PAINEL_X
    pygame.draw.rect(tela, PANEL_BG, (PAINEL_X, 0, painel_largura, ALTURA))
    pygame.draw.line(tela, BRANCO, (PAINEL_X, 0), (PAINEL_X, ALTURA), 2)

    desenhar_texto_pequeno("Proxima", PAINEL_X + 18, 20)
    pygame.draw.rect(tela, CINZA, (PAINEL_X + 18, 55, painel_largura - 36, 110), 1)
    desenhar_preview(peca_seguinte, cor_seguinte, PAINEL_X + 18, 55, painel_largura - 36, 110)

    desenhar_texto_pequeno("Segurada", PAINEL_X + 18, 195)
    pygame.draw.rect(tela, CINZA, (PAINEL_X + 18, 230, painel_largura - 36, 110), 1)
    if peca_segura is None:
        desenhar_texto_pequeno("--", PAINEL_X + 50, 270)
    else:
        desenhar_preview(peca_segura, cor_segura, PAINEL_X + 18, 230, painel_largura - 36, 110)

    fonte_instrucoes = pygame.font.SysFont("arial", 16)
    instrucoes = [
        "C/Shift: segurar",
        "Setas: mover",
        "Up/X: girar dir.",
        "Z: girar esq.",
        "Espaço: descer"
    ]
    y_instr = 380
    for instrucao in instrucoes:
        imagem = fonte_instrucoes.render(instrucao, True, BRANCO)
        tela.blit(imagem, (PAINEL_X + 10, y_instr))
        y_instr += 22


def desenhar_mensagem_central(texto, cor=BRANCO):
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect(center=(BOARD_LARGURA // 2, ALTURA // 2))
    tela.blit(imagem, retangulo)


def limpar_nome_ranking(nome):
    return nome.replace(";", " ").replace("\n", " ").replace("\r", " ").strip()


def carregar_ranking():
    entradas = []
    if not ARQUIVO_RANKING.exists():
        return entradas

    try:
        with ARQUIVO_RANKING.open("r", encoding="utf-8") as arq:
            for linha in arq:
                partes = [parte.strip() for parte in linha.strip().split(";")]
                if len(partes) < 2:
                    continue

                nome = partes[0] or "Anonimo"
                try:
                    pontos_lidos = int(partes[1])
                except ValueError:
                    continue

                nivel_lido = partes[2] if len(partes) > 2 and partes[2] else "1"
                entradas.append((nome, pontos_lidos, nivel_lido))
    except Exception:
        pass

    return entradas


def salvar_ranking(nome, pontuacao, nivel_atual):
    entradas = carregar_ranking()
    entradas.append((limpar_nome_ranking(nome) or "Anonimo", pontuacao, str(nivel_atual)))
    entradas.sort(key=lambda x: x[1], reverse=True)

    try:
        with ARQUIVO_RANKING.open("w", encoding="utf-8") as arq:
            for nome_e, pontos_e, nivel_e in entradas[:10]:
                arq.write(f"{limpar_nome_ranking(nome_e) or 'Anonimo'};{pontos_e};{nivel_e}\n")
    except Exception:
        pass


def escolher_nivel_ui():
    nivel = 1
    selecionando = True
    while selecionando:
        relogio.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    nivel = nivel + 1 if nivel < 15 else 1
                elif evento.key == pygame.K_DOWN:
                    nivel = nivel - 1 if nivel > 1 else 15
                elif evento.key == pygame.K_RETURN:
                    selecionando = False

        tela.fill(PRETO)
        titulo = fonte.render("Escolha o nivel (Up/Down) e pressione Enter", True, BRANCO)
        rect = titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40))
        tela.blit(titulo, rect)

        nivel_txt = fonte.render(str(nivel), True, (255, 215, 0))
        rect2 = nivel_txt.get_rect(center=(LARGURA // 2, ALTURA // 2 + 10))
        tela.blit(nivel_txt, rect2)

        instru = fonte_pequena.render("Pressione Esc para sair", True, CINZA)
        tela.blit(instru, (LARGURA - 200, ALTURA - 30))

        pygame.display.flip()

    return nivel


def main():
    grade = criar_grade()
    jogando = True
    pontuacao = 0

    nivel_inicial = escolher_nivel_ui()

    peca_atual, cor_atual = criar_nova_peca()
    peca_seguinte, cor_seguinte = criar_nova_peca()
    peca_segura = None
    cor_segura = None
    pode_segurar = True
    tempo_queda = 0
    tempo_queda_manual = 0
    tempo_fixacao = 0
    nivel_atual = nivel_inicial
    pecas_eliminadas = 0
    mensagem_tetris = 0
    mensagem_all_clear = 0
    x_peca, y_peca = posicao_inicial(peca_atual)

    def velocidade_por_nivel(nivel):
        return max(80, 700 - (nivel - 1) * 45)

    def atualizar_nivel():
        nonlocal nivel_atual, velocidade_queda
        nivel_atual = min(15, nivel_inicial + pecas_eliminadas // 10)
        velocidade_queda = velocidade_por_nivel(nivel_atual)

    # Cada peça que o jogador fixar, ganha 10 pontos
    # Cada linha limpa dá pontos adicionais: 1 linha = 100, 2 linhas = 200, 3 linhas = 300, 4 linhas (Tetris) = 400 * 5
    # Contabiliza as linhas removidas como "peças" para subir de nível, a cada 10 peças eliminadas, sobe um nível (até o 15)
    def fixar_peca_e_proxima():
        nonlocal peca_atual, cor_atual, peca_seguinte, cor_seguinte
        nonlocal x_peca, y_peca, pode_segurar, pecas_eliminadas, mensagem_tetris, mensagem_all_clear, pontuacao

        mesclar_peca(grade, peca_atual, x_peca, y_peca, cor_atual)
        
        pontuacao += 10
        linhas_limpas = limpar_linhas(grade)
        if linhas_limpas == 0:
            pontuacao_aumento = 0
        elif 1 <= linhas_limpas <= 3:
            pontuacao_aumento = linhas_limpas * 100
        else:
            pontuacao_aumento = 400 * 5
            mensagem_tetris = 60

        pontuacao += pontuacao_aumento
        pecas_eliminadas += linhas_limpas
        atualizar_nivel()

        if all(all(celula == 0 for celula in linha) for linha in grade):
            pontuacao += 10000
            mensagem_all_clear = 90
            mensagem_tetris = 0

        peca_atual, cor_atual = peca_seguinte, cor_seguinte
        peca_seguinte, cor_seguinte = criar_nova_peca()
        x_peca, y_peca = posicao_inicial(peca_atual)
        pode_segurar = True

        if not validar_peca(grade, peca_atual, x_peca, y_peca):
            return False
        return True
    
    velocidade_queda = velocidade_por_nivel(nivel_atual)

    while jogando:
        delta = relogio.tick(60)
        tempo_queda += delta
        teclas = pygame.key.get_pressed()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and validar_peca(grade, peca_atual, x_peca - 1, y_peca):
                    x_peca -= 1
                    tempo_fixacao = 0
                elif evento.key == pygame.K_RIGHT and validar_peca(grade, peca_atual, x_peca + 1, y_peca):
                    x_peca += 1
                    tempo_fixacao = 0
                elif evento.key == pygame.K_UP or evento.key == pygame.K_x:
                    peca_rotacionada = rotacionar_peca(peca_atual)
                    if validar_peca(grade, peca_rotacionada, x_peca, y_peca):
                        peca_atual = peca_rotacionada
                        tempo_fixacao = 0      
                elif evento.key == pygame.K_z:
                    peca_rotacionada = rotacionar_peca_antihorario(peca_atual)
                    if validar_peca(grade, peca_rotacionada, x_peca, y_peca):
                        peca_atual = peca_rotacionada
                        tempo_fixacao = 0
                elif evento.key == pygame.K_SPACE:
                    while validar_peca(grade, peca_atual, x_peca, y_peca + 1):
                        y_peca += 1
                    jogando = fixar_peca_e_proxima()
                elif evento.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT) and pode_segurar:
                    if peca_segura is None:
                        peca_segura, cor_segura = peca_atual, cor_atual
                        peca_atual, cor_atual = peca_seguinte, cor_seguinte
                        peca_seguinte, cor_seguinte = criar_nova_peca()
                    else:
                        peca_atual, peca_segura = peca_segura, peca_atual
                        cor_atual, cor_segura = cor_segura, cor_atual
                    x_peca, y_peca = posicao_inicial(peca_atual)
                    if not validar_peca(grade, peca_atual, x_peca, y_peca):
                        jogando = False
                    pode_segurar = False

        if teclas[pygame.K_DOWN]:
            tempo_queda_manual += delta
            intervalo_queda_manual = max(30, velocidade_queda // 6)
            if tempo_queda_manual >= intervalo_queda_manual:
                tempo_queda_manual = 0
                if validar_peca(grade, peca_atual, x_peca, y_peca + 1):
                    y_peca += 1
        else:
            tempo_queda_manual = 0

        pode_cair = validar_peca(grade, peca_atual, x_peca, y_peca + 1)

        if tempo_queda >= velocidade_queda:
            tempo_queda = 0
            if pode_cair:
                y_peca += 1

        if not pode_cair:
            tempo_fixacao += delta
            atraso_permitido = 500 

            if tempo_fixacao >= atraso_permitido:
                jogando = fixar_peca_e_proxima()
                tempo_fixacao = 0
        else:
            tempo_fixacao = 0

        if mensagem_tetris > 0:
            mensagem_tetris -= 1
        if mensagem_all_clear > 0:
            mensagem_all_clear -= 1

        tela.fill(PRETO)
        desenhar_grade(tela, grade)
        desenhar_sombra(tela, grade, peca_atual, cor_atual, x_peca, y_peca)
        desenhar_peca(tela, peca_atual, cor_atual, x_peca, y_peca)
        desenhar_texto(f"Pontos: {pontuacao}", 8, 8)
        desenhar_texto_pequeno(f"Nivel: {nivel_atual}", 8, 35)
        faltam = 10 - (pecas_eliminadas % 10) if pecas_eliminadas % 10 != 0 else 10
        desenhar_texto_pequeno(f"Para nivel: {faltam}", 8, 60)
        desenhar_painel(peca_seguinte, cor_seguinte, peca_segura, cor_segura)
        if mensagem_tetris > 0:
            desenhar_mensagem_central("Tetris!", (255, 215, 0))
        if mensagem_all_clear > 0:
            desenhar_mensagem_central("All Clear!", (0, 255, 0))
        pygame.display.flip()
    fim_texto = f"Fim de jogo - Pontos: {pontuacao}"
    nome = ""
    digitando = True
    while digitando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                digitando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    digitando = False
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    if evento.unicode and len(nome) < 20:
                        nome += evento.unicode

        tela.fill(PRETO)
        desenhar_texto(fim_texto, 20, ALTURA // 2 - 60)
        desenhar_texto_pequeno("Digite seu nome e pressione Enter:", 20, ALTURA // 2 - 20)
        desenhar_texto_pequeno(nome + ("_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""), 20, ALTURA // 2 + 10)
        pygame.display.flip()

    if not nome:
        nome = "Anonimo"

    # Ranking
    nome = limpar_nome_ranking(nome) or "Anonimo"
    salvar_ranking(nome, pontuacao, nivel_atual)
    entradas = carregar_ranking()

    entradas.sort(key=lambda x: x[1], reverse=True)
    top10 = entradas[:10]

    mostrando = True
    while mostrando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                mostrando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
                    mostrando = False

        tela.fill(PRETO)
        desenhar_texto("Ranking - Top 10", 20, 20)
        y = 60
        for i, entry in enumerate(top10, start=1):
            nome_e, pontos_e, nivel_e = entry
            desenhar_texto_pequeno(f"{i}. {nome_e} - {pontos_e} pts - N{nivel_e}", 20, y)
            y += 28

        desenhar_texto_pequeno("Pressione Enter ou Esc para sair", 20, ALTURA - 30)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()