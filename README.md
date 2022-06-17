# Raw Light Novel Translator

![Commit activity](https://img.shields.io/github/commit-activity/m/Snowad14/Raw-Novel-Translation)
![Lines of code](https://img.shields.io/tokei/lines/github/Snowad14/Raw-Novel-Translation?label=lines%20of%20code)
![Contributors](https://img.shields.io/github/contributors/Snowad14/Raw-Novel-Translation)

Some light novels will never be translated, therefore this project is born.
This project aims to turn Light Novel raws images into translated text


## Intallation 🦄

```bash
# First, you need to have Python(>=3.8) installed on your system.
$ python --version
Python 3.8.13

# Clone this repo
$ git clone https://github.com/Snowad14/Raw-Novel-Translation.git

# Install the dependencies
$ pip install -r requirements.txt

```

Then, download `ocr.ckpt`, `ocr-ctc.ckpt`, `detect.ckpt`, `comictextdetector.pt` and `comictextdetector.pt.onnx`
from <https://github.com/zyddnys/manga-image-translator/releases/>, put them in the root directory of this repo.

<!> If you use paid translators put the api key in the file `translators/keys.py`

## Usage 👍

```bash

$ python main.py --use-cuda --translator=google --target-lang=ENG --image <path_to_image_folder>

```

## TODO

| Feature/Bugs | Finished |
| ------ | ------ |
| Take the pictures in good order |  [✓]  |
| Well integrated sugoi Translator |  [❌]  |

## Credit 📋

```
Fork of https://github.com/zyddnys/manga-image-translator (don't hesitate to make a small donation)
```

