getSentiments<- function(text_column, language, method, fileIn, fileOut) {

#Libraries

library(tm)
library(NLP)
library(syuzhet)
library(arrow)

#Set current directory
setwd("./")
tweets <- read_parquet(fileIn, as_data_frame=TRUE)

if(nrow(tweets)==0) {
    print("[getSentiments.R] Passed DF with no rows to R! Returning empty response DF")
    quit(status=123)    
 }

print("[getSentiments.R] Computing ...")

#Generate corpus
corpus <- Corpus(VectorSource(tweets[[text_column]]))
#Load service
source(paste(Sys.getenv("WHISTLERLIB_R_SCRIPTS_PATH"), "/ngrams/cleanText.R", sep=""))
#Get clean corpus
corpus<-cleanText(corpus)

####Get vector of 
df <- data.frame(text=sapply(corpus, identity))
#Getting vectors
nrc_vector <- get_sentiment(as.character(df[[text_column]]), method=method, lang = language)
#Emotions
emotions <- get_nrc_sentiment(as.character(df[[text_column]]), language = language)
#Setting in a data frame
df <- data.frame(text=sapply(corpus, identity), 
                 polarity = nrc_vector,                 
                 emotions = emotions
                 )
#Writte
write_parquet(df,fileOut)

print("[getSentiments.R] Done.")
return()

} 

args = commandArgs(trailingOnly=TRUE)

print("[getSentiments.R] getSentiments starts")
print("[getSentiments.R] text_column")
print(args[1])
print("[getSentiments.R] language")
print(args[2])
print("[getSentiments.R] method")
print(args[3])
print("[getSentiments.R] file_in")
print(args[4])
print("[getSentiments.R] file_out")
print(args[5])

getSentiments(args[1], args[2], args[3], args[4], args[5])