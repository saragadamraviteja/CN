import socket
import random
import threading

def getGuessedWord(secretWord,lettersGuessed):
  '''
  secretword : String, word user is guessing!
  lettersguessed : List, letters guessed so far
  returns String, with letters and underscores that represents what
  letters in secretword have been guessed so far
  '''
  l,i = [],0
  while i<len(secretWord):
    for j in secretWord:
      if j in lettersGuessed:
        l.insert(i,j)
      else :
        l.insert(i,'_')
      i+=1
  return ''.join(l)



def replay(name):
    # print(name)
    conn.send("The Leaderboard is as follows: \n".encode())
    for i in scores:
        scores[i] = int(scores[i])
    board = sorted(scores.items(), key = lambda kv:(kv[1], kv[0]))
    for i in board:
        # le = len(i)
        le = len(i[0])
        p = 15 - le
        s = " " * p
        text = i[0] + s + str(i[1]) + '\n'
        conn.send(text.encode())
    conn.send('end'.encode())
    return

def getAvailableLetters(lettersGuessed):
    availableLetters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    for c in lettersGuessed:
        availableLetters.remove(c)
    availableLettersString = ''
    for e in availableLetters:
        availableLettersString =  availableLettersString + e
    return availableLettersString

def isWordGuessed(secretWord, lettersGuessed):
    '''
    secretWord: string, the word the user is guessing
    lettersGuessed: list, what letters have been guessed so far
    returns: boolean, True if all the letters of secretWord are in lettersGuessed;
      False otherwise
    '''
    result = False
    for c in secretWord:
        if c in lettersGuessed:
            result = True
        else:
            return False
    return result

def score_cal(word, guess):
    n = len(word)
    m = 10 * n
    dif = (6 - guess) * n
    score = m - dif
    return score

def start_game(secretword,names):
    chances = 8
    lettersGuessed = []
    while chances > 0:
        conn.send(('you have ' + str(chances) + 'guesses left.\n').encode())
        data = 'Available Letters: '+ getAvailableLetters(lettersGuessed) + '\n.'
        conn.send(data.encode())
        conn.send('guess a letter: \n check'.encode())
        guess = conn.recv(1024).decode()
        bool_value, guess = letter_invalid(guess)
        # print(bool_value)
        if bool_value:
            conn.send('Invalid character.\n'.encode())
            continue
        else:
            print(getAvailableLetters(lettersGuessed))
            if guess in lettersGuessed:
                conn.send(('Oops! you have already guessed that letter: '+ getGuessedWord(secretword,lettersGuessed)+ '.\n').encode())
                conn.send('--------------------.\n'.encode())
                continue
            lettersGuessed += guess
            # temp = getAvailableLetters(lettersGuessed)
            if guess in secretword:
                show = getGuessedWord(secretword, lettersGuessed)
                conn.send(('Good guess: '+ show).encode())
                conn.send('-------------------------.\n'.encode())
                if isWordGuessed(secretword, lettersGuessed):
                    conn.send(('congrats! you won.\n').encode())
                    r = score_cal(secretword,chances)
                    t = "Your score is " + str(r) + " "
                    conn.send(t.encode())
                    if names in scores.keys():
                            scores[names] = str(int(scores[names]) + r)
                    else:
                        scores[names] = str(r)
                    # conn.send('check'.encode())
                    replay(names)
                    return
            else:
                text = "Oops! That letter is not in my word: "+ getGuessedWord(secretword, lettersGuessed) + ".\n"
                conn.send(text.encode())
                conn.send("-----------------------------.\n".encode())
                chances -= 1
    if chances == 0:
        text = "Sorry You ran out of choices, the word is: " + secretword + ".\n"
        conn.send(text.encode())
        conn.send("Your score is 0 ".encode())
        if names in scores.keys():
            scores[names] = str(int(scores[names]) + 0)
        elif len(names) > 0:
            scores[names] = '0'
        # conn.send('check'.encode())
        replay(names)
        return  


def letter_invalid(guessed_letter):
    guessed_letter = guessed_letter.lower()
    guessed_letter = guessed_letter.strip("   ")
    return (
        len(guessed_letter) != 1 or not ("a" <= guessed_letter <= "z"),
        guessed_letter
    )

def word(i):
    # print('here')
    wordlist = open('words.txt','r').read().split(" ")
    secretword = wordlist[random.choice(0,len(wordlist))]
    # print(i)
    if i in prevwords:
        if secretword in i:
            word(i)
        else:
            prevwords[i] = secretword
    if i in prevwords:
        if secretword in i:
            word(i)
        else:
            prevwords[i] = secretword
    else:
        prevwords[i] = secretword
    print(secretword)
    conn.send('welcome to the game, Hangman!\n'.encode())
    conn.send(('I am thinking of a word that is ' + str(len(secretword))+ ' letters long.\n').encode())
    conn.send('----------------------.\n'.encode())
    start_game(secretword, i)
    return 'close'


def start_server(conn):
    while 1:
        conn.send('select 0: old user, select 1: new user check'.encode())
        response = conn.recv(1024).decode()
        if response == '0':
            conn.send('Enter your name: check'.encode())
            username = conn.recv(1024).decode()
            conn.send('Enter your password: check'.encode())
            password = conn.recv(1024).decode()
            # print(users)
            if username in users.keys() and users[username] == password:
                message = word(username)
                if message == 'close':
                    conn.close()
        elif response == '1':
            conn.send('enter username: check'.encode())
            name = conn.recv(1024).decode()
            conn.send('enter password: check'.encode())
            pswd = conn.recv(1024).decode()
            users[name] = pswd
            # scores[names] = '0'
            conn.send(('welcome '+ name).encode())
            message = word(name)
            if message == 'close':
                conn.close()
        else:
            conn.send('Invalid Response'.encode())




sock = socket.socket()
sock.bind(('',8003))
sock.listen(1024)

users = {}
board = {}
prevwords = {}
scores = {}
names = ""
while True:
    conn,addr = sock.accept()
    thread = threading.Thread(target = start_server, args = (conn,))
    thread.start()