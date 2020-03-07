world_death <- read.csv("C:\\Users\\aquilinoa\\Desktop\\covid19italia\\publication\\world\\time_series_19-covid-Deaths.csv")
world_confirmed <- read.csv("C:\\Users\\aquilinoa\\Desktop\\covid19italia\\publication\\world\\time_series_19-covid-Confirmed.csv",header=FALSE,skip=1)
world_recovered <- read.csv("C:\\Users\\aquilinoa\\Desktop\\covid19italia\\publication\\world\\time_series_19-covid-Recovered.csv")
library(lubridate)
province <- world_death[,1]
country <- world_death[,2]
datario <- sort(rep(seq(from=as.Date("2020-01-22"),to=as.Date(today()-1),by=1),nrow(world_death)))
countries <- rep(country,interval("2020-01-22",today())/days(1))
provinces <- rep(province,interval("2020-01-22",today())/days(1))
world_death[,c(1:4)]<-NULL
world_confirmed[,c(1:4)]<-NULL
world_recovered[,c(1:4)]<-NULL
death<-c()
confirmed <- c()
recovered <- c()
for (i in 1:length(world_death)){
  death[i] <- list(world_death[,i])
  confirmed[i] <- list(world_confirmed[,i])
  recovered[i] <- list(world_recovered[,i])
}
death <- unlist(death)
confirmed<-unlist(confirmed)
recovered<-unlist(recovered)
new_table <- data.frame(datario,countries,provinces,death,confirmed,recovered)


