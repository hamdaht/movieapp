import streamlit as st
import requests
import random

API_KEY = "8fb14546edbb0b572d1cf09aa07c8b60"

def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={"8fb14546edbb0b572d1cf09aa07c8b60"}&language=en-US"
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Raw JSON:", response.json())

    genres = response.json()["genres"]
    genre_dict = {g["name"].lower(): g["id"] for g in genres}

    return genre_dict

def get_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    videos = response.json().get("results", [])

    # Prefer YouTube trailers
    for video in videos:
        if video.get("type") == "Trailer" and video.get("site") == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"

    # Fallback: return the first available YouTube video (teaser, clip, etc.)
    for video in videos:
        if video.get("site") == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"

    return None


## UI -------- ##

st.title("Movie Night with Hamdah")
genre_dict = get_genres()
genre_name = st.selectbox("What genre are you in the mood for?", list(genre_dict.keys()))
runtime = st.slider("How many minutes do you want the movie to be MAX?", 30, 300, 120)
year = st.slider("After what year should the movie have be released by. For example, put 2015 if you don't want any movies older than 2015", 1950, 2025, 2015)
min_rating = st.slider("Minimum rating (0–10):", 0.0, 10.0, 7.0, step=0.1)



if st.button("🎲 Movie Time with Hamdah!"):
    genre_id = genre_dict[genre_name]

    # First fetch just to get total pages
    base_url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US&sort_by=popularity.desc&with_genres={genre_id}&with_runtime.lte={runtime}&primary_release_date.gte={year}-01-01"
    initial_response = requests.get(base_url + "&page=1").json()
    total_pages = min(initial_response.get("total_pages", 1), 100)  # TMDB max is 500, we’ll use 10 for safety

    # Pick a random page
    random_page = random.randint(1, total_pages)
    response = requests.get(base_url + f"&page={random_page}")
    movies = response.json().get("results", [])
    movies = [m for m in movies if m.get("vote_average", 0) >= min_rating]



    if not movies:
            st.error("😢 No movies found. Try adjusting your filters.")
    else:
        movie = random.choice(movies)
        st.success(f"🎉 We recommend: {movie['title']}")
        st.write(f"⭐ Rating: {movie['vote_average']}")
        st.write(f"📝 {movie['overview']}")
        trailer = get_trailer(movie["id"])
        if trailer:
            st.video(trailer)
        else:
            st.info("No trailer found.")
