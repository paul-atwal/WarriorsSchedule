from youtubesearchpython import VideosSearch

try:
    query = "Golden State Warriors vs Miami Heat 2025-11-19 highlights"
    print(f"Searching for: {query}")
    
    videosSearch = VideosSearch(query, limit = 1)
    result = videosSearch.result()
    
    if result['result']:
        first_video = result['result'][0]
        print(f"Found video: {first_video['title']}")
        print(f"Link: {first_video['link']}")
    else:
        print("No results found.")

except Exception as e:
    print(f"Error: {e}")
