import re
import os
import time
import random
import zipfile
import requests
from flask import Flask
from flask import request, send_file


app = Flask(__name__)


@app.route('/')
def my_form():
    return '''
<html lang="en">
<body>
    <h1>Enter google font url</h1>
    <h2>Give it a few seconds as we download and create a zip of these fonts</h2>
    <form action="." method="POST">
        <input type="text" name="url">
        <input type="submit" name="my-form" value="Send">
    </form>
</body>
</html>
'''


@app.route('/', methods=['POST'])
def my_form_post():

    url = request.form['url']
    zip_file = get_fonts(url)
    new_file_name = "Google_fonts-" + str(int(time.time())) + ".zip"
    return send_file(zip_file,
                     attachment_filename=new_file_name,
                     as_attachment=True)


def zipdir(path, ziph):
    # ziph is zipfile handle
    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_name = os.path.join(root, file)
            ziph.write(file_name)
    # Go back to script root
    os.chdir('../..')


def get_fonts(url):
    global pattern, header

    dl_session = '%030x' % random.randrange(16**30)
    base_dir = os.path.join("downloads", dl_session)

    make_path = os.path.join(base_dir, "fonts")
    if not os.path.exists(make_path):
        os.makedirs(make_path)

    # Get the generated css via google css api
    r = requests.get(url, headers=header)

    # Where we store the modified css
    css = r.text

    data = r.text.split("\n")
    font = {}
    for line in data:
        if line.startswith('}'):  # We found the end of the block
            # Create filename to save font as
            file_ext = font['url'].split('.')[-1]
            filename = font['comment'] + '_' + \
                       font['font_family'] + '_' + \
                       font['font_style'] + '_' + \
                       font['font_weight'] + '.' + \
                       file_ext
            save_path = os.path.join(base_dir, "fonts", filename)

            # Download font locally
            r_file = requests.get(font['url'], headers=header)
            with open(save_path, "wb") as code:
                code.write(r_file.content)

            # Replace url in css file with local file
            css = css.replace(font['url'], "./fonts/" + filename)

            # Clear values
            font = {}
        else:
            # Check each pattern to get the correct css value for that line
            for key in pattern:
                g = pattern[key].match(line)
                if g:
                    font[key] = g.group(1)
                    # Found it, now move to the next line
                    break

    # Save the modified css to a file
    save_file_css = os.path.join(base_dir, 'local_fonts.css')
    with open(save_file_css, 'w') as f:
        f.write(css)

    # Create a zip file to return
    zip_file = os.path.join("downloads", dl_session + '.zip')
    zipf = zipfile.ZipFile(zip_file, 'w')
    zipdir(base_dir, zipf)
    zipf.close()

    # TODO: Remove old dir

    return zip_file


if __name__ == '__main__':
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

    pattern = {}
    pattern['comment'] = re.compile('\/\*\s(.*)\s\*\/')
    pattern['url'] = re.compile('.*url\((.+)\)\s')
    pattern['font_family'] = re.compile('\s*font-family:\s\'(.*)\';')
    pattern['font_style'] = re.compile('\s*font-style:\s(.*);')
    pattern['font_weight'] = re.compile('\s*font-weight:\s(.*);')

    app.run(host='0.0.0.0', port=7001, debug=False)
