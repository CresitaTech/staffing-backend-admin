import pandas as pd
import numpy as np
import re
import os
import pickle
import PyPDF2
import docx
import textract
import sys

import logging  # Setting up the loggings to monitor gensim

from nltk import WordNetLemmatizer

logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt='%H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)
# uploading the file from the local drive
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.feature_extraction.text import CountVectorizer
import textdistance as td
from sklearn.metrics.pairwise import cosine_similarity
from string import punctuation
import spacy

# loading the english language small model of spacy
en = spacy.load('en_core_web_sm')
sw_spacy = en.Defaults.stop_words
from nltk.corpus import stopwords

sw_nltk = stopwords.words('english')
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


def get_training_data(TRAINING_PATH):
    """
    It's expected that the input csv file has two columns: "text" and "label"
    :return:
    """
    data = pd.read_csv(TRAINING_PATH)
    data['resume_text'] = data['resume_text'].astype(str)
    data = data.drop_duplicates()
    # data['resume_text'] = data['resume_text'].apply(lambda x: clean_doc(x))
    mask = (data['resume_text'].str.len() > 5)  # remove short inputs
    data = data.loc[mask]
    data = data.reset_index()
    logger.info("======================================")
    logger.info(data)

    data = data.fillna(method='ffill')

    return data


def get_csv_data(TRAINING_PATH):
    """
    It's expected that the input csv file has two columns: "text" and "label"
    :return:
    """
    df = pd.read_csv(TRAINING_PATH)
    return df


def match(resume, job_des):
    j = td.jaccard.similarity(resume, job_des)
    s = td.sorensen_dice.similarity(resume, job_des)
    c = td.cosine.similarity(resume, job_des)
    o = td.overlap.normalized_similarity(resume, job_des)
    total = (j + s + c + o) / 4
    # total = (s+o)/2
    return total * 100


def readPdf(fileName):
    fileContent = ""
    try:
        # creating a pdf file object
        pdfFileObj = open(fileName, 'rb')
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        # printing number of pages in pdf file
        print(pdfReader.numPages)
        # creating a page object
        pageObj = pdfReader.getPage(0)
        # rotating each page
        for page in range(pdfReader.numPages):
            # creating rotated page object
            pageObj = pdfReader.getPage(page)
            # pageObj.rotateClockwise(rotation)
            fileContent = fileContent + pageObj.extractText()
        # closing the pdf file object
        pdfFileObj.close()
    except:
        print("Oops! error occurred.")
    return fileContent


def readDocx(fileName):
    docContent = ""
    try:
        doc = docx.Document(fileName)
        all_paras = doc.paragraphs
        len(all_paras)
        for para in all_paras:
            docContent = docContent + para.text
    except:
        print("Oops! error occurred.")
    return docContent


def readDoc(resume):
    text = textract.process(str(resume))
    text = text.decode("utf-8")
    return text


# ========================= Pre process Text Method ==========================

def clean_doc(sentence):
    """
    :param sentence: raw sentence
    :return: cleaned sentence
    """
    # translator = str.maketrans('', '', string.punctuation)
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', str(sentence))
    # cleaned = " ".join([i for i in cleaned.lower().split()]).encode('UTF-8', 'ignore').decode('ascii', 'ignore')
    cleaned = ''.join([i for i in cleaned if not i.isdigit()])
    # cleaned = str(cleaned).translate(translator)

    return str(cleaned)


def print_text(sample, clean):
    print(f"Before: {sample}")
    print(f"After: {clean}")


def preprocess_text(text):
    text = str(text).lower()  # Lowercase text
    text = re.sub(f"[{re.escape(punctuation)}]", "", str(text))  # Remove punctuation
    text = " ".join(text.split())  # Remove extra spaces, tabs, and new lines
    text = re.sub(r'[^\x00-\x7F]+', ' ', str(text))
    text = text.strip('\t')
    text = text.rstrip("\n\r")
    text = text.replace('\n', ' ').replace('\r', '')

    return text


# Removes Punctuations
def remove_punctuations(data):
    punct_tag = re.compile(r'[^\w\s]')
    data = punct_tag.sub(r'', data)
    return data


# Removes HTML syntaxes
def remove_html(data):
    html_tag = re.compile(r'<.*?>')
    data = html_tag.sub(r'', data)
    return data


# Removes URL data
def remove_url(data):
    url_clean = re.compile(r"https://\S+|www\.\S+")
    data = url_clean.sub(r'', data)
    return data


# Removes Emojis
def remove_emoji(data):
    emoji_clean = re.compile("["
                             u"\U0001F600-\U0001F64F"  # emoticons
                             u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                             u"\U0001F680-\U0001F6FF"  # transport & map symbols
                             u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                             u"\U00002702-\U000027B0"
                             u"\U000024C2-\U0001F251"
                             "]+", flags=re.UNICODE)
    data = emoji_clean.sub(r'', data)
    url_clean = re.compile(r"https://\S+|www\.\S+")
    data = url_clean.sub(r'', data)
    return data


def remove_hyperlinks(text):
    text = re.sub(r"https?://\S+", "", text)
    return text


def remove_cases(text):
    text = text.casefold()
    return text


def remove_achor_tag(text):
    text = re.sub(r"<a[^>]*>(.*?)</a>", r"\1", text)
    return text


def remove_extra_spaces(text):
    text = " ".join(text.split())
    return text


def remove_numbers(text):
    text = re.sub(r"\b[0-9]+\b\s*", "", text)
    return text


def remove_digits(text):
    text = " ".join([w for w in text.split() if not w.isdigit()])  # Side effect: removes extra spaces
    return text


def remove_non_alphabetic(text):
    text = " ".join([w for w in text.split() if w.isalpha()])  # Side effect: removes extra spaces
    return text


def remove_all_special(text):
    text = re.sub(r"[^A-Za-z0-9\s]+", "", text)
    return text


def remove_short_tokens(text):
    tokens = text.split()
    text = [t for t in tokens if len(t) > 2]
    text = " ".join(text)
    return text


def remove_newline_tag(text):
    text = text.lower()  # Lowercase text
    # text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = text.strip('\t')
    text = text.rstrip("\n\r")
    text = text.replace('\n', ' ').replace('\r', '')
    return text


def remove_stopwords(text):
    words = [word for word in text.split() if word.lower() not in sw_nltk]
    words = " ".join(words)
    words = [word for word in words.split() if word.lower() not in sw_spacy]
    words = " ".join(words)
    words = remove_stopwords(words)
    words = [word for word in words.split() if word.lower() not in ENGLISH_STOP_WORDS]
    words = " ".join(words)
    return words


def remove_repeated_characters(text):
    text = re.sub(r'(.)\1{3,}', r'\1', text)
    return text


def remove_none_value(text):
    text = text.replace('None', '')
    return text


# Lemmatize the corpus
def lemma_traincorpus(data):
    lemmatizer = WordNetLemmatizer()
    tokens = data.split()
    out_data = ""
    for words in tokens:
        out_data = " ".join(lemmatizer.lemmatize(words))
    return out_data


def tfidf(data):
    tfidfv = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), lowercase=True, max_features=150000)
    fit_data_tfidf = tfidfv.fit_transform(data)
    return fit_data_tfidf


def extractContent(resume_path):
    logger.info("resume_path: " + str(resume_path))
    fileName = r'/home/admin/projectDir/staffingapp/media/' + str(resume_path)
    logger.info("fileName: " + fileName)
    ext = os.path.splitext(fileName)[-1].lower()
    logger.info(ext)
    content = "NA"
    text = None
    if ext == '.pdf':
        content = readPdf(fileName)
        # dataList.append(content)
    elif ext == '.docx':
        content = readDocx(fileName)
        # dataList.append([fileName, content])
        # dataList.append(content)
    elif ext == '.doc':
        content = readDoc(fileName)
        # dataList.append([fileName, content])
        # dataList.append(content)
    else:
        print('File format not matched')
        # dataList.append([fileName, content])
        # dataList.append(content)

    logger.info('File number ' + str(fileName) + ' Completed')

    try:
        # text = await preprocess_text(text)
        text = preprocess_text(content)
        text = clean_doc(text)
        # print("clean_doc completed")
        text = remove_punctuations(text)
        # print("remove_punctuations completed")
        text = remove_html(text)
        # print("remove_html completed")
        text = remove_url(text)
        # print("remove_url completed")
        text = remove_all_special(text)
        # print("remove_newline completed")
        # text = await remove_stopwords(text)
        # print("remove_emoji completed")
        text = remove_hyperlinks(text)
        text = remove_cases(text)
        text = remove_achor_tag(text)
        text = remove_extra_spaces(text)
        text = remove_numbers(text)
        text = remove_digits(text)
        text = remove_non_alphabetic(text)
        # text = lemma_traincorpus(text)
        # text = await remove_short_tokens(text)
    except:
        print("Oops! Error occurred. File not formated.")

    logger.info("Extract content: " + str(text))

    return text