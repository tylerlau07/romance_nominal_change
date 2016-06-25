# This script will analyze what the endings for each
# Gender/Declension/Case/Number combo is

library(readr)

df = read_delim('rootending.txt', delim = "\t")

df[df == 'mh'] <- 'm'
df[df == 'fh'] <- 'f'

endings <- subset(df, select = c('Suffix', 'Case', 'Gender', 'Declension'))

freq_table <- table(endings)

genders <- c('m', 'f', 'n')
declensions <- seq(1, 5)
cases <- c('nomsg', 'nompl', 'accsg', 'accpl', 'gensg', 'genpl')

for (gender in genders) {
  for (dec in declensions) {
    for (case in cases) {
      pre_table <- freq_table[ , case, gender, dec]
      assign(paste0(gender, dec, case), pre_table[pre_table != 0])
    }
  }
}

n2nompl

df[df$Suffix == "um" & df$Gender == "n" & df$Declension == 2 & df$Case == "nompl", ]
