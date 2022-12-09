
import numpy as np
import pandas as pd
from flask import Flask,render_template,request

books = pd.read_csv('Books.csv',low_memory=False)
users = pd.read_csv('Users.csv',low_memory=False)
ratings = pd.read_csv('Ratings.csv',low_memory=False)

books['Book-Title'].nunique()
Book_Count_df=pd.DataFrame(books['Book-Title'].value_counts())
Book_Count_df.reset_index(inplace=True)
Book_Count_df.rename(columns={'index':'Book-Title','Book-Title':'Count'})
User_Rating_Count=pd.DataFrame(ratings['User-ID'].value_counts())
User_Rating_Count.reset_index(inplace=True)
User_Rating_Count.rename(columns={'index':'User-ID','User-ID':'Count'},inplace=True)
ratings_with_name = ratings.merge(books,on='ISBN')
num_rating_df = ratings_with_name.groupby('Book-Title').count()['Book-Rating'].reset_index()
num_rating_df.rename(columns={'Book-Rating':'num_ratings'},inplace=True)
avg_rating_df = ratings_with_name.groupby('Book-Title').mean()['Book-Rating'].reset_index()
avg_rating_df.rename(columns={'Book-Rating':'avg_rating'},inplace=True)
popular_df = num_rating_df.merge(avg_rating_df,on='Book-Title')
popular_df = popular_df[popular_df['num_ratings']>=250].sort_values('avg_rating',ascending=False).head(50)
popular_df = popular_df.merge(books,on='Book-Title').drop_duplicates('Book-Title')[['Book-Title','Book-Author','Image-URL-M','num_ratings','avg_rating']]
popular_df['Image-URL-M'][0]
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_colwidth', 1000)
x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
wellread_users = x[x].index
filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(wellread_users)]
y = filtered_rating.groupby('Book-Title').count()['Book-Rating']>=40
famous_books = y[y].index
final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]
pt = final_ratings.pivot_table(index='Book-Title',columns='User-ID',values='Book-Rating')
pt.isna().sum()
pt.fillna(0,inplace=True)
from sklearn.metrics.pairwise import cosine_similarity
similarity_scores = cosine_similarity(pt)

def recommend(book_name):
    # index fetch
    index = np.where(pt.index==book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])),key=lambda x:x[1],reverse=True)[1:6]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)
    return data

app = Flask(__name__)
app.secret_key = "secret"

@app.route('/',methods = ['GET','POST'])
def index():
    return render_template("mi.html")
#  ,, 
@app.route('/server',methods = ['GET','POST'])
def server():
    if request.method == "POST":
        book = request.form['reco']
        print(book)
        data = recommend(book)
        return render_template("mi.html",data = data)

app.run(debug = True)