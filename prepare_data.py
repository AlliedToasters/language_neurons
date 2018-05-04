import pandas as pd
import os
import re
import sys

def update_progress(progress):
    """Displays or updates a console progress bar
    Accepts a float between 0 and 1. Any int will be converted to a float.
    A value under 0 represents a 'halt'.
    A value at 1 or bigger represents 100%
    """
    barLength = 25 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100, 3), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def get_text(idx, df=df):
    """Takes idx and df and returns text."""
    path = df.loc[idx].path
    with open(path, 'r') as f:
        result = f.read()
    return result

def remove_tags(input_string):
    result = input_string
    tag = re.compile(r'<[^<]*>')
    while tag.search(result):
        match = tag.search(result)
        strt = match.span()[0]
        stp = match.span()[1]
        result = result[:strt] + result[stp:]
    return result

if __name__ in '__main__':
    cols = ['lang', 'path']
    df = pd.DataFrame(columns=cols)

    languages = os.popen('ls ./data/txt/').read().split('\n')[:-1]
    for lang in languages:
        print('adding language {}...'.format(lang))
        lang_frame = pd.DataFrame(columns=cols)
        txts = os.popen('ls ./data/txt/{}/'.format(lang)).read().split('\n')[:-1]
        paths = ['./data/txt/{}/{}'.format(lang, txt) for txt in txts]
        lang_frame['path'] = paths
        lang_frame['lang'] = lang
        lang_frame.index = range(len(df), len(df)+len(lang_frame))
        df = pd.concat([df, lang_frame], axis=0)

    #one bad file: ./data/txt/pl/ep-09-10-22-009.txt

    #withold some fraction from every class for validation.
    test_prop = .05
    test = pd.DataFrame(columns=cols)
    for lang in df.lang.unique():
        samp = df[df.lang == lang].sample(frac=test_prop, random_state=0)
        test = pd.concat([test, samp])

    train = df[~df.index.isin(test.index)]
    print('documents in training set: ', len(train))
    print('documents in validation set: ', len(test))

    train_path = './data/train.txt'
    val_path = './data/val.txt'
    os.system('rm {} {}'.format(train_path, val_path))

    cnt = 0
    txt = ''
    print('creating validation file...')
    shuffle = train.sample(frac=1)
    for i, row in shuffle.iterrows():
        try:
            new_txt = get_text(i, df=train)
        except UnicodeDecodeError:
            print('decode problem at: {}'.format(i))
            print('language: ', row.lang)
            pass
        new_txt = remove_tags(new_txt)
        txt = txt + new_txt
        cnt += 1
        prog = cnt/len(train)
        update_progress(prog)

    print('characters in train txt:', len(txt))
    with open(train_path, 'w+') as f:
            f.write(txt)
    print('train file saved at: ', train_path)

    del txt

    cnt = 0
    txt = ''
    print('creating validation file...')
    shuffle = test.sample(frac=1)
    for i, row in shuffle.iterrows():
        try:
            new_txt = get_text(i, df=test)
        except UnicodeDecodeError:
            print('decode problem at: {}'.format(i))
            print('language: ', row.lang)
            pass
        new_txt = remove_tags(new_txt)
        txt = txt + new_txt
        cnt += 1
        prog = cnt/len(test)
        update_progress(prog)

    print('characters in validation txt:', len(txt))
    with open(val_path, 'w+') as f:
            f.write(txt)
    print('validation file saved at: ', val_path)

    del txt