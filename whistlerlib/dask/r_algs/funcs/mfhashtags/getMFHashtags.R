#Libraries
library(tm) 
library(SnowballC)
library(twitteR)
library(arrow)

#Defined function
getMDHashtags<- function(text_column, fileIn, fileOut) {
  
      
  #Set current directory
  setwd("./")
  #Read fileIn file
  #tweets <- read.csv(fileIn) 
  tweets <- read_parquet(fileIn, as_data_frame=TRUE)

  print("[getMFHashtags.R] Rows:")
  print(nrow(tweets))

  if(nrow(tweets)==0) {
    print("[getMFHashtags.R] Passed DF with no rows to R! Returning status 123")
    quit(status=123)
  }

  print("[getMFHashtags.R] Computing ...")

  #Set in a vector
  corpus = Corpus(VectorSource(tweets[[text_column]]))
  #Get data
  vec1 = tweets[[text_column]]
  
  
  #Extract the patterns
  extract.hashes = function(vec){
    
    hash.pattern = "#[[:alpha:]]+"
    have.hash = grep(x = vec, pattern = hash.pattern)
    hash.matches = gregexpr(pattern = hash.pattern,
                            text = vec[have.hash])
    extracted.hash = regmatches(x = vec[have.hash], m = hash.matches)
    df = data.frame(table(tolower(unlist(extracted.hash))))

    if(nrow(df)==0) {
      print("[getMFHashtags.R] extract.hashes DF is empty! Returning status 123")
      quit(status=123)
    }

    colnames(df) = c("tag","freq")
    df = df[order(df$freq,decreasing = TRUE),]
    return(df)
  }
    
  dat = extract.hashes(vec1)
 
  #Write into a .CVS
  #hashtags <- write.csv(dat,fileOut)
  write_parquet(dat, fileOut)
  
  print("[getMFHashtags.R] The list of hashtags has been created")

}

args = commandArgs(trailingOnly=TRUE)

print("[getMFHashtags.R] getMFHashtags starts")
print("[getMFHashtags.R] text_column")
print(args[1])
print("[getMFHashtags.R] file_in")
print(args[2])
print("[getMFHashtags.R] file_out")
print(args[3])

getMDHashtags(args[1], args[2], args[3])