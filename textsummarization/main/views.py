from django.shortcuts import render,redirect
from django.http import HttpResponse
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from django.contrib.auth.models import User
from django.contrib import messages
from .models import userdata
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required





def preprocess_text(text):
    """Preprocess the text: tokenize, remove stopwords, and apply stemming."""
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
    return filtered_words

def sentence_scoring(text, sentences, tfidf_matrix):
    """Score each sentence based on TF-IDF scores and other features."""
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        for word in word_tokenize(sentence.lower()):
            if word in tfidf_matrix.vocabulary_:
                score += tfidf_matrix.idf_[tfidf_matrix.vocabulary_[word]]
        # Additional scoring criteria (optional)
        score += (len(sentence.split()) / len(sentences))  # Give preference to longer sentences
        sentence_scores.append((sentence, score))
    return sentence_scores

def extractive_summary(text, num_sentences=3):
    """Generate an extractive summary from the text."""
    # Tokenize text into sentences
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text  # If text is too short, return it as is

    # Preprocess text for TF-IDF
    filtered_words = preprocess_text(text)
    clean_text = ' '.join(filtered_words)

    # Calculate TF-IDF scores
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([clean_text])

    # Score sentences
    sentence_scores = sentence_scoring(text, sentences, vectorizer)

    # Sort sentences by score
    ranked_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)

    # Select the top sentences for the summary
    summary_sentences = [sentence for sentence, score in ranked_sentences[:num_sentences]]
    summary = ' '.join(summary_sentences)

    return summary
@login_required(login_url="log")
def summary(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        num_sentences = int(request.POST.get('num_sentences', 3))
        if text:
            summarized_text = extractive_summary(text, num_sentences)
            text_block = {
                'text': text,
                'summarized_text': summarized_text
            }
        else:
            text_block = {
                'text': '',
                'summarized_text': ''
            }
    else:
        text_block = {
            'text': '',
            'summarized_text': ''
        }

    return render(request, 'summarize.html', text_block)



def sign(request):
    if request.method=="POST":
        username=request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        password=request.POST.get('password')
        email=request.POST.get('email')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.error(request, "User already exists")
            return render(request, 'sign_in.html')
        
        user=User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,

        )
        user.set_password(password)
        user.save()
        user1=userdata.objects.create(
            email=email
        )
        user1.save()
        messages.success(request,"User successfully added")
    return render(request,"sign_in.html")


def log(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = User.objects.filter(username=username)

        if not user.exists():
            messages.error(request,"User does'nt exist")
            return redirect("sign")
        
        user=authenticate(username=username,password=password)
        if user is None:
            messages.error(request,"Invalid password please try again")
            return redirect("log")
        else:
            login(request,user)
            messages.success(request,"Login successful")
            return redirect("summary")
        
    return render (request,"login.html")

def log_out(request):
    logout(request)
    return redirect("log")

            