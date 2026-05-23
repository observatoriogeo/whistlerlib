#Defined function
cleanText<-function(corpus)
{
  library(tm)
  
  removeURL <- function(x) gsub("http[[:alnum:][:punct:]]*", "",x)
  corpus <- tm_map(corpus, content_transformer(removeURL))
  #Remove Emoticons
  removeEmoticon<-function(x) gsub("<[[:alnum:][:punct:]]*>","",x)
  corpus <- tm_map(corpus, content_transformer(removeEmoticon))
  #Remove Hashtags
  removeHashtag <- function(x) gsub("#[[:alnum:][:punct:]]*","",x)
  corpus <- tm_map(corpus, content_transformer(removeHashtag))
  #Remove RT
  removeRT <- function(x) gsub("RT[a-z,A-Z]*: ","",x)
  corpus <- tm_map(corpus, content_transformer(removeRT))
  #Remove References
  removeRefer <- function(x) gsub("@[a-z,A-Z,0-9]*","",x)
  corpus <- tm_map(corpus, content_transformer(removeRefer))
  #Remove Punctuation
  removePuntuacion <- function(x) gsub("[[:punct:]]", "",x)
  corpus <- tm_map(corpus, content_transformer(removePuntuacion))
  #Remove Bar
  corpus <- tm_map(corpus, removePunctuation) 
  removeBar <- function(x) gsub('[\n?\r]*', '', x)  
  corpus <- tm_map(corpus, content_transformer(removeBar))
  #Minusculas
  corpus <- tm_map(corpus, content_transformer(tolower))
  corpus <- tm_map(corpus, removeNumbers)
  #Stop words
  corpus = tm_map(corpus, removeWords, stopwords("spanish"))
  
  return(corpus)
}



