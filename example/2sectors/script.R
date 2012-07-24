x11();
plot(buy_log_household$consumption_good|buy_log_household$id, type='l',col='red')
plot(household$HH|household$id, type='l', col='green')
x11()
plot(production_log_firm$intermediate_good[which(production_log_firm$id == 0)], type='l', col='blue', ylim=c(0,2.5))
lines(production_log_firm$consumption_good[which(production_log_firm$id == 1)], col='red')

sam(0)
sam(10)
