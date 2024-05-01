library(tm)
library(RWeka)
library(reshape2)
library(dplyr)
library(tidyr)
library(arrow)

getNgrams<- function(fileIn, csvOutput, N, text_column){
  
  print("[getNgrams.R] R function starts!")  

  tweets <- read_parquet(fileIn, as_data_frame=TRUE)

  nrows = nrow(tweets)
  print('[getNgrams.R] Rows: ')
  print(nrows)
  
  if(nrows==0) {
    print("[getNgrams.R] Passed DF with no rows to R! Returning status 123")
    quit(status=123)
  }    
  print("[getNgrams.R] Computing ...")
  
  #Check duplicate 
  #tweets <- tweets[!duplicated(tweets), ] #TODO: double check with Angelina if it is safe to remove this line
  
  #Generate corpus  
  corpus = Corpus(VectorSource(tweets[[text_column]]))
  
  #Load service  
  source(paste(Sys.getenv("WHISTLERLIB_R_SCRIPTS_PATH"), "/ngrams/cleanText.R", sep=""))
  
  #Get clean corpus
  corpus<-cleanText(corpus)
  
  #Delimiters
  tokenDel <- " \\t\\r\\n.!?,;\"()"
  
  #N gram generator
  N_Tokens <- NGramTokenizer(corpus, Weka_control(min=N,max=N, delimiters = tokenDel))
  
  #Create a table
  Nword <- data.frame(table(N_Tokens))
  
  #Order the N-grams
  #nGramsL <- Nword[order(Nword$Freq,decreasing=TRUE),] #TODO: ask Angelina if it is safe to remove this line

  # debug
  #print("DEBUG Nword = ")
  #print(Nword)

  #print("DEBUG")
  #print(Nword[Nword$N_Tokens == "list language =",])
  
  if(nrow(Nword)==0) {
    print("[getNgrams.R] Generated a DF with no rows! Returning status 123")
    quit(status=123)
  } else {
    write_parquet(Nword, csvOutput)
  }

  print("[getNgrams.R] Done.")
  return()
    
}

args = commandArgs(trailingOnly=TRUE)

print("[getNgrams.R] getNgrams starts")
print("[getNgrams.R] fileIn")
print(args[1])
print("[getNgrams.R] csvOutput")
print(args[2])
print("[getNgrams.R] N")
print(args[3])
print("[getNgrams.R] text_column")
print(args[4])

getNgrams(args[1], args[2], strtoi(args[3]), args[4])