import streamlit as st
from PIL import Image
from glob import glob
from io import BytesIO
from link_drive import upload_file_link
from concurrent.futures import ThreadPoolExecutor
# from stqdm import stqdm
import json
import requests
st.set_page_config(layout="wide",initial_sidebar_state='collapsed')

# Frontend
if 'title' not in st.session_state:
    title = '<h1 style="font-size: 42px;">Drills library</h1>'
    st.session_state['title'] = title

st.markdown(st.session_state['title'], unsafe_allow_html=True)

# Function to load image from Drive without resizing
def load_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

# Function to load images asynchronously
def load_images_async(urls):
    images = []
    with ThreadPoolExecutor() as executor:
        # Submit each URL for downloading and loading
        futures = [executor.submit(load_image, url) for url in urls]
        # Get the results
        for future in futures:
            images.append(future.result())
    return images

# upload links file
with st.spinner('Update files...'):
    dct_files = json.load(open('./drive_links.json'))
    if 'fold_names' not in st.session_state:
        folds = dct_files.keys()
        st.session_state['fold_names'] = folds
    
        for fold in folds:
            st.session_state[fold] = {}
            urls = []
            for drill in dct_files[fold]:
                try:
                    img_id = dct_files[fold][drill]['image']
                    url_image = f"https://drive.google.com/uc?export=view&id={img_id}"
                    urls.append(url_image)
                    st.session_state[fold][drill] = {}
                    st.session_state[fold][drill]['url_image'] = url_image
                except:
                    pass
                
                try:
                    video_id = dct_files[fold][drill]['video']
                    url_video = f"https://drive.google.com/file/d/{video_id}/view?usp=drive_link"
                    st.session_state[fold][drill]['url_video'] = url_video
                except:
                    pass
            
            # Load images asynchronously
            images = load_images_async(urls)
            for drill, image in zip(dct_files[fold], images):
                st.session_state[fold][drill]['loaded_image'] = image
                    
st.success('Update files...Done!')


# # settings sidebar
# with st.sidebar:
#     st.markdown('SETTING')
#     if st.button('Upload google drive links'):
#         upload_file_link()



option = st.selectbox('Seleziona una categoria',[' '] + list(st.session_state['fold_names']))
if option != ' ':
    try:
        lst_drill = list(st.session_state[option].keys())
        
        c1,c2,c3,c4,c5 = st.columns(5)
        n_rows = int(len(st.session_state[option])/5)+1
        cols_order = [c1,c2,c3,c4,c5]*n_rows
        
        lst_zip = []
        startN = 0
        for row in range(n_rows):
            c1,c2,c3,c4,c5 = st.columns(5)
            values = dict( ((key, st.session_state[option][key]) for key in lst_drill[startN:startN+5]) )
            lst_zip.append([values,[c1,c2,c3,c4,c5]])
            startN += 5
    
        for vals,cols in lst_zip:
            with st.container():
                for i,col in zip(vals,cols): 
                    with col:
                        st.divider()
                        st.markdown(i)
                        try:
                            st.image(vals[i]['loaded_image'], use_column_width=True)
                        except:
                            st.write('NO IMAGE')
                        try:
                            st.link_button("Go to video", vals[i]['url_video'])
                        except:
                            st.write('NO VIDEO')
    except:
        pass