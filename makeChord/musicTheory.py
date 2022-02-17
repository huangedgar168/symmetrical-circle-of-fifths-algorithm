'''
    Coded by Song Jia-Qi, 2020
'''

import music21
import json
import random

rhythm = []
chord = {}

with open('./musicTheory/rythem.json','r') as _:
    rythem = json.loads(_.read())

with open('./musicTheory/chord.json','r') as _:
    chord = json.loads(_.read())

def combineRhythm(beats:int=1):
    '''
        以隨機的方式產生出節奏
    '''
    combList = []
    while beats > 0:
        randList1 = random.choice(rythem)
        if len(randList1)==0:
            continue
        randList2 = random.choice(randList1)
        combList = combList + randList2
        beats -= rythem.index(randList1)
    return combList

def showChord(chordPattern):
    chord = music21.chord.Chord([i for i in range(12) if chordPattern[i]])
    print(chord)

def moveChordPattern(chordPattern, way='fifth'):
    if way == 'fifth':
        return chordPattern[-7:] + chordPattern[:-7]
    elif way == 'forth':
        return chordPattern[-5:] + chordPattern[:-5]
    elif way == 'halftone':
        return chordPattern[1:] + chordPattern[:1]
    elif way == 'halftone-down':
        return chordPattern[-1:] + chordPattern[:-1]
    else:
        return chordPattern[-int(way)%12:] + chordPattern[:-int(way)%12]

def chordPatternMatch(chordPattern, noteCount):
    #showChord(chordPattern)
    sum = 0
    for i in range(12):
        #print((noteCount[i]), (chordPattern[i]))
        if chordPattern[i]:
            sum += noteCount[i]
    return sum


def makeChord(notes, quarterLengt=2, key=None, way='symmetrical-fifth'):
    '''
    依照給定的音符序列找出適當的和弦
    
    Parameters
    ---
    notes:
        由 music21.note.Note 組成的序列。

    key:
        指定調性，若無設定則自行判斷。
        調性會影響到主音的位置與和弦判斷的順序。

    quarterLengt:
        指定和弦的持續長度，預設為 2 拍
    
    way:
        巡迴的方式。可選擇上五度（'fifth'）、下五度（'forth'）、上半音（'halftone'）、下半音（'halftone-down'）、
        對稱五度（'symmetrical-fifth'，預設值）、逆對稱五度（'anti-symmetrical-fifth'）。
        前四項分別可用 7, 5, 11, 1 表示。其他數字不會判斷到所有和弦。
    
    Returns
    ---
    newChord:
        依照判斷結果生成出來的和弦。
    '''
    # 計算該片段中每個音出現的次數
    countNote = [0 for _ in range(12)]
    for note in notes:
        if isinstance(note, music21.note.Note):
            countNote[int(note.pitch.ps)%12] += 1
    
    # 引入各種 chordPattern
    major = [(i in chord['Maj']) for i in range(12)]
    minor = [(i in chord['Min']) for i in range(12)]
    dim = [(i in chord['Dim']) for i in range(12)]
    arg = [(i in chord['Arg']) for i in range(12)]
    dom7 = [(i in chord['Dom7']) for i in range(12)]
    dim7 = [(i in chord['Dim7']) for i in range(12)]
    maj7 = [(i in chord['Maj7']) for i in range(12)]
    
    # 判斷的順序，越前面優先權越高
    chordPatternSequrence = [major[:], minor[:], dim[:]]

    if key == None:
        key = music21.analysis.discrete.analyzeStream(music21.stream.Stream(notes), 'key')
    elif isinstance(key, music21.key.Key):
        pass
    else:
        key = music21.key.Key(key)
    '''
        key.tonic: 找主音
        key.mode:  找調性

        key.tonic.ps: 主音的絕對音高
    '''
    # 將 chordPattern 移動到主音的位置
    nextChordGroup = []
    for chordPattern in chordPatternSequrence:
        nextChordGroup.append(moveChordPattern(chordPattern, way=key.tonic.ps))
    chordPatternSequrence = nextChordGroup

    # 若判斷為大調則優先判斷大和弦，否則優先判斷小和弦（原本的順序為 [maj, min, ...]）
    if key.mode == 'minor':
        chordPatternSequrence[0], chordPatternSequrence[1] = chordPatternSequrence[1][:], chordPatternSequrence[0][:]
    
    currChord = None
    max = 0

    # 利用 chordPattern 做比對，取與片段吻合最多的 chordPattern 作為搭配的和弦
    # chordPattern 循環模式包含上五度（'fifth'）、下五度（'forth'）、上半音（'halftone'）、下半音（'halftone-down'）、對稱五度（'symmetrical-fifth'）

    if way == 'symmetrical-fifth':
        toUp = [moveChordPattern(chordPattern[:]) for chordPattern in chordPatternSequrence]
        toDown = [chordPattern[:] for chordPattern in chordPatternSequrence]
        for _ in range(6):
            sum = 0
            nextChordGroup = []
            for chordPattern in toDown:
                sum = chordPatternMatch(chordPattern, countNote)
                if sum > max:
                    max = sum
                    currChord = chordPattern[:]
                nextChordGroup.append(moveChordPattern(chordPattern, way='forth'))
            toDown = nextChordGroup[:]

            sum = 0
            nextChordGroup = []
            for chordPattern in toUp:
                sum = chordPatternMatch(chordPattern, countNote)
                if sum > max:
                    max = sum
                    currChord = chordPattern[:]
                nextChordGroup.append(moveChordPattern(chordPattern, way='fifth'))
            toUp = nextChordGroup[:]

    elif way == 'anti-symmetrical-fifth':
        toDown = [moveChordPattern(chordPattern[:]) for chordPattern in chordPatternSequrence]
        toUp = [chordPattern[:] for chordPattern in chordPatternSequrence]
        for _ in range(6):
            sum = 0
            nextChordGroup = []
            for chordPattern in toUp:
                sum = chordPatternMatch(chordPattern, countNote)
                if sum > max:
                    max = sum
                    currChord = chordPattern[:]
                nextChordGroup.append(moveChordPattern(chordPattern, way='fifth'))
            toUp = nextChordGroup[:]

            sum = 0
            nextChordGroup = []
            for chordPattern in toDown:
                sum = chordPatternMatch(chordPattern, countNote)
                if sum > max:
                    max = sum
                    currChord = chordPattern[:]
                nextChordGroup.append(moveChordPattern(chordPattern, way='forth'))
            toDown = nextChordGroup[:]

            
    else:
        for _ in range(12):
            nextChordGroup = []
            for chordPattern in chordPatternSequrence:
                sum = chordPatternMatch(chordPattern, countNote)
                if sum > max:
                    max = sum
                    currChord = chordPattern[:]
                nextChordGroup.append(moveChordPattern(chordPattern, way=way))
            chordPatternSequrence = nextChordGroup[:]
    
    newChord = music21.chord.Chord([music21.note.Note(i, octave=3) for i in range(12) if currChord[i] == True], quarterLength=quarterLengt)
    return newChord
