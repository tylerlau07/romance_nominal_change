# This script will analyze what the endings for each
# Gender/Declension/Case/Number combo is

library(readr)

df = read_delim('rootending.txt', delim = "\t")

df[df == 'mh'] <- 'm'
df[df == 'fh'] <- 'f'
df[df == 'mh, fh'] <- 'm'
df[df == 'm, f'] <- 'm'

endings <- subset(df, select = c('Suffix', 'Case', 'Gender', 'Declension'))

freq_table <- table(endings)

genders <- c('m', 'f', 'n')
declensions <- seq(1, 5)
cases <- c('nomsg', 'nompl', 'accsg', 'accpl', 'gensg', 'genpl', 
           'datsg', 'datpl', 'ablsg', 'ablpl', 'vocsg', 'vocpl')

for (gender in genders) {
  for (dec in declensions) {
    for (case in cases) {
      pre_table <- freq_table[ , case, gender, dec]
      assign(paste0(gender, dec, case), pre_table[pre_table != 0])
    }
  }
}

m4nomsg

df[df$Suffix == "ēs" & df$Gender == "m" & df$Declension == 3 & df$Case == "nomsg", ]

table(df$Gender)
