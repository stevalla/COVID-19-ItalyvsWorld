
library(lubridate)

world_death <- read.csv("C:\\Users\\aquilinoa\\Desktop\\COVID-19-ItalyvsWorld\\data\\world\\history\\time_series_19-covid-Deaths.csv")
world_confirmed <- read.csv("C:\\Users\\aquilinoa\\Desktop\\COVID-19-ItalyvsWorld\\data\\world\\history\\time_series_19-covid-Confirmed.csv")
world_recovered <- read.csv("C:\\Users\\aquilinoa\\Desktop\\COVID-19-ItalyvsWorld\\data\\world\\history\\time_series_19-covid-Recovered.csv")

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



library(data.table)
library(ggplot2)
#creo il data table
new_table <- setDT(new_table)
italy <- new_table[countries == "Italy"]
#scalo i confirmed per 10
italy <- cbind(italy[,1],italy[,4],italy[,5]/10,italy[,6])#preparo il dataset per ggplot
italy <-melt(italy,"datario")
#plot con asse secondario *
setwd("C:\\Users\\aquilinoa\\Desktop\\COVID-19-ItalyvsWorld\\results\\graph")
file_name <- paste("Italy_",format(today()-1, "%Y-%m-%d"), ".pdf", sep = "")
pdf(file_name,height=4,paper='special')
plot_italy<-ggplot(italy,aes(datario,value,color=variable,group=variable))+geom_line()+ggtitle("Covid 19 Italy")
plot_italy <- plot_italy + scale_y_continuous("death - recovered", sec.axis = sec_axis(~.*10, name="confirmed"))
#salvo il grafico in un pdfn
plot_italy
dev.off()


