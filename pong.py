'''
pong made with python
Michael Xilinas
'''

import sys, os
import time
import turtle
import random
import threading
from functools import partial
from playsound import playsound

os.chdir(sys._MEIPASS)

# Global Variables
FRAME_RATE = 60
FRAME_TIME_TARGET = 1 / FRAME_RATE

ARENA_HEIGHT = 400
ARENA_WIDTH = 500

PADDLE_HEIGHT = 100
PADDLE_WIDTH = 25

BALL_HEIGHT = 15
BALL_WIDTH = 15
BALL_SPEED = 10
BALL_ACCELERATION = 1

PLAYER_SPEED = 100
CPU_SPEED = 5

SCORE_LIMIT = 3

DATA = 'data/'
OBJECTS = DATA + 'objects/'
SOUNDS = DATA + 'sounds/'
DIGITS = DATA + 'digits/'
COINS = DATA + 'coins/'
MUSIC = DATA + 'music/'

# Assets
KEY_BINDINGS = {
    'cpu_up': "Up",
    'player_up': "w",
    'player_down': "s",
    'cpu_down': "Down",
    'quit': "Escape",
    'singleplayer': "1",
    'multiplayer': "2"
}

OBJECT_SPRITES = {
    'paddle': OBJECTS + 'paddle.gif',
    'ball': OBJECTS + 'ball.gif',
    'player1_win': OBJECTS + 'player1_winner.gif',
    'player2_win': OBJECTS + 'player2_winner.gif',
    'game_over': OBJECTS + 'game_over.gif',
    'winner': OBJECTS + 'winner.gif'
}

SOUND_EFFECTS = {
    'blip': SOUNDS + 'blip.wav',
    'boop': SOUNDS + 'boop.wav',
    'goal': SOUNDS + 'goal.wav',
    'fail': SOUNDS + 'fail.wav',
    'coin': SOUNDS + 'coin.wav',
    'slot': SOUNDS + 'slot.wav',
    'lose': SOUNDS + 'lose.wav',
    'win': SOUNDS + 'win.wav',

    'impacts': [
        SOUNDS + 'impact0.wav',
        SOUNDS + 'impact1.wav',
    ]
}

NUMBER_SPRITES = [
    DIGITS + 'zero.gif',
    DIGITS + 'one.gif',
    DIGITS + 'two.gif',
    DIGITS + 'three.gif',
    DIGITS + 'four.gif',
    DIGITS + 'five.gif',
    DIGITS + 'six.gif',
    DIGITS + 'seven.gif',
    DIGITS + 'eight.gif',
    DIGITS + 'nine.gif',
    DIGITS + 'ten.gif',
]

COIN_SPRITES = [
    COINS + 'coin0.gif',
    COINS + 'coin1.gif',
    COINS + 'coin2.gif',
    COINS + 'coin3.gif',
    COINS + 'coin4.gif',
    COINS + 'coin5.gif',
]

MUSIC = [
    MUSIC + 'azureflux.mp3',
    MUSIC + 'pocketmaster.mp3',
    MUSIC + 'sawsquarenoise.mp3',
]

# Dynamic Global Variables
playlist = MUSIC[:]
dynamic_ball_speed = BALL_SPEED
number_sprites_cpu = NUMBER_SPRITES[:]
number_sprites_player = NUMBER_SPRITES[:]
last_frame_time = 0

###FUNCTIONS###
def quadrant(b):
    '''returns the direction of the ball's heading (quadrant 1-4)'''
    if b.heading() > 0 and b.heading() < 90:
        return 1
    elif b.heading() > 90 and b.heading() < 180:
        return 2
    elif b.heading() > 180 and b.heading() < 270:
        return 3
    elif b.heading() > 270 and b.heading() < 360:
        return 4

###ARENA_PHYSICS_FUNCTIONS###
def arenaCollision(b):
    '''returns true if the ball hits the top or bottom of arena'''
    return (
    b.ycor() + BALL_HEIGHT >= ARENA_HEIGHT or 
    b.ycor() - BALL_HEIGHT <= -ARENA_HEIGHT
    )

def arenaReflectionAngle(q, b):
    '''returns the ball's reflection angle (for arena collisions)'''
    if q == 1:
        return b.heading() * 2
    elif q == 2:
        return 360 - b.heading() * 2
    elif q == 3:
        return (b.heading() - 180) * 2
    elif q == 4:
        return 720 - b.heading() * 2

def arenaReflections(b):
    '''enables collisions between the ball and the arena floor/cieling'''
    if arenaCollision(b):
        if quadrant(b) == 1 or quadrant(b) == 3:
            b.rt(arenaReflectionAngle(quadrant(b), b))
        else:
            b.lt(arenaReflectionAngle(quadrant(b), b))

###PADDLE_PHYSICS_FUNCTIONS###
def playerCollision(p, c, b):
    '''returns true if the ball collides with the player'''
    if b.ycor() + BALL_HEIGHT >= p.ycor() - PADDLE_HEIGHT and b.ycor() - BALL_HEIGHT <= p.ycor() + PADDLE_HEIGHT:
        if b.xcor() >= p.xcor() - PADDLE_WIDTH and b.xcor() <= p.xcor() + PADDLE_WIDTH:
            return True

def cpuCollision(p, c, b):
    '''returns true if the ball collides with the cpu'''
    if b.ycor() + BALL_HEIGHT >= c.ycor() - PADDLE_HEIGHT and b.ycor() - BALL_HEIGHT <= c.ycor() + PADDLE_HEIGHT:
        if b.xcor() >= c.xcor() - PADDLE_WIDTH and b.xcor() <= c.xcor() + PADDLE_WIDTH:
            return True

def frontOfPaddle(p, c, b):
    '''returns the distance between the ball and the inner edge of either paddle'''
    if b.xcor() < 0:
        return p.xcor() + PADDLE_WIDTH - 1
    else:
        return c.xcor() - PADDLE_WIDTH + 1

def pointUpOrDown(q, b):
    '''
    returns the angle that will make the ball turtle point straight up or down
    (whatever is closest) regardless of its original heading
    '''
    if q == 1:
        return 90 - b.heading()
    elif q == 2:
        return b.heading() - 90
    else:
        return b.heading() - 270

def paddleReflectionAngle():
    '''returns the ball's relfection angle (for paddle collisions)'''
    return random.randrange(35, 65)

def playerReflection(p, c, b):
    '''enables collisions between the ball and the player'''
    if playerCollision(p, c, b):
        b.setx(frontOfPaddle(p, c, b))
        if quadrant(b) == 2:
            b.rt(pointUpOrDown(quadrant(b), b))
            b.rt(paddleReflectionAngle())
        else:
            b.rt(pointUpOrDown(quadrant(b), b))
            b.lt(paddleReflectionAngle())

def cpuReflection(p, c, b):
    '''enables collisions between the ball and the cpu'''
    if cpuCollision(p, c, b):
        b.setx(frontOfPaddle(p, c, b))
        if quadrant(b) == 1:
            b.lt(pointUpOrDown(quadrant(b), b))
            b.lt(paddleReflectionAngle())
        else:
            b.rt(pointUpOrDown(quadrant(b), b))
            b.rt(paddleReflectionAngle())

###BALL_PHYSICS_FUNCTIONS###
def dynamicBallSpeed(p, c, b):
    '''
    increases ball speed after every collision with a paddle
    also resets ball speed if either paddle scores a goal
    '''
    global dynamic_ball_speed
    if playerCollision(p, c, b) or cpuCollision(p, c, b):
        dynamic_ball_speed = dynamic_ball_speed + BALL_ACCELERATION

    elif playerGoal(b) or cpuGoal(b):
        dynamic_ball_speed = BALL_SPEED

def ballBehaviour(p, c, b):
    '''enables ball physics and mechanics'''
    dynamicBallSpeed(p, c, b)
    serve(b)
    b.fd(dynamic_ball_speed)
    turtle.update()

###CPU_AI_FUNCTIONS###
def ballAboveCpu(c, b):
    '''return True if the ball is above the cpu'''
    if b.ycor() > c.ycor():
        return True

def ballBelowCpu(c, b):
    '''return True if the ball is below the cpu'''
    if b.ycor() < c.ycor():
        return True

def paddleBelowCieling(p):
    '''returns True if a paddle is below the arena cieling'''
    if p.ycor() + PADDLE_HEIGHT < ARENA_HEIGHT:
        return True

def paddleAboveFloor(p):
    '''returns True if a paddle is above the arena floor'''
    if p.ycor() - PADDLE_HEIGHT > -ARENA_HEIGHT:
        return True
    
def cpuLocomotion(c, b):
    '''
    moves the cpu up if the ball is above the cpu
    and down if the ball is below the cpu
    '''
    if b.ycor() != 0:
        if ballAboveCpu(c, b) and paddleBelowCieling(c):
            c.fd(CPU_SPEED)
        elif ballBelowCpu(c, b) and paddleAboveFloor(c):
            c.bk(CPU_SPEED)

###USER_INTERFACE_FUNCTIONS###
def paddleUp(p):
    '''moves a given paddle up'''
    p.fd(PLAYER_SPEED)

def paddleDown(p):
    '''moves a given paddle down'''
    p.fd(-PLAYER_SPEED)

def playerController(s, p):
    '''allows the use of keybindings to control the player's movement'''
    if paddleBelowCieling(p):
        turtle.onkeypress(partial(paddleUp, p), KEY_BINDINGS['player_up'])
    else:
        turtle.onkeypress(None, KEY_BINDINGS['player_up'])

    if paddleAboveFloor(p):
        turtle.onkeypress(partial(paddleDown, p), KEY_BINDINGS['player_down'])
    else:
        turtle.onkeypress(None, KEY_BINDINGS['player_down'])

    s.listen()

def player2Controller(s, c):
    '''allows the use of keybindings to control the cpu's movement'''
    if paddleBelowCieling(c):
        turtle.onkeypress(partial(paddleUp, c), KEY_BINDINGS['cpu_up'])
    else:
        turtle.onkeypress(None, KEY_BINDINGS['cpu_up'])

    if paddleAboveFloor(c):
        turtle.onkeypress(partial(paddleDown, c), KEY_BINDINGS['cpu_down'])
    else:
        turtle.onkeypress(None, KEY_BINDINGS['cpu_down'])

    s.listen()

def quitGame():
    '''closes the game window'''
    os._exit(0)

def exitOnEscape():
    '''closes the game window if the user presses the quit key (defined in keybindings)'''
    turtle.onkey(quitGame, KEY_BINDINGS["quit"])

###GAME_MECHANIC_FUNCTIONS###
def playerGoal(b):
    '''returns True if the ball has gone past the right side of the arena'''
    if b.xcor() - BALL_WIDTH > ARENA_WIDTH + PADDLE_WIDTH:
        return True

def cpuGoal(b):
    '''returns True if the ball has gone past the left side of the arena'''
    if b.xcor() + BALL_WIDTH < -ARENA_WIDTH - PADDLE_WIDTH:
        return True

def serve(b):
    '''resets ball position after a goal'''
    if playerGoal(b):
        b.home()
    elif cpuGoal(b):
        b.home()
        b.seth(180)

def scoreBoard(b, p_counter, c_counter):
    '''updates score sprite after every goal'''
    if playerGoal(b) and len(number_sprites_player) > 1:
        p_counter.shape(number_sprites_player.pop(1))

    elif cpuGoal(b) and len(number_sprites_cpu) > 1:
        c_counter.shape(number_sprites_cpu.pop(1))

def player1Wins():
    '''returns true if the player reaches the score limit'''
    if len(number_sprites_player) == len(NUMBER_SPRITES) - SCORE_LIMIT:
        return True

def player2Wins():
    '''returns true if the cpu reaches the score limit'''
    if len(number_sprites_cpu) == len(NUMBER_SPRITES) - SCORE_LIMIT:
        return True

def flashTurtle(w):
    '''displays a given turtle for 3 seconds'''
    w.showturtle()
    turtle.update()
    time.sleep(3)
    w.hideturtle()

def displayMultiplayerWinner(w):
    '''shows win message after a win (for multiplayer games)'''
    if player1Wins():
        w.shape(OBJECT_SPRITES['player1_win'])
    elif player2Wins():
        w.shape(OBJECT_SPRITES['player2_win'])
    
    flashTurtle(w)

def displaySingleplayerWinner(w):
    '''shows win message after win (for singleplayer games)'''
    if player1Wins():
        w.shape(OBJECT_SPRITES['winner'])
    else:
        w.shape(OBJECT_SPRITES['game_over'])

    flashTurtle(w)

def playSingleplayerWinAudio():
    '''plays audio after a win in a singleplayer game'''
    if player1Wins():
        playsound(SOUND_EFFECTS['win'], False)
    elif player2Wins():
        playsound(SOUND_EFFECTS['lose'], False)

def playMultiplayerWinAudio():
    '''plays audio after a win in a multiplayer game'''
    if player1Wins() or player2Wins():
        playsound(SOUND_EFFECTS['win'], False)

def resetPaddlePosition(p, c):
    '''sets paddle positions to zero'''
    p.sety(0)
    c.sety(0)

def unbindMultiplayerKeys():
    '''sets the keybindings to None for both paddles'''
    turtle.onkeypress(None, KEY_BINDINGS['player_up'])
    turtle.onkeypress(None, KEY_BINDINGS['player_down'])
    turtle.onkeypress(None, KEY_BINDINGS['cpu_up'])
    turtle.onkeypress(None, KEY_BINDINGS['cpu_down'])

def resetScoreBoard(p_counter, c_counter):
    '''sets the scoreboard sprites to zero'''
    p_counter.shape(NUMBER_SPRITES[0])
    c_counter.shape(NUMBER_SPRITES[0])

def resetScore():
    '''restores the sprite list which resets the score'''
    global number_sprites_player
    global number_sprites_cpu
    number_sprites_player = NUMBER_SPRITES[:]
    number_sprites_cpu = NUMBER_SPRITES[:]

def multiplayerWin(p, c, p_counter, c_counter, w):
    '''mechanics for multiplayer wins'''
    if player1Wins() or player2Wins():
        unbindMultiplayerKeys()
        resetPaddlePosition(p, c)
        playMultiplayerWinAudio()
        resetScoreBoard(p_counter, c_counter)
        displayMultiplayerWinner(w)
        resetScore()

def unbindSinglePlayerKeys():
    '''sets the keybindings to None for one paddle'''
    turtle.onkeypress(None, KEY_BINDINGS['player_up'])
    turtle.onkeypress(None, KEY_BINDINGS['player_down'])

def singleplayerWin(p, c, p_counter, c_counter, w):
    '''mechanics for singleplayer wins'''
    if player1Wins() or player2Wins():
        unbindSinglePlayerKeys()
        resetPaddlePosition(p, c)
        playSingleplayerWinAudio()
        resetScoreBoard(p_counter, c_counter)
        displaySingleplayerWinner(w)
        resetScore()
        
###AUDIO_FUNCTIONS###
def randomImpactSound():
    '''returns a random impact sound effect'''
    return random.choice(SOUND_EFFECTS['impacts'])

def soundEffects(p, c, b):
    '''handles gameloop sound effects'''
    if arenaCollision(b):
        playsound(randomImpactSound())

    elif playerCollision(p, c, b):
        playsound(SOUND_EFFECTS['boop'])

    elif cpuCollision(p, c, b):
        playsound(SOUND_EFFECTS['blip'])

    elif playerGoal(b):
        playsound(SOUND_EFFECTS['goal'])
    
    elif cpuGoal(b):
        playsound(SOUND_EFFECTS['fail'])

def randomSong():
    '''picks a random song and removes it from the playlist'''
    return playlist.pop(random.randrange(len(playlist)))

def playMusic():
    '''plays a random song from the playlist'''
    global playlist
    while True:
        playsound(randomSong())
        if len(playlist) == 0:
            playlist = MUSIC[:]

def playCoinSound():
    playsound(SOUND_EFFECTS['coin'])

###SETUP_FUNCTIONS###
def registerNumberSprites(s):
    for n in NUMBER_SPRITES:
        s.register_shape(n)

def registerCoinSprites(s):
    for c in COIN_SPRITES:
        s.register_shape(c)

def registerObjectSprites(s):
    for o in OBJECT_SPRITES.values():
        s.register_shape(o)

def createScreen():
    s = turtle.Screen()
    s.title('Pong')
    s.bgcolor('black')

    registerObjectSprites(s)
    registerNumberSprites(s)
    registerCoinSprites(s)
    return s

def createPlayer():
    p = turtle.Turtle()
    p.shape(OBJECT_SPRITES['paddle'])
    return p

def createPlayerScore():
    p_counter = turtle.Turtle()
    p_counter.shape(NUMBER_SPRITES[0])
    return p_counter

def createCpu():
    c = turtle.Turtle()
    c.shape(OBJECT_SPRITES['paddle'])
    return c

def setuCpuScore():
    c_counter = turtle.Turtle()
    c_counter.shape(NUMBER_SPRITES[0])
    return c_counter

def createBall():
    b = turtle.Turtle()
    b.shape(OBJECT_SPRITES['ball'])
    return b

def setupArena(p, c, b, p_counter, c_counter):
    '''sets the initial position of the game objects'''
    p.penup()
    p.setx(-ARENA_WIDTH + PADDLE_WIDTH * 2)
    p.lt(90)

    p_counter.penup()
    p_counter.setpos(-ARENA_WIDTH + 100, ARENA_HEIGHT - 75)
    p_counter.lt(180)

    c.penup()
    c.setx(ARENA_WIDTH - PADDLE_WIDTH * 2)
    c.lt(90)

    c_counter.penup()
    c_counter.setpos(ARENA_WIDTH - 100, ARENA_HEIGHT - 75)

    b.penup()

def createLine(color):
    '''creates a turtle for drawing arena lines'''
    l = turtle.Turtle()
    l.pensize(1)
    l.hideturtle()
    l.color(color)
    return l

def createCoins():
    '''creates turtle objects and assigns them coin graphics'''
    coin_turtles = []
    for c in COIN_SPRITES:
        coin = turtle.Turtle()
        coin.shape(c)
        coin.hideturtle()
        coin_turtles.append(coin)
    return coin_turtles

def removeCoins(*coin_turtles):
    '''hides and deletes all coins'''
    for c in coin_turtles:
        c.hideturtle()
        del c

def createWinBanner():
    '''creates a turtle for splash messages'''
    w = turtle.Turtle()
    w.hideturtle()
    return w

###DRAW_FUNCTIONS###
def drawBoundaryBox(l):
    '''draws the square with arena height and width'''
    l.penup()
    l.setpos(-ARENA_WIDTH, ARENA_HEIGHT)
    l.pendown()
    for _ in range(2):
        l.fd(ARENA_WIDTH * 2)
        l.rt(90)
        l.fd(ARENA_HEIGHT * 2)
        l.rt(90)

def drawArena():
    '''visualizes the arena borders'''
    l = createLine('black')
    drawBoundaryBox(l)
    del l

def drawFieldMarker():
    '''draws the arena divider'''
    l = createLine('white')
    l.penup()
    l.sety(-ARENA_HEIGHT)
    l.lt(90)
    while l.ycor() < ARENA_HEIGHT:
        l.pendown()
        l.fd(26)
        l.penup()
        l.fd(26)
    del l

###INTRO_ANIMATION_FUNCTIONS###
def playCoinAnimation(*coin_turtles):
    '''animates coin sprites'''
    for coin in coin_turtles:
        coin.showturtle()
        turtle.update()
        time.sleep(.1)
        coin.hideturtle()

###GAMELOOPS/MENU_FUNCTIONS###
def newGame(*coin_turtles):
    '''starts music and hides coin sprites'''
    playsound('sounds/slot.wav')
    removeCoins(*coin_turtles)
    song = threading.Thread(target=playMusic)
    song.start()

def baseGame(s, p, c, b, p_counter, c_counter, w):
    '''basic game physics and mechanics'''
    ballBehaviour(p, c, b)
    scoreBoard(b, p_counter, c_counter)
    sound_effects = threading.Thread(target=soundEffects, args=(p, c, b))
    sound_effects.start()
    playerReflection(p, c, b)
    cpuReflection(p, c, b)
    arenaReflections(b)
    exitOnEscape()

def singlePlayer(s, p, c, b, p_counter, c_counter, w, *coin_turtles):
    '''includes base game and functions specific to singleplayer'''
    turtle.onkey(None, KEY_BINDINGS['singleplayer'])
    newGame(*coin_turtles)
    LAST_FRAME_TIME = time.time()
    while True:
        current_time = time.time()
        baseGame(s, p, c, b, p_counter, c_counter, w)
        cpuLocomotion(c, b)
        playerController(s, p)
        singleplayerWin(p, c, p_counter, c_counter, w)
        elapsed_time = current_time - LAST_FRAME_TIME
        if (elapsed_time < FRAME_TIME_TARGET - elapsed_time):
            time.sleep(FRAME_TIME_TARGET - elapsed_time)
        LAST_FRAME_TIME = time.time()
        
def multiplayer(s, p, c, b, p_counter, c_counter, w, *coin_turtles):
    '''includes base game and functions specific to multiplayer'''
    turtle.onkey(None, KEY_BINDINGS['multiplayer'])
    newGame(*coin_turtles)
    LAST_FRAME_TIME = time.time()
    while True:
        current_time = time.time()
        baseGame(s, p, c, b, p_counter, c_counter, w)
        playerController(s, p)
        player2Controller(s, c)
        multiplayerWin(p, c, p_counter, c_counter, w)
        elapsed_time = current_time - LAST_FRAME_TIME
        if (elapsed_time < FRAME_TIME_TARGET - elapsed_time):
            time.sleep(FRAME_TIME_TARGET - elapsed_time)
        LAST_FRAME_TIME = time.time()
        
def titleScreen(s, p, c, b, p_counter, c_counter, w, coin_turtles):
    '''intro screen, plays animation and allows the user to select game-modes'''
    while True:
        turtle.onkey(partial(singlePlayer, s, p, c, b, p_counter, c_counter, w, *coin_turtles), KEY_BINDINGS['singleplayer'])
        turtle.onkey(partial(multiplayer, s, p, c, b, p_counter, c_counter, w, *coin_turtles), KEY_BINDINGS['multiplayer'])
        s.listen()
        playCoinAnimation(*coin_turtles)
        playCoinSound()
        exitOnEscape()

def main():
    turtle.tracer(0, 0)
    drawArena()
    drawFieldMarker()
    screen = createScreen()
    ball = createBall()
    player = createPlayer()
    player_score = createPlayerScore()
    cpu = createCpu()
    cpu_score = setuCpuScore()
    coin_turtles = createCoins()
    win_banner = createWinBanner()
    setupArena(player, cpu, ball, player_score, cpu_score)

    turtle.update()

    titleScreen(screen, player, cpu, ball, player_score, cpu_score, win_banner, coin_turtles)

main()
