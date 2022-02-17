try:
    import music21
    from music21.converter import ConverterException
except ModuleNotFoundError as e:
        if e.msg == "No module named 'music21'":
            print('Module "music21" has not been installed, install now? (Y,N)')
            c = input()
            if c == 'Y' or c == 'y':
                os.system('pip install music21')
                import music21
                from music21.converter import ConverterException
            else:
                raise e
        else:
            raise e

import musicTheory

from sys import argv
import os

usage=f'''
Usage: makeChord.py <path>
'''

def cml_interface():
    try:
        file_path = argv[1]
        make_chord_sequence_demo(file_path)
    except IndexError:
        print(usage)
        exit()
    except ConverterException:
        print(f'File "{file_path}" not found.')

    

def make_chord_sequence_demo(filepath, range_length=2, save=True):
    '''將指定的樂譜檔案作範例，展現出所有不同的和聲樣式的生成結果
    
    若要用一般的和弦生成，用 `make_chord_sequence`。

    Parameters
    ---
    filepath:
        檔案路徑。

    range_length:
        將旋律分割的四分音符長度單位。

    save:
        是否要存檔，將會存檔成 mxl。
        存檔路徑與原檔案路徑位置一樣，且在附檔名前加 "_output" 的字樣。

    Tips
    ---
    本程式不會對音樂記譜法的正確性做檢查。
    '''
    # 讀檔，並擷取資料
    score = music21.converter.parse(filepath)
    part = score.recurse().parts[0]
    notes = part.recurse().notes
    key = music21.analysis.discrete.analyzeStream(score, 'key')
    max_offset = int(notes[-1].offset)  # 合理假設最後一個音的 offset 最大

    # demo 模式
    ways = [('halftone','ht'), ('halftone-down','hd'), ('fifth','5th'), ('forth','4th'), ('symmetrical-fifth','sm5'), ('anti-symmetrical-fifth','as5')]

    for way in ways:
        # 設定新 part 資訊
        chord_part = music21.stream.Part()
        instrument = music21.instrument.Piano()
        instrument.partName, instrument.partAbbreviation = way        
        chord_part.insert(0, instrument)
        chord_part.insert(0, key)
        for i in range(0, max_offset + 1, range_length):
            melody = [note for note in notes if note.offset >= i and note.offset < i + range_length]
            chord = musicTheory.makeChord(melody, range_length, key)
            chord_part.insert(i, chord)
        score.insert(0, chord_part)

    score.show()
    
    if save:
        fname = filepath.split('.')[0]
        fname = fname + '_output.mxl'
        score.write('mxl', fp=fname)

def make_chord_sequence(filepath, range_length=2, way='symmetrical-fifth', show=False, save=True):
    '''將指定的樂譜檔案作範例，依指定和聲樣式循環的生成結果
    
    Parameters
    ---
    filepath:
        檔案路徑。

    range_length:
        將旋律分割的四分音符長度的區間單位。

    way:
        指定的循環模式，提供 6 種：\n
            上五度（'fifth'）\n
            下五度（'forth'）\n
            上半音（'halftone'） \n
            下半音（'halftone-down'）\n
            對稱五度（'symmetrical-fifth'，預設值）\n
            逆對稱五度（'anti-symmetrical-fifth'，預設值）\n

    show:
        設定是否要檢視生成結果。

    save:
        是否要存檔，將會存檔成 mxl。
        存檔路徑與原檔案路徑位置一樣，且在附檔名前加 "_output" 的字樣。

    Tips
    ---
    本程式不會對音樂記譜法的正確性做檢查。
    '''
    # 讀檔，並擷取資料
    score = music21.converter.parse(filepath)
    part = score.recurse().parts[0]
    notes = part.recurse().notes
    key = music21.analysis.discrete.analyzeStream(score, 'key')
    max_offset = int(notes[-1].offset)  # 合理假設最後一個音的 offset 最大

    # demo 模式
    ways = [('halftone','ht'), ('halftone-down','hd'), ('fifth','5th'), ('forth','4th'), ('symmetrical-fifth','sm5'), ('anti-symmetrical-fifth','as5')]
    
    # 設定新 part 資訊
    chord_part = music21.stream.Part()
    instrument = music21.instrument.Piano()      
    chord_part.insert(0, instrument)
    chord_part.insert(0, key)

    # 在每個區間單位中判斷適合的和弦
    for i in range(0, max_offset + 1, range_length):
        melody = [note for note in notes if note.offset >= i and note.offset < i + range_length]
        chord = musicTheory.makeChord(melody, range_length, key, way)
        chord_part.insert(i, chord)
    
    # 添加到舊的 score 裡後顯示（第三方軟體）
    score.insert(0, chord_part)
    return score

if __name__ == '__main__':
    cml_interface()