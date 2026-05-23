#Libraries
library(dplyr)
library(tidyr)
library(stringr)
library(advertools)
library(arrow)
 
#Defined function
getMentionsR<- function(text_column, fileIn, fileOut) {
  
  #Read fileIn file
  tweets <- read_parquet(fileIn, as_data_frame=TRUE)

  print("[getMentions.R] Rows:")
  print(nrow(tweets))

  if(nrow(tweets)==0) {
    print("[getMentions.R] Passed DF with no rows to R! Returning status 123")
    quit(status=123)
  }

  print("[getMentions.R] Computing ...")

  #Getting mentions
  mentions<-twtr_get_mentions(tweets[[text_column]])
  #Setting in a data frame
  mentions_list<-mentions$top_mentions #TODO: replace with 'mentions' in order to get all mentions?

  if(nrow(mentions_list)==0) {
      print("[getMentions.R] resulting DF is empty! Returning status 123")
      quit(status=123)
  }
  
  #Write into a .CVS  
  write_parquet(mentions_list, fileOut)
  
  print("[getMentions.R] The list of mentions has been created")

}

args = commandArgs(trailingOnly=TRUE)

print("[getMentions.R] getMentions starts")
print("[getMentions.R] text_column")
print(args[1])
print("[getMentions.R] file_in")
print(args[2])
print("[getMentions.R] file_out")
print(args[3])

getMentionsR(args[1], args[2], args[3])