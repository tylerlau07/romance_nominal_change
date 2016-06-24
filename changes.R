# This program will look at which specific words changed to what classes

library(readr)
library(plyr)
library(ggplot2)
library(reshape2)
library(gtools)

### Read stats files ###
files = list.files(pattern = '\\.csv')

# We want to make a data frame showing what each word became, start with counts
df_wordcount <- data.frame()

# Add counts for each word
file_originfo <- read_csv(files[1])

# Original
for (i in 1:nrow(file_originfo)) {
  word <- file_originfo$`Declined Noun`[i]
  df_wordcount[word, 'Gender'] <- unlist(strsplit(file_originfo$`0`[i], ' '))[1]
  df_wordcount[word, 'Declension'] <- unlist(strsplit(file_originfo$`0`[i], ' '))[2]
  df_wordcount[word, 'Case'] <- unlist(strsplit(file_originfo$`0`[i], ' '))[3]
  df_wordcount[word, 'Number'] <- unlist(strsplit(file_originfo$`0`[i], ' '))[4]
}

# Now we want to go through files and add 1 to each change in declension and gender that takes place
for (file in files) {
  read <- read_csv(file)
  for (row in 1:nrow(read)) {
    word <- read$`Declined Noun`[row]
    
    # Generation 15 info (Gen, Dec, Case, Num)
    final_info <- unlist(strsplit(read[row, ncol(read)], ' '))
    gen <- final_info[1]
    dec <- final_info[2]
    case <- final_info[3]
    num <- final_info[4]
    
    # Assign
    df_wordcount[word, gen] <- ifelse(invalid(df_wordcount[word, gen]), 1, df_wordcount[word, gen] + 1)
    df_wordcount[word, dec] <- ifelse(invalid(df_wordcount[word, dec]), 1, df_wordcount[word, dec] + 1)
    df_wordcount[word, paste(case, num, sep = ".")] <- ifelse(invalid(df_wordcount[word, paste(case, num, sep = ".")]), 1, df_wordcount[word, paste(case, num, sep = ".")] + 1)
 }
}

df_wordpercent <- cbind(df_wordcount[ , 1:4], df_wordcount[5:ncol(df_wordcount)]/50*100)
df_wordpercent[is.na(df_wordpercent)] <- 0

### Now we want to see what happened

# Declension IV nouns: basically all went to M or rarely N
IV <- df_wordpercent[df_wordpercent$Declension == "IV", ]

# Declension V nouns: goes to F only ~20% of the time, M otherwise
V <- df_wordpercent[df_wordpercent$Declension == "V", ]

# Feminine I nouns that went to F less than 90% of the time
fI <- df_wordpercent[df_wordpercent$Gender == "f" & df_wordpercent$Declension == "I" & df_wordpercent$f < 90, ]

# Masculine II nouns that went to F more than 10% of the time
mII <- df_wordpercent[df_wordpercent$Gender == "m" & df_wordpercent$Declension == "II" & df_wordpercent$f > 10, ]

# Neuter II nouns that went to F more than 10% of the time
nIIf <- df_wordpercent[df_wordpercent$Gender == "n" & df_wordpercent$Declension == "II" & df_wordpercent$f > 10, ]

# Neuter II nouns: 
nII <- df_wordpercent[df_wordpercent$Gender == "n" & df_wordpercent$Declension == "II", ]

# Masculine III nouns: 
mIII <- df_wordpercent[df_wordpercent$Gender == "m" & df_wordpercent$Declension == "III", ]

# Neuter III nouns: 
nIII <- df_wordpercent[df_wordpercent$Gender == "n" & df_wordpercent$Declension == "III", ]

# Feminine III nouns:
fIII <- df_wordpercent[df_wordpercent$Gender == "f" & df_wordpercent$Declension == "III", ]

View(fIII)
