##################################################################################################
##
##Ver. 1.0
##
## getNgrams -> This function get the  N-Grams from a text data set from the
##              fileIn.csv file, and generate a fileOut.csv to writte in it the N hashtags. 
##
##################################################################################################
## Parameters ##
## fileIn: Name of the file with the data to be extracted and analyzed.
## myWordcloud: Name of the File with the  wordcloud of the N mos frequents Ngrams.
## N:      Number of the most frequent hashtags
##################################################################################################
## Specifications ##
## R version 3.6.3 (2020-02-29)
## platform       x86_64-w64-mingw32          
## arch           x86_64                      
## os             mingw32                     
## system         x86_64, mingw32
##date            2020-03-25 
#################################################################################################
## Libraries version
## ggplot2_3.3.0
## SnowballC_0.7.0
## twitteR_1.1.9
################################################################################################

library(wordcloud)
library(wordcloud2)
library(htmlwidgets) # agr: this library was missing
library(withr) # for the with_dir function
library(arrow)
 
getWordCloud <- function(fileIn, htmlFolder, htmlFilen){

  nGramsL <- read_parquet(fileIn, as_data_frame=TRUE)

  if(nrow(nGramsL)==0) {
    print("[getWordCloud.R] Passed DF with no rows to R! Returning status 123")
    quit(status=123)
  }    
 
  myWordcloud=wordcloud2(nGramsL, color = "random-dark", backgroundColor = "white")

  with_dir(htmlFolder, saveWidget(myWordcloud, htmlFilen, selfcontained = F))

  print("[getWordCloud.R.getWordCloud] Done.")

  return()

}

args = commandArgs(trailingOnly=TRUE)

print("[getWordCloud.R] getWordCloud starts")
print("[getWordCloud.R] fileIn")
print(args[1])
print("[getWordCloud.R] htmlFolder")
print(args[2])
print("[getWordCloud.R] htmlFilen")
print(args[3])

getWordCloud(args[1], args[2], args[3])