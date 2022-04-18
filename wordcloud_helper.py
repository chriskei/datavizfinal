from wordcloud import WordCloud
import matplotlib.pyplot as plt

# generates a wordcloud given dataframe and category and saves it assets folder for dash server 
# returns image name
def generate_wordcloud(df, category: str):
    text = ''
    index = str(df.index[0]) # workaround to image not updating is renaming it, fix
    file_name = "artist_wordcloud" + index + ".png"
    path = "assets/" + file_name
    for word in df[category]:
        text += str(word).replace("'", "").replace(" ", "")
    wordcloud = WordCloud(width=500, height=500, 
        background_color=None,
        mode = "RGBA",
        collocation_threshold=30, 
        relative_scaling=1).generate(text)

    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)   
    plt.axis("off")
    plt.tight_layout(pad = 0)
    plt.savefig(path)

    return file_name

