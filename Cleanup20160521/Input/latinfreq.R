df <- read.delim(file = "latinfrequency.txt", sep = ";")

df$Prose <- as.numeric(df$Prose)
df$Poetry <- as.numeric(df$Poetry)
df$Total <- as.numeric(df$Total)

byTotal <- df[order(df$Total, decreasing = TRUE), ]
byProse <- df[order(df$Prose, decreasing = TRUE), ]
byPoetry <- df[order(df$Poetry, decreasing = TRUE), ]

View(byProse)
View(byPoetry)
View(byTotal)
