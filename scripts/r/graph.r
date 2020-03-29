
library(lubridate)
library(ggplot2)
library(data.table)

#creo path ai file con directory dinamica
file_path_temp <- "data/history/world/time_series_covid19_"
data_csv <- paste(Sys.Date()-1,".csv",sep="")
death_f <- paste(file_path_temp,"deaths_global_",data_csv,sep="")
confirmed_f <- paste(file_path_temp,"confirmed_global_",data_csv,sep="")
recovered_f <- paste(file_path_temp,"recovered_global_",data_csv,sep="")
path_final_deaths<- file.path(getwd(),death_f)
path_final_confirmed<- file.path(getwd(),confirmed_f)
path_final_recovered<- file.path(getwd(),recovered_f)
world_death <- read.csv(path_final_deaths)
world_confirmed <- read.csv(path_final_confirmed)
world_recovered <- read.csv(path_final_recovered)


#iniio a creare il mio dataframe
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
new_table <- data.frame(datario,countries,provinces,death,confirmed)

################## GRAFICI PER PAESE ############################


#creo il data table
new_table <- setDT(new_table)
names <- unique(new_table$countries)
#c="US"
k<-0

table_final <-c()

for (c in names){
death <- c()
confirmed <- c()
recovered <- c()
areas <- c()
k<-k+1
world <- new_table[countries == c]
f<-0
#i="2020-01-23"
  for (i in unique(world$datario)){
    f<-f+1
    world_new <- world[datario == i]
    death[f] <- sum(world_new[,4])
    confirmed[f] <-  sum(world_new[,5])
    # recovered[f] <- sum(world_new[,6])
    areas[f] <- c
  
  }

  table <- data.frame(areas,death,confirmed)
  table_final <- rbind(table_final,table)
}

dates <- rep(days,length(unique(table_final$areas)))
table_final <- setDT(cbind.data.frame(dates,table_final))

path_temp<-"results/countries_distr"
file_name <- paste("World_",format(today()-1, "%Y-%m-%d"), ".pdf", sep = "")
file_name <- file.path(getwd(), path_temp, file_name)
# apro la connessione
pdf(file_name,height=4,paper='special')
for (i in unique(table_final$areas)){
  final_plot <- table_final[areas == i]
  final <-melt(final_plot,c("dates","areas"))
  
  plot_world <- ggplot(final,aes(dates,value,color=variable,group=variable))+geom_line()+ggtitle(paste("Covid 19",i,sep=" - "))
  
  # asse secondario
  #plot_world <- plot_world + scale_y_continuous("death - recovered", sec.axis = sec_axis(~.*10, name="confirmed"))
  
   print(plot_world)
  
}
dev.off()
  

