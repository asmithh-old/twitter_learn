import theanets, tweepy, csv, time, ast, numpy as np, random, os.path

consumer_key = 'foo'
consumer_secret = 'foo'
access_token = 'foo'
access_token_secret = 'foo'
keywords = ['female,females', 'woman,women', 'girl,girls', 'man,men', 'male,males', 'boy,boys']
keywords_ban = set(['female','females', 'woman','women', 'girl','girls', 'man','men', 'male','males', 'boy','boys'])
def get_tweets(ckey, csecret, atoken, asecret, keywords):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    tweets_by_keyword = {}
    with open('gender_tweets_3.csv', 'w') as f:
        #time.sleep(900)
        for i in range(48):
            print 'starting iteration ' + str(i)
            for keyword in keywords:
                tweets = []
                f.write(str(keyword))
                f.write(str([tweet.text for tweet in tweepy.Cursor(api.search, q = keyword, result_type = "recent", include_entities = True, lang = "en").items(100)]))
                f.write('\n')
            print 'wrote iteration ' + str(i) + ' of 15 successfully.'
            print
            time.sleep(950)
        f.close()
#get_tweets(consumer_key, consumer_secret, access_token, access_token_secret, keywords)

def clean():
    with open(os.path.expanduser('~/Desktop/steak/gender_tweets_2.csv')) as f:
        tweets = {i:[] for i in range(len(keywords))}
        freq = {i:dict() for i in range(len(keywords))}
        num_words = {i:0 for i in range(len(keywords))}
        content = f.readlines()
        for line in content:
            b = line.split('[', 1)
            tweets[keywords.index(b[0])] += ast.literal_eval('[' + b[1])
        f.close()
    tweets_cleaner = {}
    for k in tweets.keys():
        tweets_cleaner[k] = []
        for t in tweets[k]:
            tweet_split = {}
            for i in t.split(' '):
                print len(i)
                if len(i) > 0 and (i[0] == '@' or i == 'RT' or (len(i) > 2 and i[0:3] == 'http') or i[0] == '#'):
                    pass
                elif i in keywords_ban:
                    pass
                else:
                    num_words[k] += 1
                    if i in freq[k]:
                        freq[k][i] += 1
                    else:
                        freq[k][i] = 1
                    tweet_split[i] = True
            tweets_cleaner[k].append(tweet_split)
    all_words_set = set()
    for k in tweets.keys():
        freq[k] = {w: float(freq[k][w])/float(num_words[k]) for w in freq[k].keys()}
        for i in freq[k].keys():
            all_words_set.add(i)
    valid = set()
    nonindicative = 0
    for w in list(all_words_set):
        b = [freq[k][w] if w in freq[k] else 0 for k in range(len(keywords))]
        avg = np.sum(b)/float(len(keywords))
        if avg < 0.00001:
            print 'rare', w
        elif np.sum([(i-avg)**2 for i in b])/float(len(keywords)) < 0.00000001:
            print 'non-indicative', w
            nonindicative += 1
        else:
            valid.add(w)
        #TODO: if variance/stddev of this list is too low, kick out the words.
        #if word is very rare singleton, kick it out.
    valid = sorted(list(valid))
    print len(valid)
    matrix = []
    for k in tweets_cleaner.keys():
        if k == 0 or k == 1 or k == 2:
            l = 0
        elif k == 3 or k == 4 or k == 5:
            l = 1
        for t in tweets_cleaner[k]:
            s = np.zeros(len(valid))
            for w in t.keys():
                if w in valid:
                    s[valid.index(w)] = 1
            matrix.append((l, s))
    return (matrix, valid)
(matrix, valid) = clean()
def neural_net():
    random.shuffle(matrix)
    train = ([m[1] for m in matrix[:int(0.8*len(matrix))]], [m[0] for m in matrix[:int(0.8*len(matrix))]])
    validate = [m[1] for m in matrix[int(0.8*len(matrix)):]], [m[0] for m in matrix[int(0.8*len(matrix)):]]
    net = theanets.feedforward.Classifier(layers=[len(valid), 500, 6])
    print net.score(train[0], train[1], w = None)
