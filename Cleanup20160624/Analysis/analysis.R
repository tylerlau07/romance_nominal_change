# This program analyzes the output of program
file <- '../Main Code 7/V_NotSonCont/stats_Epochs3_Gens10_TokFreqT_Trial2.txt'

df <- read.delim(file)

df[df == 'mh'] <- 'm'
df[df == 'fh'] <- 'f'
df[df == 'mh, fh'] <- 'm'
df[df == 'm, f'] <- 'm'

get_endings <- function(df) {
  endings <- subset(df, select = c('X10', 'Case', 'Gender', 'Declension'))
  freq_table = table(endings)
  
  genders <- c('m', 'f', 'n')
  declensions <- seq(1, 5)
  cases <- c('Nom.Sg', 'Nom.Pl', 'Acc.Sg', 'Acc.Pl', 'Gen.Sg', 
             'Gen.Pl', 'Dat.Sg', 'Dat.Pl', 'Abl.Sg', 'Abl.Pl')
  
  for (gender in genders) {
    for (dec in declensions) {
      for (case in cases) {
        pre_table <- freq_table[ , case, gender, dec]
        print(paste0(gender, dec, case), pre_table[pre_table != 0])
        print(assign(paste0(gender, dec, case), pre_table[pre_table != 0]))

      }
    }
  }
}

get_endings(df)

# df[df$Gender == "f" & df$Declension == 1 & df$Case == "Nom.Sg", ]
