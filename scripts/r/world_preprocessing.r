
library(lubridate)

world_death <- read.csv("C:\\Users\\aquilinoa\\Desktop\\covid19italia\\publication\\world\\time_series_19-covid-Deaths.csv")
world_confirmed <- read.csv("C:\\Users\\aquilinoa\\Desktop\\covid19italia\\publication\\world\\time_series_19-covid-Confirmed.csv")
world_recovered <- read.csv("C:\\Users\\aquilinoa\\Desktop\\covid19italia\\publication\\world\\time_series_19-covid-Recovered.csv")

province <- world_death[,1]
country <- world_death[,2]
#droppo le prime 4 colonne
world_death[,c(1:4)]<-NULL
world_confirmed[,c(1:4)]<-NULL
world_recovered[,c(1:4)]<-NULL
#prendo le date del file
days <-  colnames(world_death)
days <- gsub("X",0,days)
days <- as.Date(days,format="%m.%d.%y")
#creo le prime 3 colonne della new_table
datario <- sort(rep(days,nrow(world_death)))
countries <- rep(country,interval(min(days),max(days)+1)/days(1))
provinces <- rep(province,interval(min(days),max(days)+1)/days(1))

death<-c()
confirmed <- c()
recovered <- c()

for (i in 1:length(world_death)){
  death[i] <- list(world_death[,i])
  confirmed[i] <- list(world_confirmed[,i])
  recovered[i] <- list(world_recovered[,i])
  }
#creo le colonne con le osservazioni
death <- unlist(death)
confirmed<-unlist(confirmed)
recovered<-unlist(recovered)
#tabella finale
new_table <- data.frame(datario,countries,provinces,death,confirmed,recovered)

