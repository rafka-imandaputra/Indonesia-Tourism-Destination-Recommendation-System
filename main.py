# import library
import pandas as pd
import folium
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# preparing dataset
url = 'https://drive.google.com/file/d/1wNh4iGiRg3nTTqujcbN8pix5ZgJZfZKf/view?usp=sharing'
url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
df = pd.read_csv(url)

# processing dataframe
data_content_based_filtering = df.copy()
data_content_based_filtering['Tags'] = data_content_based_filtering['Category_en'] + ' ' + data_content_based_filtering['Description_en']
data_content_based_filtering = data_content_based_filtering[['Place_Id', 'Place_Name', 'Tags', 'Category_en', 'City','Description_en', 'Lat', 'Long','Rating','Price']]

# process cosine similarity
tv = TfidfVectorizer(max_features=5000)
vectors = tv.fit_transform(data_content_based_filtering.Tags).toarray()
similarity = cosine_similarity(vectors)

# define output
m = folium.Map(location=[-7.229360, 109.371727],  zoom_start=7)
fmt = ""


# Create a function that will return the name of the recommended tourist spot to the user
def recommend_by_content_based_filtering(place_key, place_city, place_number):
    data_preferred = data_content_based_filtering[data_content_based_filtering['Category_en']==place_key].sample(1).values[0][1]
    place_key_index = data_content_based_filtering[data_content_based_filtering['Place_Name']==data_preferred].index[0]
    distancess = similarity[place_key_index]
    place_key_list = sorted(list(enumerate(distancess)), key=lambda x: x[1], reverse=True)[1:100]

    recommended_place_keys = []
    for i in place_key_list:
        if data_content_based_filtering.iloc[i[0]].City == place_city:
            recommended_place_keys.append([data_content_based_filtering.iloc[i[0]].Place_Name])

        if len(recommended_place_keys) >= int(place_number.split()[0]):
            break
        
    return recommended_place_keys 


# Create a function to return the coordinates of recommended tourist sites
def makeMarker(place):
    data = data_content_based_filtering[data_content_based_filtering['Place_Name']==' '.join(place)]

    folium.Marker(  # Marker with icon
        location=[float(data['Lat'].values), float(data['Long'].values)], 
        popup=place,
        tooltip=place,
        icon=folium.Icon(color='#43BFF5', icon="info-sign"),
    ).add_to(m) 


# Function to prepare output to be generated with HTML
def makeRecommender(recommendation):
    fmt = ""
    for places in recommendation:
        data = data_content_based_filtering[data_content_based_filtering['Place_Name']==' '.join(places)]

        place_name = ' '.join(places)
        place_category = ' '.join(data['Category_en'].values)
        place_entry_price = str(data['Price'].values)  
        place_rating = str(data['Rating'].values) 
        place_desc = ' '.join(data['Description_en'].values)

        fmt += "<h3><a href='https://www.google.com/search?q=" + str(place_name) + "' target='_blank'>" + str(place_name) + " </a></h3>" + "<p>Category: " + place_category + ". Entry price (Indonesia Rupiah): " + place_entry_price + ". Rating: " + place_rating + "</p>" + "Description:<br><p>" + str(place_desc) + "</p><br><br>"
    return fmt  
    

def main(inputs):
    # Process tourist destination place
    recommendation = recommend_by_content_based_filtering(inputs['input_type'], inputs['input_city'], inputs['input_number']) 
    
    # Process the map markers coordinates
    for places in recommendation:
        makeMarker(places)
    
    # Process the output formatting
    formatter = makeRecommender(recommendation)

    map_html = m._repr_html_()
    return {"recommendation": formatter, "maps": map_html}
