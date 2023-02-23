from imutils import contours
from imutils import grab_contours
import cv2
import pytesseract
import numpy as np

possiveisEscolhas = ['A', 'B', 'C', 'D', 'E']

p1 = (210,830)
p2 = (1550, 2480)

def recortaProva(img):
    resize = 0.5 
    imgColorida = cv2.imread(img) #Carregamento da imagems
    imgColorida = cv2.resize(imgColorida, (2480, 3508))

    # Mostra imagem de entrada
    #cv2.imshow('img', imgColorida)

    # crop na imagem
    imgRecortadaAutenticacao = imgColorida[200:370, 1720:2220]
    imgRecortadaMarcacoesA = imgColorida[1010:3100, p1[0]:p1[1]]
    imgRecortadaMarcacoesB = imgColorida[1010:3100, p2[0]:p2[1]]
    imgRecortadaAutenticacao = cv2.resize(imgRecortadaAutenticacao, (int(imgRecortadaAutenticacao.shape[1] * resize), int(imgRecortadaAutenticacao.shape[0] * resize)))
    imgRecortadaMarcacoesA = cv2.resize(imgRecortadaMarcacoesA, (int(imgRecortadaMarcacoesA.shape[1] * resize), int(imgRecortadaMarcacoesA.shape[0] * resize)))
    imgRecortadaMarcacoesB = cv2.resize(imgRecortadaMarcacoesB, (int(imgRecortadaMarcacoesB.shape[1] * resize), int(imgRecortadaMarcacoesB.shape[0] * resize)))
    return imgRecortadaAutenticacao, imgRecortadaMarcacoesA, imgRecortadaMarcacoesB

def encontraContornos(image):
    thresh = trataImagem(image)

    # Mostra imagem tratada para reconhecimento das marcações
    # cv2.imshow('a', thresh)
    # cv2.waitKey()

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = grab_contours(cnts)
    questionCnts = []  # contorno das alternativas

    # verifica a hitbox de cada contorno e mantem somente os circulos (maiores)
    for c in cnts:
        area = cv2.contourArea(c)
        
        # Alternativa para reconhecimento das marcações
        # (x, y, w, h) = cv2.boundingRect(c)
        # ar = w / float(h)
        # if w >= 30 and h >= 30 and ar >= 0.7 and ar <= 1.3:
        #     questionCnts.append(c)

        if area > 700: # area da alternativa possui em media 800 px
            questionCnts.append(c)

    # organiza os contornos na ordem do topo até em baixo 
    questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]
    bubbledList = []
    # cada questao tem 5 respostas disponiveis, entao faco um loop para separar de 5 em 5 contornos
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
        cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
        bubbled = None
        for (j, c) in enumerate(cnts):      
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask) # somente a alternativa que está sendo verificada está pintada em branco, então contamos quantos pixels brancos tem na imagem
            
            # Mostra a alternativa q está sendo verificada
            # cv2.imshow('mask', mask)
            # cv2.waitKey()
            if bubbled is None or total > bubbled[0]: # guardamos a alternativa que mais contem pixels brancos
                bubbled = (total, j)
        
        # Mostra alternativa marcada
        #print(q + 1, possiveisEscolhas[bubbled[1]])
        bubbledList.append(bubbled[1])
    return bubbledList # retorna as alternativas marcadas na prova

def trataImagem(imagem):
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    return thresh # retorna imagem binária (somente preto e branco)

def leInstricao(provaRecortadaNome):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\luiz.monteiro\AppData\Local\Programs\Tesseract-OCR\tesseract.exe";
    texto = pytesseract.image_to_string(provaRecortadaNome).split('\n')
    for i in texto:
        try:
            return int(i)
        except:
            return 0

def resultado(path):
    provaRecortadaAutenticacao, provaRecortadaGabA, provaRecortadaGabB = recortaProva(path)

    alternativasA = encontraContornos(provaRecortadaGabA)
    alternativasB = encontraContornos(provaRecortadaGabB)
    alternativas = alternativasA + alternativasB

    for i, j in enumerate(alternativas):
        alternativas[i] = possiveisEscolhas[j]
    
    # Le o numero da inscricao
    #autenticacao = (provaRecortadaAutenticacao)
    return alternativas

if __name__ == '__main__':
    print(resultado(r"prova.jpg"))
