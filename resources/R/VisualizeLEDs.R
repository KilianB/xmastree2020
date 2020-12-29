library(ggplot2)
library("RColorBrewer")

setwd("~/git/xmastree2020/resources/R")

##Import data
file <- "coords.txt"
coordsRaw = readLines(file)
replaceRegex = "\\[|\\]| "

colNames = c("X","Y","Z")
coordinates = read.csv(textConnection(gsub(pattern = replaceRegex,x = coordsRaw,replacement = "")),sep=",", col.names=colNames)

minX = min(coordinates$X)
maxX = max(coordinates$X)

minZ = min(coordinates$Z)
maxZ = max(coordinates$Z)

midX = (minX + maxX)/2

minY = min(coordinates$Y)

##Create buckets

bins = 7
binWidth = (maxX - minX)/bins

binCoordinates.calc = data.frame(X=numeric(),Y=numeric())
binCoordinates = data.frame(X=numeric(),Y=numeric())

topPoint = data.frame(X=midX,Y=maxZ)

for (i in 0:(bins)) {
  binCoordinates = rbind(binCoordinates,c(minX + binWidth * i,minZ,i))
  binCoordinates = rbind(binCoordinates,c(midX,maxZ,i))
  binCoordinates.calc= rbind(binCoordinates.calc,c(minX + binWidth * i,minZ,i))
}
colnames(binCoordinates) = c("X","Y","Group")
colnames(binCoordinates.calc) = c("X","Y","Group")
##Put each led into the correct bucket

isLeft = function(p1,p2,c){
  # p1 
  # p2 top point
  # c point to check    ## C he are using Z instead of Y
  
  #https://stackoverflow.com/a/3461533/3244464
  return ((((p2["X"] - p1["X"])*(c["Z"] - p1["Y"])) - ((p2["Y"] - p1["Y"])*(c["X"] - p1["X"]))) > 0);
}


resolveBin = function(ledCoordinate){
  for(i in 1:nrow(binCoordinates.calc)){
    ##First 2 lines are combiend into 1 bucket
    ##Last 2 are combined into a bucket
    if(isLeft(binCoordinates.calc[i,],topPoint,ledCoordinate)){
      if(i < 2){
        return(1);
      }else{
        return(i-1);
      }
    }
  }
  print("Not found. assume last")
  return(nrow(binCoordinates.calc)-1)
}


coordinates["bucket"]  <- apply(coordinates,1,resolveBin)

ggplot(coordinates, aes(x=X, y=Z, colour=Y)) + 
  geom_point() + labs(title = "Christmas Tree LED Distribution", y ="Z") +theme_bw()

ggplot(coordinates, aes(x=X, y=Z)) + 
  geom_point(aes(colour=as.factor(bucket))) + 
  geom_point(aes(x=midX, y=maxZ), colour="red") + 
  geom_line(binCoordinates[3:(nrow(binCoordinates)-2),],mapping = aes(x=X,y=Y,group=Group)) + 
  labs(title = "Christmas Tree LED Distribution", y =" Z ", fill="Bins") +theme_bw()
