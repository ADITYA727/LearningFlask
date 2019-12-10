from flask import Flask,render_template,url_for,request, redirect, Response
import json
import tweepy
import re
import os
import tablib
import sys
import csv
import glob
import pandas as pd
import random


app = Flask(__name__)

def clean_tweet(tweet):
    tweet = re.sub('http\S+\s*', '', tweet)  # remove URLs
    tweet = re.sub('RT|cc', '', tweet)  # remove RT and cc
    tweet = re.sub('#\S+', '', tweet)  # remove hashtags
    tweet = re.sub('@\S+', '', tweet)  # remove mentions
    tweet = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), '', tweet)  # remove punctuations
    tweet = re.sub('\s+', ' ', tweet)  # remove extra whitespace
    return tweet








@app.route('/')
def main():
    return render_template('index.html')


@app.route('/naves_bayes')
def naves_bayes():
    return render_template('naves_bayes.html')


    


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
        config = json.loads(open('credential.json').read())
        if(str(username) == config['username'] and str(password) == config['password']):
            return redirect('/')
          
        else:
            message = "username and password not correct"
            return render_template('login.html', message=message)

    return render_template('login.html')


@app.route('/logout')
def logout():
    return redirect('/login')            












#########################################Scrap From Tweeter########################################################

@app.route('/scrap_home')
def scrap_home():
    csv_list = os.listdir('./scrap_data')
    csv_mix = os.listdir('./data')
    return render_template('scrap_data.html', csv_list = csv_list, csv_mix=csv_mix)

@app.route('/scrap_data', methods = ['GET', 'POST'])
def scrap_data():
    if request.method == 'POST':
        enter_number_of_tweets = request.form['number']
        hashtag = request.form['hashtag']
        auth = tweepy.OAuthHandler("mJ2fluR2xOZaj5byk68urYhRl", "c0lmSii3lq436Oh9Lyp2vsIkxj2fLMTVaCfVbi8xoX1L6kXJJ2")
        auth.set_access_token("1048889324052275200-hVDEZ5I7L7wQLx2KclPnACpj982rcx", "eI7pR91fjbVSrGNVGRUbd6CEVEIp82rkUMmiPhH9xlK5j")
        api = tweepy.API(auth)
        with open('./scrap_data/'+ hashtag + '.csv', 'w+', newline='') as tweet_text:
            import csv
            fieldnames = ['tweets', 'tagname']
            writer = csv.DictWriter(tweet_text, fieldnames=fieldnames)
            writer.writeheader()
            for tweet in tweepy.Cursor(api.search, q = '#' + hashtag, rpp = 100).items(int(enter_number_of_tweets)):
                clean_text = tweet.text
                emoji_clear_data = clean_text.encode('ascii', 'ignore').decode('ascii')
                cleared_data = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",emoji_clear_data).split())
                cleared_data = ''.join([i for i in cleared_data if not i.isdigit()])
                data = clean_tweet(cleared_data)
                if data != '':
                    writer.writerow({'tweets': str(data.encode('utf-8').decode()), 'tagname': hashtag})
        print('Extracted ' + str(enter_number_of_tweets) + ' tweets with hashtag #' + hashtag)
      
    return redirect('/scrap_home')

@app.route('/csv_read/<name_file>')
def csv_read(name_file):
    os.chdir('./scrap_data')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                dataset.csv = f.read()
        else:
            pass
    os.chdir('../')        
    return dataset.html


@app.route('/csv_delete/<name_file>')
def csv_delete(name_file):
    os.chdir('./scrap_data')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            os.remove(name_file)
            csv_list = os.listdir()
            print(csv_list)
        else:
            pass
    os.chdir('../')   
    
    return redirect('/scrap_home')  


@app.route("/csv_download/<name_file>")
def csv_download(name_file):
    os.chdir('./scrap_data')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                csv = dataset.csv = f.read()
        else:
            pass
    os.chdir('../')        
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":"attachment; filename = "+ name_file})    


@app.route('/mix_all_csv')
def mix_all_csv():
    all_tweet = ''
    os.chdir('./scrap_data')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    for name_file in csv_list:
        df = pd.read_csv(name_file)
        #out = df.append(df)
        out = pd.concat([df], axis=0, join='outer', ignore_index=True)
        with open('../data/result.csv', 'a+', encoding='utf-8') as f:
            out.to_csv(f, index=False)
    os.chdir('../')                
    return redirect('/scrap_home') 




@app.route('/mix_csv_read/<name_file>')
def mix_csv_read(name_file):
    os.chdir('./data')
    csv_dir =  os.getcwd()
    print(csv_dir)
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                dataset.csv = f.read()
        else:
            pass
    os.chdir('../')        
    return dataset.html 



@app.route('/mix_csv_delete/<name_file>')
def mix_csv_delete(name_file):
    os.chdir('./data')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            os.remove(name_file)
            csv_list = os.listdir()
            print(csv_list)
        else:
            pass
    os.chdir('../')   
    
    return redirect('/scrap_home') 


@app.route("/mix_csv_download/<name_file>")
def mix_csv_download(name_file):
    os.chdir('./data')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                csv = dataset.csv = f.read()
        else:
            pass
    os.chdir('../')        
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":"attachment; filename = "+ name_file})                    
 









############## fake tweets #####################################################################################



@app.route('/generate_fake_tweets_home')
def generate_fake_tweets_home():
    csv_list = os.listdir('./fake_data_tweets/fake_tweets')
    csv_mix = os.listdir('./fake_data_tweets/fake_mix_tweets')
    return render_template('generate_fake_tweets.html', csv_list=csv_list, csv_mix=csv_mix)


@app.route('/generate_fake_tweets', methods = ['GET', 'POST'])
def generate_fake_tweets():
    if request.method == 'POST':
        import csv
        enter_number_of_tweets = request.form['number']
        hashtag = request.form['hashtag']
        f = open('./fake_data_tweets/fake_tweets/'+ hashtag + '.csv', 'w+', newline='')
        fieldnames = ['tweets', 'tagname']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        f_nouns =  open('./fake_data_tweets/generate_fake_tweets/nouns.txt','r')
        f_verbs =  open('./fake_data_tweets/generate_fake_tweets/verbs.txt','r')
        f_adverb =  open('./fake_data_tweets/generate_fake_tweets/adverb.txt','r')
        f_adjective =  open('./fake_data_tweets/generate_fake_tweets/adjective.txt','r')
        f_nouns = f_nouns.read()
        f_verbs = f_verbs.read()
        f_adverb = f_adverb.read()
        f_adjective = f_adjective.read()
        f_nouns_list = f_nouns.split('\n')
        f_verbs_list = f_verbs.split('\n')
        f_adverb_list = f_adverb.split('\n')
        f_adjective_list = f_adjective.split('\n')
        for i in range(0, int(enter_number_of_tweets)):
            num = random.randrange(0,5)
            tweets_data = f_nouns_list[num] + ' ' + f_verbs_list[num] + ' ' + f_adverb_list[num] + ' ' + f_adjective_list[num]
            data = clean_tweet(tweets_data)
            print(data)
            writer.writerow({'tweets': str(data.encode('utf-8').decode()), 'tagname': hashtag})
        f.close()  
    return redirect('/generate_fake_tweets_home')


@app.route('/fake_csv_read/<name_file>')
def fake_csv_read(name_file):
    os.chdir('./fake_data_tweets/fake_tweets')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(name_file)
    print(csv_list,'########')
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                dataset.csv = f.read()
        else:
            pass
    os.chdir('../../')        
    return dataset.html 



@app.route('/fake_csv_delete/<name_file>')
def fake_csv_delete(name_file):
    os.chdir('./fake_data_tweets/fake_tweets')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            os.remove(name_file)
            csv_list = os.listdir()
            print(csv_list)
        else:
            pass
    os.chdir('../../')   
    
    return redirect('/generate_fake_tweets_home') 



@app.route("/fake_csv_download/<name_file>")
def fake_csv_download(name_file):
    os.chdir('./fake_data_tweets/fake_tweets')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                csv = dataset.csv = f.read()
        else:
            pass
    os.chdir('../../')        
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":"attachment; filename = "+ name_file})
  


@app.route('/fake_mix_all_csv')
def fake_mix_all_csv():
    os.chdir('./fake_data_tweets/fake_tweets')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list,'##########')
    for name_file in csv_list:
        df = pd.read_csv(name_file)
        #out = df.append(df)
        out = pd.concat([df], axis=0, join='outer', ignore_index=True)
        with open('../../fake_data_tweets/fake_mix_tweets/fake_mix_result.csv', 'a+', encoding='utf-8') as f:
            out.to_csv(f, index=False)
    os.chdir('../../')                
    return redirect('/generate_fake_tweets_home') 



@app.route('/fake_mix_csv_read/<name_file>')
def fake_mix_csv_read(name_file):

    os.chdir('./fake_data_tweets/fake_mix_tweets')
    csv_dir =  os.getcwd()
    print(csv_dir)
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                dataset.csv = f.read()
        else:
            pass
    os.chdir('../../')        
    return dataset.html 



@app.route('/fake_mix_csv_delete/<name_file>')
def fake_mix_csv_delete(name_file):
    os.chdir('./fake_data_tweets/fake_mix_tweets')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            os.remove(name_file)
            csv_list = os.listdir()
            print(csv_list)
        else:
            pass
    os.chdir('../../')   
    
    return redirect('/generate_fake_tweets_home') 


@app.route("/fake_mix_csv_download/<name_file>")
def fake_mix_csv_download(name_file):
    os.chdir('./fake_data_tweets/fake_mix_tweets')
    csv_dir =  os.getcwd()
    csv_list = os.listdir()
    print(csv_list)
    for i in csv_list:
        if name_file == i:
            dataset = tablib.Dataset()
            with open(csv_dir+"/" +name_file, "r") as f:
                csv = dataset.csv = f.read()
        else:
            pass
    os.chdir('../../')        
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":"attachment; filename = "+ name_file})           










if __name__ == '__main__':
    app.run(debug=True)




















